let rayon = 10
let w = 10
let h = 10
let marge = 20
let radar_drag = null

Ard.couleur = "#00ff00"
Ard.nom = "Ard"

RPi_1.couleur = "blue"
RPi_1.nom = "RPi_1"

RPi_2.couleur = "red"
RPi_2.nom = "RPi_2"

let x1 = null
let y1 = null
let x2 = null
let y2 = null


let liste_radars = [Ard, RPi_1, RPi_2]
for (let radar of liste_radars){
    radar.vecteur = null
    radar.distance_vecteur = null
    radar.div_distance_vecteur = null
    radar.addEventListener("dragstart", function(){
        radar_drag = radar
        dessiner_autres_vecteurs(radar_drag)
        if (radar.div_distance_vecteur != null){
            div_video.removeChild(radar.div_distance_vecteur)
            radar.div_distance_vecteur = null
        }
    })
}

div_radars.addEventListener("drop", function(event){
    dropzone_radars.appendChild(radar_drag)
    radar_drag.setAttribute("style", "")
})


div_video.addEventListener("drop", function(event){
    let rect = canvas_video.getBoundingClientRect()
    let x = event.clientX - rect.left + scrollX
    let y = event.clientY - rect.top + scrollY
    radar_drag.setAttribute("style", "z-index:20; position:absolute;"  
            + "top:" + Math.trunc(y-radar_drag.offsetHeight/2) + "px;" + 
            "left:" + Math.trunc(x-radar_drag.offsetWidth/2) + "px")
    div_video.appendChild(radar_drag)
    radar_drag.point_radar = {"x" : x , "y" : y}
    canvas_video.radar = radar_drag
    canvas_video.addEventListener("mousemove", dessiner_vecteur_mouvement)
    canvas_video.addEventListener("click", placer_vecteur)
    })

function dessiner_autres_vecteurs(radar){
    ctx_canvas_video.clearRect(0, 0, canvas_video.width, canvas_video.height)
    for (let autre_radar of liste_radars){
        if (autre_radar != radar && autre_radar.vecteur != null &&
            div_video.contains(autre_radar)){
            tracer_fleche(autre_radar.point_radar, 
            {"x" : autre_radar.vecteur["x"] + autre_radar.point_radar["x"], 
            "y" : autre_radar.vecteur["y"] + autre_radar.point_radar["y"]}, 
            rayon,  autre_radar.couleur)
        }
    }
}

function dessiner_vecteur_mouvement(event){
    let radar = canvas_video.radar
    dessiner_autres_vecteurs(radar)
    let rect = canvas_video.getBoundingClientRect()
    let x = event.clientX - rect.left + scrollX
    let y = event.clientY - rect.top + scrollY
    radar.vecteur = {"x" : x - radar.point_radar["x"], 
        "y" : y - radar.point_radar["y"]}
    tracer_fleche(radar.point_radar, {"x" : x , "y" : y}, rayon,  radar.couleur)
}

function placer_vecteur(event){
    let radar = canvas_video.radar
    let rect = canvas_video.getBoundingClientRect()
    let x = event.clientX - rect.left + scrollX
    let y = event.clientY - rect.top + scrollY
    radar.vecteur = {"x" : x - radar.point_radar["x"], 
        "y" : y - radar.point_radar["y"]}
    tracer_fleche(radar.point_radar, {"x" : x , "y" : y}, rayon,  radar.couleur)
    let div_distance_vecteur= document.createElement("div")
    div_distance_vecteur.classList.add("div_distance_vecteur")
    div_distance_vecteur.setAttribute("style", "z-index:30; position:absolute;"  
        + "top:" + (radar.point_radar["y"] + y)/2 
        + "px; left:" + (radar.point_radar["x"] + x)/2 + "px")
    radar.div_distance_vecteur = div_distance_vecteur
    let checkbox_distance_vecteur = document.createElement("input")
    checkbox_distance_vecteur.setAttribute("type", "checkbox")
    let input_distance_vecteur = document.createElement("input")
    input_distance_vecteur.setAttribute("type", "number")
    input_distance_vecteur.setAttribute("placeholder", "long. (m)")
    
    div_distance_vecteur.appendChild(input_distance_vecteur)
    div_distance_vecteur.appendChild(checkbox_distance_vecteur)

    div_video.appendChild(div_distance_vecteur)

    checkbox_distance_vecteur.addEventListener("change", function(){
        if (checkbox_distance_vecteur.checked){
            input_distance_vecteur.disabled = true
            radar.distance_vecteur = parseInt(input_distance_vecteur.value)
        }
        else {
            input_distance_vecteur.disabled = false
            radar.distance_vecteur = null
        }
    })
    canvas_video.removeEventListener("mousemove", dessiner_vecteur_mouvement)
    canvas_video.removeEventListener("click", placer_vecteur)
}

