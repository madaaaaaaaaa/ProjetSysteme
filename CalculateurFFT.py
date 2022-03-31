import numpy as np
import redis
from threading import Thread
import traceback
import json
from queue import Queue, Empty
import time
import random 
import argparse
from scipy.signal import convolve, find_peaks
import munkres
#Mettre du Numpy/Scipy partout + Multiprocessing

def CA_CFARv2(fft, frequences, n_train, n_guard, fa_rate=1/1000):
    alpha = n_train * (fa_rate ** (-1 / n_train) - 1)
    ones = np.ones(n_train//2)
    zeros = np.zeros(n_guard)
    kernel = np.concatenate([ones, zeros, ones])
    conv = convolve(fft, kernel, mode = "same")
    mean = conv/n_train
    thresholds = mean*alpha
    peaks, properties = find_peaks(fft, height = thresholds, distance = (n_train + n_guard)//2)
    return peaks.tolist(), [frequences[i] for i in peaks], \
        properties["peak_heights"].tolist(), thresholds.tolist()
                
def calculerFFT(echantillons, mode, N_FFT, n_train, n_guard, taux_fa):
    Ns =  200
    Fs =  200000
    frequences =  [-Fs/2 + ((Fs*i)/N_FFT) for i in range(N_FFT)]
    max_voltage = 3.3
    ADC_bits = 12
    ADC_intervals = 2 ** ADC_bits

    I, Q = echantillons["I"], echantillons["Q"]
    I, Q = np.array(echantillons["I"]), np.array(echantillons["Q"])

    I = np.subtract(np.multiply(I, max_voltage / ADC_intervals), 
            np.mean(np.multiply(I, max_voltage / ADC_intervals)))
    Q = np.subtract(np.multiply(Q, max_voltage / ADC_intervals),
            np.mean(np.multiply(Q, max_voltage / ADC_intervals)))

    if (mode == 3):

        I_m = I[0:Ns]
        Q_m = Q[0:Ns]
        I_d = I[Ns:2 * Ns]
        Q_d = Q[Ns:2 * Ns]

        Vecteur_complexe_m = I_m + 1j*Q_m
        Vecteur_complexe_d = I_d - 1j*Q_d

        #fenêtre de hanning
        Vecteur_complexe_m = Vecteur_complexe_m*np.hanning(Ns)*2/3.3
        Vecteur_complexe_d = Vecteur_complexe_d*np.hanning(Ns)*2/3.3

        #zero-padding
        fft_m = {"fft" : 2*np.absolute(np.fft.fftshift(np.fft.fft(Vecteur_complexe_m/Ns, N_FFT)))}
        fft_d = {"fft" : 2*np.absolute(np.fft.fftshift(np.fft.fft(Vecteur_complexe_d/Ns, N_FFT)))}
        #CA-CFAR
        fft_m["indices_pics"], fft_m["frequences_pics"], fft_m["valeurs_pics"], fft_m["seuils"] \
                = CA_CFARv2(fft_m["fft"], frequences, n_train, n_guard, taux_fa)  
                
        fft_d["indices_pics"], fft_d["frequences_pics"], fft_d["valeurs_pics"], fft_d["seuils"] \
                = CA_CFARv2(fft_d["fft"], frequences, n_train, n_guard, taux_fa)  
        
        fft_m["fft"] = fft_m["fft"].tolist()
        fft_d["fft"] = fft_d["fft"].tolist()
        return {"FFT" : 
                    {
                    "fft_m" : fft_m,
                    "fft_d" : fft_d,
                    "frequences" : frequences,
                    },
                }

    elif (mode == 4):
        I_m1 = I[0:Ns]
        Q_m1 = Q[0:Ns]
        I_d1 = I[Ns:2*Ns]
        Q_d1 = Q[Ns:2*Ns]

        I_m2 = I[2*Ns:int(2.75*Ns)]
        Q_m2 = Q[2*Ns:int(2.75*Ns)]
        I_d2 = I[int(2.75*Ns):int(3.5*Ns)]
        Q_d2 = Q[int(2.75*Ns):int(3.5*Ns)]

        vecteur_complexe_m1 = I_m1 + 1j*Q_m1
        vecteur_complexe_d1 = I_d1 - 1j*Q_d1

        vecteur_complexe_m2 = I_m2 + 1j*Q_m2
        vecteur_complexe_d2 = I_d2 - 1j*Q_d2

        vecteur_complexe_m1 = vecteur_complexe_m1*np.hanning(Ns)*2/3.3
        vecteur_complexe_d1 = vecteur_complexe_d1*np.hanning(Ns)*2/3.3

        vecteur_complexe_m2 = vecteur_complexe_m2*np.hanning(0.75*Ns)*2/3.3
        vecteur_complexe_d2 = vecteur_complexe_d2*np.hanning(0.75*Ns)*2/3.3

        fft_m1 = 2*np.absolute(np.fft.fftshift(np.fft.fft(vecteur_complexe_m1/Ns, N_FFT)))
        fft_d1 = 2*np.absolute(np.fft.fftshift(np.fft.fft(vecteur_complexe_d1/Ns, N_FFT)))

        fft_m2 = 2*np.absolute(np.fft.fftshift(np.fft.fft(vecteur_complexe_m2/Ns, N_FFT)))
        fft_d2 = 2*np.absolute(np.fft.fftshift(np.fft.fft(vecteur_complexe_d2/Ns, N_FFT)))

        # start = N_FFT//2
        # fft_m1[start] = fft_m1[start - 1]
        # fft_d1[start] = fft_d1[start - 1]
        # fft_m2[start] = fft_m2[start - 1]
        # fft_d2[start] = fft_d2[start - 1]
        
        # fft_m1_log = 20*np.log(fft_m1)
        # fft_d1_log = 20*np.log(fft_d1)
        # fft_m2_log = 20*np.log(fft_m2)
        # fft_d2_log = 20*np.log(fft_d2)

        FFT_m1 = {"fft" : fft_m1}
        FFT_d1 = {"fft" : fft_d1}

        FFT_m2 = {"fft" : fft_m2}
        FFT_d2 = {"fft" : fft_d2}

        FFT_m1["indices_pics"], FFT_m1["frequences_pics"], FFT_m1["valeurs_pics"], FFT_m1["seuils"] \
                = CA_CFARv2(fft_m1, frequences, n_train, n_guard, taux_fa)  
                
        FFT_d1["indices_pics"], FFT_d1["frequences_pics"], FFT_d1["valeurs_pics"], FFT_d1["seuils"] \
                = CA_CFARv2(fft_d1, frequences, n_train, n_guard, taux_fa)  


        FFT_m2["indices_pics"], FFT_m2["frequences_pics"], FFT_m2["valeurs_pics"], FFT_m2["seuils"] \
                = CA_CFARv2(fft_m2, frequences, n_train, n_guard, taux_fa)     

        FFT_d2["indices_pics"], FFT_d2["frequences_pics"], FFT_d2["valeurs_pics"], FFT_d2["seuils"] \
                = CA_CFARv2(fft_d2, frequences, n_train, n_guard, taux_fa) 

        FFT_m1["fft"] = FFT_m1["fft"].tolist()
        FFT_d1["fft"] = FFT_d1["fft"].tolist()

        FFT_m2["fft"] = FFT_m2["fft"].tolist()
        FFT_d2["fft"] = FFT_d2["fft"].tolist() 

        return {"FFT" : {
                    "fft_m1" : FFT_m1,
                    "fft_d1" : FFT_d1,
                    "fft_m2" : FFT_m2,
                    "fft_d2" :  FFT_d2,
                    "frequences" : frequences,
                    },
                }

    else :
        raise Exception("mode 3 ou mode 4 seulement")

def associations_frequences(dsp, mode=4, f0=5, BW=240, e=1):
    #reecrire avec numpy
    Ns = 200
    c = 3e8
    f0 = (24000 + f0)*1e6
    BW = BW * 1e6
    Fs  = 200000
    points_potentiels = []
    points_certains = []
    
    if (mode==3):
        droites_m, droites_d = [], []
        for f_pic in dsp["fft_m"]["frequences_pics"] :
            droite = {
                "m" : -(f0*(Ns/Fs))/BW,
                "b" : (f_pic*c*(Ns/Fs))/(2*BW)
            }
            droites_m.append(droite)
        for f_pic in dsp["fft_d"]["frequences_pics"] :
            droite = {
                "m" : (f0*(Ns/Fs))/BW,
                "b" : (f_pic*c*(Ns/Fs))/(2*BW)
            }
            droites_d.append(droite)
        for d_m in droites_m :
            for d_d in droites_d :
                if (d_d["m"] - d_m["m"]!=0) :
                    v = (d_m["b"]-d_d["b"])/(d_d["m"] - d_m["m"])
                    d =   d_d["m"]*v + d_d["b"] 
                    intersection = {
                        "v" : v,
                        "d" : d,
                    }
                    points_potentiels.append(intersection)                
        return {
            "points" : {
                "points_certains" : points_certains, 
                "points_potentiels" : points_potentiels
                },
            "droites" : {
                "droites_m" : droites_m, 
                "droites_d" : droites_d
                }
        }

    elif (mode==4):
        droites_m1, droites_d1 = [], []
        for f_m1 in dsp["fft_m1"]["frequences_pics"] :
            droite = {
                "m" : -(f0*(Ns/Fs))/BW,
                "b" : (f_m1*c*(Ns/Fs))/(2*BW)
            }
            droites_m1.append(droite)
        for f_d1 in dsp["fft_d1"]["frequences_pics"] :
            droite = {
                "m" : (f0*(Ns/Fs))/BW,
                "b" : (f_d1 *c*(Ns/Fs))/(2*BW)
            }
            droites_d1.append(droite)

        droites_m2, droites_d2 = [], []
        for f_m2 in dsp["fft_m2"]["frequences_pics"] :
            droite = {
                "m" : -(f0*(0.75*(Ns/Fs)))/BW,
                "b" : (f_m2 *c*(0.75*(Ns/Fs)))/(2*BW)
            }
            droites_m2.append(droite)
        for f_d2 in dsp["fft_d2"]["frequences_pics"] :
            droite = {
                "m" : (f0*(0.75*(Ns/Fs)))/BW,
                "b" : (f_d2*c*(0.75*(Ns/Fs)))/(2*BW)
            }
            droites_d2.append(droite)

        droites_utilisees = []
        for d_m1 in droites_m1:
            for d_d1 in droites_d1:
                if not d_d1 in droites_utilisees and d_d1["m"] - d_m1["m"] != 0:
                    v = (d_m1["b"]-d_d1["b"])/(d_d1["m"] - d_m1["m"])
                    d =   d_d1["m"]*v + d_d1["b"] 
                    intersection = {
                        "v" : v,
                        "d" : d
                    }
                    for d_m2 in droites_m2 :
                        if not d_m2 in droites_utilisees :
                            if abs(d_m2["m"]*intersection["v"]+d_m2["b"]
                                    - intersection["d"])<e :
                                points_potentiels.append(intersection)
                                droites_utilisees+= [d_m1, d_d1, d_m2]
                                for d_d2 in droites_d2:
                                    if not d_d2 in droites_utilisees :
                                        if abs(d_d2["m"]*intersection["v"]+d_d2["b"]
                                                - intersection["d"])<e :
                                            points_certains.append(intersection)
                                            droites_utilisees.append(d_d2)           
        return {
            "points" : {
                "points_certains" : points_certains, 
                "points_potentiels" : points_potentiels
                },
            "droites" : {
                "droites_d1" : droites_d1,
                "droites_m1" : droites_m1, 
                "droites_m2" : droites_m2,
                "droites_d2" : droites_d2,
                }
        }
    else :
        raise Exception("mode 3 ou mode 4 seulement")

def associations_munkres(dsp, mode=4, f0=5, BW=240, e=1):
    Ns = 200
    c = 3e8
    f0 = (240 + f0)*1e9
    BW = BW * 1e6
    Fs  = 200000
    m = munkres.Munkres()
    if mode==3 :
        points = []
        matrice = []
        for f_m in dsp["fft_m"]["frequences_pics"] : 
            ecarts = []
            for f_d in dsp["fft_m"]["frequences_pics"] : 
                ecarts.append(abs(f_m - f_d))
            matrice.append(ecarts)
        indices = m.compute(matrice)
        if matrice:
            for (i_m, i_d) in indices: 
                f_m = dsp["fft_m"]["frequences_pics"][i_m]
                f_d = dsp["fft_d"]["frequences_pics"][i_d]
                f_doppler = (f_m - f_d)/2
                deltaf = (f_m + f_d)/2
                v = c*f_doppler / (2*f0)
                d = (Ns / Fs)*c*deltaf/(2*BW)
                points.append({"v" : v, "d" : d})
    if mode==4 :
        points1 = []
        matrice1 = []
        for f_m1 in dsp["fft_m1"]["frequences_pics"] : 
            ecarts = []
            for f_d1 in dsp["fft_d1"]["frequences_pics"] : 
                ecarts.append(abs(f_m1 - f_d1))
            matrice1.append(ecarts)
        if matrice1:
            indices = m.compute(matrice1)
            for (i_m1, i_d1) in indices: 
                f_m1 = dsp["fft_m1"]["frequences_pics"][i_m1]
                f_d1 = dsp["fft_d1"]["frequences_pics"][i_d1]
                f_doppler = (f_m1 - f_d1)/2
                deltaf = (f_m1 + f_d1)/2
                v = c*f_doppler / (2*f0)
                d = (Ns / Fs)*c*deltaf/(2*BW)
                points1.append({"v" : v, "d" : d})
        
        points2 = []
        matrice2 = []
        for f_m2 in dsp["fft_m2"]["frequences_pics"] : 
            ecarts = []
            for f_d2 in dsp["fft_d2"]["frequences_pics"] : 
                ecarts.append(abs(f_m2 - f_d2))
            matrice2.append(ecarts)
        if matrice2:
            indices = m.compute(matrice2)
            for (i_m2, i_d2) in indices: 
                f_m2 = dsp["fft_m2"]["frequences_pics"][i_m2]
                f_d2 = dsp["fft_d2"]["frequences_pics"][i_d2]
                f_doppler = (f_m2 - f_d2)/2
                deltaf = (f_m2 + f_d2)/2
                v = c*f_doppler / (2*f0)
                d = (Ns / Fs)*c*deltaf/(2*BW)
                points2.append({"v" : v, "d" : d})
        matrice = []
        points = []
        for pt1 in points1 : 
            ecarts = []
            for pt2 in points2 :
                ecarts.append(abs(pt1["d"] - pt2["d"]))
            matrice.append(ecarts)
        if matrice :
            indices = m.compute(matrice)
            for (i_pt1, i_pt2) in indices : 
                pt1 = points1[i_pt1]
                pt2 = points2[i_pt2]
                d = (pt1["d"] + pt2["d"])/2
                v = (pt1["v"] + pt2["v"])/2
                if d>0 and d<40 and abs(v)<10:
                    point = {"d" : d, "v" : v}
                    points.append(point)







    
        

