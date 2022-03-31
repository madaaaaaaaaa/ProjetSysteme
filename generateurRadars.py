import redis
import random
import json
import CalculateurFFT
import time
r = redis.Redis(host="localhost",  port=6379, db=0)


while True :
    for nom_radar in ["Ard", "RPi_1", "RPi_2"] :
        echantillons = {"I" : [int(2000*random.random()) for _ in range(2000)],
            "Q" : [int(2000*random.random()) for _ in range(2000)]}
        dsp_radar = CalculateurFFT.calculerFFT(echantillons, 4, 2048, 40, 20, 1/100)
        associations = CalculateurFFT.associations_frequences(dsp_radar["FFT"])
        dsp_radar["associations"] = associations
    ################
        points_generes = [{"d" : 3*random.random(), "v" : 3*random.random()}]
        dsp_radar["associations"]["points"]["points_potentiels"] = points_generes
    ################
        r.set("dsp_" + nom_radar, json.dumps(dsp_radar))
        #r.set("points_" + nom_radar, json.dumps(points_generes))
        r.set("points_" + nom_radar, json.dumps([
            {"d" : 3*random.random(), "v" : 3*random.random()},
            {"d" : 3*random.random(), "v" : 3*random.random()}, 
            {"d" : 3*random.random(), "v" : 3*random.random()}
            ])
        )
    time.sleep(0.05)