div_dessiner_rectangle_max.addEventListener("click", function(){
    ctx_canvas_video.couleur_rectangle = "darkorange"
    canvas_video.url = "/envoyer_rectangle_max"
    canvas_video.addEventListener("click", placer_premier_point)
})

div_dessiner_rectangle_min.addEventListener("click", function(){
    ctx_canvas_video.couleur_rectangle = "orange"
    canvas_video.url = "/envoyer_rectangle_min"
    canvas_video.addEventListener("click", placer_premier_point)
})

function placer_premier_point(event){
    let rect = canvas_video.getBoundingClientRect()
    x1 = event.clientX - rect.left + scrollX
    y1 = event.clientY - rect.top + scrollY
    canvas_video.addEventListener("mousemove", dessiner_rectangle)
    canvas_video.addEventListener("click", retirer_events)
    canvas_video.removeEventListener("click", placer_premier_point)
}

function dessiner_rectangle(event){
    ctx_canvas_video.clearRect(0, 0, canvas_video.width, canvas_video.height)
    let rect = canvas_video.getBoundingClientRect()
    x2 = event.clientX - rect.left + scrollX
    y2 = event.clientY - rect.top + scrollY
    ctx_canvas_video.lineWidth = "3"
    ctx_canvas_video.strokeStyle = ctx_canvas_video.couleur_rectangle
    ctx_canvas_video.strokeRect(x1, y1, x2 - x1, y2 - y1)
}

function retirer_events(event){
    ctx_canvas_video.clearRect(0, 0, canvas_video.width, canvas_video.height)
    canvas_video.removeEventListener("mousemove", dessiner_rectangle)
    canvas_video.removeEventListener("click", retirer_events)
    envoyer_rectangle_limite(canvas_video.url)
}

function tracer_fleche(base, pointe, rayon, couleur) {
    //https://gist.github.com/jwir3/d797037d2e1bf78a9b04838d73436197
    let angle;
    let x;
    let y;
    ctx_canvas_video.beginPath()
    ctx_canvas_video.strokeStyle = couleur
    ctx_canvas_video.fillStyle = couleur
    ctx_canvas_video.moveTo(base["x"], base["y"])
    ctx_canvas_video.lineTo(pointe["x"], pointe["y"])
    ctx_canvas_video.stroke()
    angle = Math.atan2(pointe["y"] - base["y"], pointe["x"] - base["x"])
    x = rayon*Math.cos(angle) + pointe["x"];
    y = rayon*Math.sin(angle) + pointe["y"];
    ctx_canvas_video.moveTo(x, y)

    angle += (1.0/3.0)*(2*Math.PI)
    x = rayon*Math.cos(angle) + pointe["x"];
    y = rayon*Math.sin(angle) + pointe["y"];

    ctx_canvas_video.lineTo(x, y);
    angle += (1.0/3.0)*(2*Math.PI)
    x = rayon*Math.cos(angle) + pointe["x"];
    y = rayon*Math.sin(angle) + pointe["y"];

    ctx_canvas_video.lineTo(x, y);
    ctx_canvas_video.closePath();
    ctx_canvas_video.fill();
}