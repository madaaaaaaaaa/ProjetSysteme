from flask import Flask, render_template, Response, request
import redis 
import json
import random
from DetecteurVideo2 import DetecteurVideo
import traceback
import argparse
import time
from threading import Thread

app = Flask(__name__)

@app.route('/')
def hello_world():  
    return render_template("index.html")

@app.route("/connexionRedis")
def connexion_Redis() : 
    try :
        r.ping()
        return json.dumps("connecte")
    except :
        traceback.print_exc()
        return json.dumps("pas connecte")

@app.route("/envoyer_rectangle_max", methods = ["POST"])
def rectangle_max():
    jsn = request.get_json(force=True)
    detecteurVideo.rectangle_max = jsn["rectangle_limite"]
    return ""

@app.route("/envoyer_rectangle_min", methods = ["POST"])
def rectangle_min():
    jsn = request.get_json(force=True)
    detecteurVideo.rectangle_min = jsn["rectangle_limite"]
    return ""

@app.route("/recuperer_positions_radars", methods=["POST"])
def recuperer_positions_radars():
    jsn = request.get_json(force=True)
    positions_radars = {} 
    for nom_radar in ["Ard", "RPi_1", "RPi_2"]:
        if "vecteur_unitaire" in jsn[nom_radar] and "point_radar" in jsn[nom_radar]:
            positions_radars[nom_radar] = {
                "vecteur_unitaire" : jsn[nom_radar]["vecteur_unitaire"],
                "point_radar" : jsn[nom_radar]["point_radar"]
            }
    detecteurVideo.positions_radars = positions_radars
    return ""

@app.route("/recuperer_mesures", methods=["GET"])
def recuperer_mesures():
    N = 8       #On affiche 1/4
    N_min = (int(N/2) - 1)/N
    N_max = (int(N/2) + 1)/N
    dsp = {}
    for nom_radar in ["Ard", "RPi_1", "RPi_2"]:
        dsp_radar = r.get("dsp_" + nom_radar)
        if dsp_radar != None:
            dsp_radar = json.loads(dsp_radar)
            dsp_radar_FFT = dsp_radar["FFT"]
            frequences = dsp_radar_FFT["frequences"]
            dsp_radar_FFT["frequences"] = frequences[int(N_min*len(frequences)):int(N_max*len(frequences))]
            if "fft_m" in dsp_radar_FFT and "fft_d" in dsp_radar_FFT :
                for fft in [dsp_radar_FFT["fft_m"], dsp_radar_FFT["fft_d"]]:
                    fft["seuils"] = fft["seuils"] [int(N_min*len(fft["seuils"])):int(N_max*len(fft["seuils"] ))]
                    fft["fft"] = fft["fft"] [int(N_min*len(fft["fft"])):int(N_max*len(fft["fft"] ))]

            elif "fft_m1" in dsp_radar_FFT and "fft_d1" in dsp_radar_FFT and "fft_m2" in dsp_radar_FFT and "fft_d2" in dsp_radar_FFT:
                for fft in [dsp_radar_FFT["fft_m1"], dsp_radar_FFT["fft_d1"], dsp_radar_FFT["fft_m2"], dsp_radar_FFT["fft_d2"]]:
                    fft["seuils"] = fft["seuils"] [int(N_min*len(fft["seuils"] )):int(N_max*len(fft["seuils"]))]
                    fft["fft"] = fft["fft"] [int(N_min*len(fft["fft"] )):int(N_max*len(fft["fft"] ))]
        dsp[nom_radar] = dsp_radar
    return dsp

@app.route("/flux_video")
def flux_video():
    detecteurVideo.positions_radars = {} 
    return Response(detecteurVideo.lancer_detection(), 
        mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/debuter_enregistrement")
def debuter_enregistrement():
    detecteurVideo.action_enregistrement = "debuter_enregistrement"
    return ""

@app.route("/arreter_enregistrement")
def arreter_enregistrement():
    detecteurVideo.action_enregistrement = "arreter_enregistrement"
    return ""

@app.route("/flux_capture")
def flux_capture():
    return Response(detecteurVideo.lire_capture(), 
        mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/lire_capture")
def lire_capture():
    return render_template("lire_capture.html")

@app.route("/obtenir_nbr_frames")
def nbr_frames():
    nbr_frames = r.get("nbr_frames")
    if (nbr_frames!=None) :
        nbr_frames = json.loads(nbr_frames)
    else : 
        nbr_frames = 0
    return json.dumps(nbr_frames)

@app.route("/obtenir_mesures")
def obtenir_mesures():
    mesures = r.get("mesures")
    if (mesures!=None) :
        mesures = json.loads(mesures)
    else : 
        mesures = []
    return json.dumps(mesures)

if __name__=="__main__": 
    print("\n/!\ Ne pas se connecter sur WifiCampus\n") 
    parser = argparse.ArgumentParser()
    parser.add_argument("adr_IPv4_redis")
    parser.add_argument("adr_IPv4_video")
    args = parser.parse_args()
    r = redis.Redis(host=args.adr_IPv4_redis,  port=6379)
    detecteurVideo = DetecteurVideo(r, args.adr_IPv4_video)
    app.run(host="localhost", debug=True, threaded = True)
    



