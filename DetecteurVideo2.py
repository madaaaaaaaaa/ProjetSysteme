from re import T
import traceback
import cv2
import random
import munkres
import math
import redis
import json
from threading import Thread
import time
import numpy as np
import requests
import imutils
import datetime as datetime

def calculer_distance(point1, point2):
    return math.sqrt((point1["x"] - point2["x"])**2 + (point1["y"] - point2["y"])**2)

class DetecteurVideo():
    def __init__(self, r, adr_IPv4_video):
        self.r  = r
        self.adr_IPv4_video = adr_IPv4_video
        self.positions_radars = None

    def lancer_detection(self):
        self.action_enregistrement = None
        nbr_frames = 0
        fps = 30
        m = munkres.Munkres()
        self.aire_min = 200
        self.rectangle_max = None
        self.rectangle_min = None
        cap = None
        marge = 10
        fgbg = cv2.createBackgroundSubtractorMOG2(varThreshold=100)
        #kernel = np.ones((5,5), np.float32)/25
        #capture = cv2.VideoCapture("http://{}:8080/video".format(self.adr_IPv4_video))
        capture = cv2.VideoCapture("pietons.webm")
        while True : 
            ticks = cv2.getTickCount()
            ret, frame = capture.read()

            if not ret:
                capture = cv2.VideoCapture("pietons.webm")
                ret, frame = capture.read()

            fgmask = fgbg.apply(frame)
            #fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)            

            #FILTRES
            if self.rectangle_max :
                cv2.rectangle(frame, (self.rectangle_max["x1"], self.rectangle_max["y1"]), 
                    (self.rectangle_max["x2"], self.rectangle_max["y2"]), 
                    color = (0, 140, 255), thickness = 1, lineType = cv2.LINE_AA)
                cv2.putText(img = frame, text = "max", org = (self.rectangle_max["x2"] + marge, 
                    self.rectangle_max["y1"]), fontFace = cv2.FONT_HERSHEY_PLAIN, fontScale = 1.5, 
                    color = (0, 140, 255), thickness = 1,  lineType = cv2.LINE_AA)
                self.aire_max = abs(self.rectangle_max["x2"] - self.rectangle_max["x1"])* \
                    abs(self.rectangle_max["y2"] - self.rectangle_max["y1"])  

            if self.rectangle_min :
                cv2.rectangle(frame, (self.rectangle_min["x1"], self.rectangle_min["y1"]), 
                    (self.rectangle_min["x2"], self.rectangle_min["y2"]), 
                    color = (0, 165, 255), thickness = 1, lineType = cv2.LINE_AA)
                cv2.putText(img = frame, text = "min", org = (self.rectangle_min["x2"] + marge, 
                        self.rectangle_min["y1"]), fontFace = cv2.FONT_HERSHEY_PLAIN, fontScale = 1.5, 
                        color = (0, 165, 255), thickness = 1,  lineType = cv2.LINE_AA)
                self.aire_min = abs(self.rectangle_min["x2"] - self.rectangle_min["x1"])* \
                    abs(self.rectangle_min["y2"] - self.rectangle_min["y1"])

            #DETECTION           
            contours,_ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            liste_rectangles = []
            for contour in contours:
                if self.rectangle_max and cv2.contourArea(contour) > self.aire_max :
                    continue
                elif cv2.contourArea(contour) < self.aire_min :
                    continue
                x, y, w, h = cv2.boundingRect(contour)
                if h < w:
                    continue
                rectangle = {"x" : x, "y" : y, "cx" : int(x + w/2), "cy" : int(y + h/2),  "w" : w, "h" : h}
                cv2.rectangle(frame, (x, y), (x + w, y + h),  color = (0, 255, 255), thickness = 2)
                liste_rectangles.append(rectangle)

            #ASSOCIATIONS MESURES RADARS
            if (nbr_frames%40==0):
                liste_points_radars = self.r.mget(["points_Ard", "points_RPi_1", "points_RPi_2"])
                points_radars = {rad : json.loads(pts_rad) if pts_rad else None for rad, pts_rad in zip(["Ard", "RPi_1", "RPi_2"], 
                    liste_points_radars)}
                
            if self.positions_radars:
                for nom_radar in ["Ard", "RPi_1", "RPi_2"]:
                    if nom_radar in self.positions_radars : 
                        position_radar = self.positions_radars[nom_radar]
                        if (nom_radar == "Ard"):
                            couleur = (0, 255, 0)
                        elif (nom_radar == "RPi_1"):
                            couleur = (255, 0, 0)
                        elif (nom_radar == "RPi_2"):
                            couleur = (0, 0, 255)

                        cv2.putText(img = frame, text = nom_radar, org = (int(position_radar["point_radar"]["x"] + marge), 
                            int(position_radar["point_radar"]["y"])), fontFace = cv2.FONT_HERSHEY_PLAIN, 
                            fontScale = 1.5, color = couleur, thickness = 1,  lineType = cv2.LINE_AA)

                        cv2.circle(frame, (int(position_radar["point_radar"]["x"]), 
                            int(position_radar["point_radar"]["y"])), 5, color = couleur, thickness = -1,  
                            lineType = cv2.LINE_AA)

                        cv2.circle(frame, (int(position_radar["point_radar"]["x"]), 
                            int(position_radar["point_radar"]["y"])), 5, color = (0, 0, 0), thickness = 1,  
                            lineType = cv2.LINE_AA)

                        cv2.arrowedLine(frame, (int(position_radar["point_radar"]["x"]), 
                            int(position_radar["point_radar"]["y"])), 
                            (int(position_radar["point_radar"]["x"] +  
                            position_radar["vecteur_unitaire"]["x"]),
                            int(position_radar["point_radar"]["y"] +  
                            position_radar["vecteur_unitaire"]["y"])),
                            color = couleur, thickness=1, tipLength=0.2, line_type = cv2.LINE_AA)

                        matrice = []
                        if points_radars[nom_radar]:  
                            points = points_radars[nom_radar]
                            for point in points: 
                                point["x"] = int(position_radar["point_radar"]["x"] + 
                                        position_radar["vecteur_unitaire"]["x"]*point["d"])
                                
                                point["y"] =  int(position_radar["point_radar"]["y"] + 
                                        position_radar["vecteur_unitaire"]["y"]*point["d"])

                                cv2.ellipse(frame, (point["x"], point["y"]), (8, 4), 
                                    angle = 0, startAngle = 0, endAngle = 360, color = couleur, 
                                    thickness = -1, lineType = cv2.LINE_AA) 

                                cv2.rectangle(frame, (point["x"]-marge, point["y"]-marge), 
                                    (point["x"]+marge, point["y"]+marge), color = (0, 0, 0), 
                                    thickness = 1, lineType = cv2.LINE_AA)

                                liste_distances = []
                                for rect in liste_rectangles : 
                                    distance = calculer_distance({"x" : rect["cx"], "y" : rect["cy"]}, point)
                                    liste_distances.append(distance)
                                matrice.append(liste_distances)

                            if matrice:
                                indices=m.compute(matrice)
                                for (indice_point, indice_rect) in indices:
                                    point, rect = points[indice_point], liste_rectangles[indice_rect]
                                    if self.action_enregistrement == "continuer_enregistrement" :
                                        mesures.append({"point": {"x" : rect["cx"],"y" : rect["cy"]}, "frame" : nbr_frames,
                                            "t" : int(100*(time.time() - t))/100, "v" : int(100*point["v"])/100, "d" : int(100*point["d"])/100,
                                            "radar" : nom_radar})
                                    cv2.line(frame, (point["x"], point["y"]), (rect["cx"], rect["cy"]),
                                        color = couleur,  lineType = cv2.LINE_AA)
                                    if (nom_radar == "Ard"):
                                        offset = 0
                                    elif (nom_radar == "RPi_1"):
                                        offset = rectangle["h"]//2
                                    elif (nom_radar == "RPi_2"):
                                        offset = rectangle["h"]
                                    cv2.putText(frame, str(int(10*point["v"])/10) + "m/s " + str(int(10*point["d"])/10)+ "m", 
                                        (rect["x"] + rect["w"] + marge, int(rect["y"] + offset + marge)),
                                        fontFace = cv2.FONT_HERSHEY_PLAIN, fontScale = 1.8, color = couleur, thickness = 1,
                                        lineType = cv2.LINE_AA)
                                    cv2.rectangle(frame, (rect["x"], rect["y"]), 
                                        (rect["x"] + rect["w"], rect["y"] + rect["h"]),
                                        color = couleur, thickness = 2, lineType = cv2.LINE_AA)

            if self.action_enregistrement == "debuter_enregistrement" :
                mesures = [] 
                nbr_frames = 0
                t = time.time()
                W = int(capture.get(3))
                H = int(capture.get(4))
                cap = cv2.VideoWriter("capture.avi",  
                    cv2.VideoWriter_fourcc(*"MJPG"), 1, (W , H)) 
                self.action_enregistrement = "continuer_enregistrement"

            elif self.action_enregistrement == "continuer_enregistrement" and cap != None:
                cap.write(frame)
                cv2.circle(frame, (W-30, 20), 10, color = (0, 0, 255), thickness = -1,  
                    lineType = cv2.LINE_AA)   
 
            elif self.action_enregistrement == "arreter_enregistrement" and cap != None :
                self.r.set("nbr_frames", json.dumps(nbr_frames))
                self.r.set("mesures", json.dumps(mesures))

                cap.release()
                cap = None
                self.action_enregistrement = None
            else : 
                pass

            nbr_frames += 1

            if self.rectangle_max :
                cv2.rectangle(frame, (self.rectangle_max["x1"], self.rectangle_max["y1"]), 
                    (self.rectangle_max["x2"], self.rectangle_max["y2"]), 
                    color = (0, 140, 255), thickness = 1, lineType = cv2.LINE_AA)
                cv2.putText(img = frame, text = "max", org = (self.rectangle_max["x2"] + marge, 
                    self.rectangle_max["y1"]), fontFace = cv2.FONT_HERSHEY_PLAIN, fontScale = 1.5, 
                    color = (0, 140, 255), thickness = 1,  lineType = cv2.LINE_AA)

            if self.rectangle_min :
                cv2.rectangle(frame, (self.rectangle_min["x1"], self.rectangle_min["y1"]), 
                    (self.rectangle_min["x2"], self.rectangle_min["y2"]), 
                    color = (0, 165, 255), thickness = 1, lineType = cv2.LINE_AA)
                cv2.putText(img = frame, text = "min", org = (self.rectangle_min["x2"] + marge, 
                        self.rectangle_min["y1"]), fontFace = cv2.FONT_HERSHEY_PLAIN, fontScale = 1.5, 
                        color = (0, 165, 255), thickness = 1,  lineType = cv2.LINE_AA)
            
            fps = cv2.getTickFrequency()/(cv2.getTickCount()-ticks)
            cv2.putText(frame, "FPS : {:05.2f}".format(fps), (10, 25), fontFace = cv2.FONT_HERSHEY_PLAIN, 
                fontScale = 1.8, color = (255, 0, 0), thickness = 1, lineType = cv2.LINE_AA)
            # ret, buffer = cv2.imencode(".jpg", fgmask)
            # fgmask = buffer.tobytes()
            # yield (b"--frame\r\n" 
            #         b"Content-Type: image/jpeg\r\n\r\n" + fgmask + b"\r\n")
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n" 
                    b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    def lire_capture(self):
        capture=cv2.VideoCapture("capture.avi")
        while True :
            ret, frame = capture.read()
            ticks = cv2.getTickCount()
            fps_cap = 30
            cv2.waitKey(int((1 / int(fps_cap))*1000))
            if not ret:
                break
            fps = cv2.getTickFrequency()/(cv2.getTickCount()-ticks)
            cv2.putText(frame, "FPS : {:05.2f}".format(fps), (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2, cv2.LINE_AA)
            ret, buffer = cv2.imencode(".jpg", frame)  
            frame = buffer.tobytes()
            yield (b"--frame\r\n" 
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")









