function supprimer_graphe(div){
    Plotly.purge(div)
}

function obtenir_echantillons(N_FFT, N){
    let echantillons = new Array()
    for (let i = -(N_FFT/(2*N)); i<(N_FFT/(2*N)); i++){
        echantillons.push(i)
    }
    return echantillons
}

function obtenir_echantillons_pics(frequences, echantillons, frequences_pics, N_FFT){
    echantillons_pics = new Array()
    for (let frequence_pic of frequences_pics){
        let i = frequences.indexOf(frequence_pic)
        if (i == -1){
            echantillons_pics.push(null)
        }
        else{
            echantillons_pics.push(echantillons[i])
        }
           
    }
    return echantillons_pics
}

function tracer_FFT(resultats_dsp_FFT, fft_selec, mode_affichage, callback){
    let N = 8
    let data = new Array()
    let plots_pics = new Array()
    let plots_FFT = new Array()
    let plots_seuils = new Array()
    let color
    let color_CA_CFAR
    let range
    let dtick
    let title
    let N_FFT = N*resultats_dsp_FFT["frequences"].length
    for (let [nom_fft, fft] of Object.entries(resultats_dsp_FFT)){
        if ((fft_selec == "triangle" && (nom_fft == "fft_m" || nom_fft == "fft_d"))
            ||(fft_selec == "triangle1" && (nom_fft == "fft_m1" || nom_fft == "fft_d1"))
            ||(fft_selec == "triangle2" && (nom_fft == "fft_m2" || nom_fft == "fft_d2"))){
            if (nom_fft == "fft_m" || nom_fft == "fft_m1" || nom_fft == "fft_m2"){
                color = "orange"
                color_CA_CFAR = "blue"
                color_pics = "darkorange"
            }
            else if (nom_fft == "fft_d" || nom_fft == "fft_d1" || nom_fft == "fft_d2"){
                color = "green"
                color_CA_CFAR = "red"
                color_pics = "yellowgreen"
            }

            if (mode_affichage == "frequences"){
                range = [-200000/N, 200000/N]
                dtick = 5000
                title = {"text" : "Fréquences"}
                if (fft["frequences_pics"].length == 0 && fft["valeurs_pics"].length == 0){
                    fft["frequences_pics"] = [null]
                    fft["valeurs_pics"] = [null]
                }
                plots_pics.push({x: fft["frequences_pics"], y: fft["valeurs_pics"], 
                    mode: "markers", type: "scattergl", name: "Pics " + nom_fft, marker: {size : 20, 
                    symbol : "square-open", color : color_pics, line : {width : 3}}
                    })
                if (resultats_dsp_FFT["frequences"].length == 0 && fft["fft"].length == 0){
                    resultats_dsp_FFT["frequences"] = [null]
                    fft["fft"] = [null]
                }
                plots_FFT.push({x: resultats_dsp_FFT["frequences"], y: fft["fft"], mode: "line", 
                    type: "scattergl", name: nom_fft, line : {width : 3, 
                    color : color}
                    })
                if (resultats_dsp_FFT["frequences"].length == 0 && fft["seuils"].length == 0){
                    resultats_dsp_FFT["frequences"] = [null]
                    fft["seuils"] = [null]
                }
                plots_seuils.push({x: resultats_dsp_FFT["frequences"], y: fft["seuils"], 
                    mode: "line", type: "scattergl", name: "CA-CFAR", line : 
                    {width : 2, color : color_CA_CFAR}
                    })
            }
            else if (mode_affichage == "echantillons"){
                range = [-N_FFT/(2*N), N_FFT/(2*N)]
                dtick = 20*(N_FFT/2048)
                title = {"text" : "Echantillons"}
                let echantillons = obtenir_echantillons(N_FFT, N)
                let echantillons_pics = obtenir_echantillons_pics(resultats_dsp_FFT["frequences"], echantillons,
                    fft["frequences_pics"], N_FFT, N)
                if (echantillons_pics.length == 0 && fft["valeurs_pics"].length == 0){
                    echantillons_pics = [null]
                    fft["valeurs_pics"] = [null]
                }
                plots_pics.push({x: echantillons_pics, y: fft["valeurs_pics"], 
                    mode: "markers", type: "scattergl", name: "pics " + nom_fft, marker: {size : 15, 
                    symbol : "square-open", color : color_pics, line : {width : 3}}
                })
                if (echantillons.length == 0 && fft["fft"].length == 0){
                    echantillons = [null]
                    fft["fft"] = [null]
                }
                plots_FFT.push({x: echantillons, y: fft["fft"], mode: "line", 
                    type: "scattergl", name: nom_fft, line : {width : 3, 
                    color : color}
                    })
                if (echantillons.length == 0 && fft["seuils"].length == 0){
                    echantillons = [null]
                    fft["seuils"] = [null]
                }
                plots_seuils.push({x: echantillons, y: fft["seuils"], 
                    mode: "line", type: "scattergl", name: "CA-CFAR "+ nom_fft, line : 
                    {width : 2, color : color_CA_CFAR}
                })
            }
        }
    }
    let layout = {
        title : {
            text : "FFT - CA-CFAR"
        },
        xaxis : {
            range : range,
            dtick: dtick,
            title : title
            },
        yaxis: {
            title : {
                text : "Amplitude"
                }
        },
        showlegend:true,
        margin: {
            l: 80,
            r: 80,
            b: 80,
            t: 60,
            pad: 20
            },
        }
    data = [...plots_FFT, ...plots_seuils, ...plots_pics]
    Plotly.react(div_graphe, data, layout, {staticPlot: true, 
        responsive : true})
    callback()
}

function tracer_droites(resultats_dsp_associations, callback){
    let data = new Array()
    for (let [noms_droites, droites] of Object.entries(resultats_dsp_associations["droites"])){
        let showlegend = true
        if (noms_droites == "droites_m"){
            color = "black"
        }
        else if (noms_droites == "droites_d"){
            color = "red"
        } 
        else if (noms_droites == "droites_m1"){
            color = "black"
        }
        else if (noms_droites == "droites_d1"){
            color = "red"
        }
        else if (noms_droites == "droites_m2"){
            color = "blue"
        }
        else if (noms_droites == "droites_d2"){
            color = "green"
        }
        if (droites.length == 0){
            let plot = {x : [null], y : [null], legendgroup : noms_droites, 
                showlegend : showlegend, name : noms_droites, line : {width : 3, color : color}}
            data.push(plot)
        }
        else{
            for (let droite of droites){
                let plot = {
                    x : [-20, 50], y : [droite["m"]*(-20) + droite["b"], droite["m"]*50 + droite["b"]],
                        mode : "line", type: "scattergl", line : {width : 3, color : color}, 
                        legendgroup : noms_droites, showlegend : showlegend, name : noms_droites
                    }
                showlegend = false
                data.push(plot)
            }
        }
    }
    let x = new Array()
    let y = new Array()
    for (let point of Object.values(resultats_dsp_associations["points"]["points_potentiels"])){
        x.push(point["v"])
        y.push(point["d"])
    }
    let plot_points_potentiels
    if (x.length == 0 && y.length == 0){
        plot_points_potentiels = {
            x : [null], y : [null], mode : "markers", type : "scattergl",name : "points potentiels",
            marker: {size : 20, symbol : "square-open", color : "yellowgreen", line : {
                width : 3}}
                
        }
    }
    else{
        plot_points_potentiels = {
            x : x, y : y, mode : "markers", type : "scattergl",name : "points potentiels",
            marker: {size : 20, symbol : "square-open", color : "yellowgreen", line : {
                width : 3}}
                
        }
    }
    data.push(plot_points_potentiels)
    x = new Array()
    y = new Array()
    for (let point of Object.values(resultats_dsp_associations["points"]["points_certains"])){
        x.push(point["v"])
        y.push(point["d"])
    }
    let plot_points_certains
    if (x.length == 0 && y.length == 0){
        plot_points_certains = {
            x : [null], y : [null], mode : "markers", type : "scattergl",name : "points certains",
            marker: {size : 20, symbol : "square-open", color : "orange", line : {
                width : 3}}
        }
    }
    else{
        plot_points_certains = {
            x : x, y : y, mode : "markers", type : "scattergl",name : "points certains",
            marker: {size : 20, symbol : "square-open", color : "orange", line : {
                width : 3}}
                
        }
    }
    data.push(plot_points_certains)
    let layout = {
        title : {
            text : "Associations des pics"
        },
        xaxis : {
            range : [-5, 5],
            gridwidth: 1,
            dtick : 2,
            title : {
                text : "Vitesse en m/s"
                }
            },
        yaxis: {
            range : [-10, 40],
            gridwidth: 1,
            dtick : 5,
            title : {
                text : "Distance en m"
                }
        },
        showlegend:true,
        margin: {
            l: 80,
            r: 80,
            b: 80,
            t: 60,
            pad: 20
        },
    }
    Plotly.react(div_graphe, data, layout, {staticPlot: true, 
    responsive : true})
    callback()
}


function tracer_points(resultats_dsp){
    let data = []
    for (let [nom_radar, object] of Object.entries(resultats_dsp)){
        if ("associations" in object){
            let points_radar = object["associations"]["points"]["points_potentiels"]
        if (nom_radar=="Ard"){
            
            color = "#00ff00"
        }
        else if (nom_radar=="RPi_1"){
            color = "blue"
        }
        else if (nom_radar=="RPi_2"){
            color = "red"
            
        }
        let x = new Array()
        let y = new Array()
        for (let point of points_radar){
            x.push(point["d"])
            y.push(point["v"])
        }
        if (x.length==0 && y.length==0){
            let plot = {x : [null], y : [null], mode:"markers", type : "scattergl", name : nom_radar, 
                marker : {size : 20, color:color, line : {width : 1, color : "black"}}}
            data.push(plot)
        }
        else {
            let plot = {x : x, y : y, mode:"markers", type : "scattergl", name : nom_radar, 
                marker : {size : 20, color:color, line : {width : 1, color : "black"}}}
            data.push(plot)
            }
        }
    }
    let layout = {
        title : {
            text : "Mesures distance/vitesse"
        },
        xaxis : {
            range : [-10, 40],
            gridwidth: 1,
            dtick : 5,
            title : {
                text : "distance en m"
                }
            },
        yaxis: {
            range : [-5, 5],
            gridwidth: 1,
            dtick : 2,
            title : {
                text : "vitesse en m/s"
                }
        },
        showlegend:true,
        margin: {
            l: 80,
            r: 80,
            b: 80,
            t: 60,
            pad: 20
        },
    }
    Plotly.react(div_graphe, data, layout, {staticPlot: true, 
        responsive : true})
    callback()
}