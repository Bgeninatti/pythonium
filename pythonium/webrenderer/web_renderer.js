// Globals
let SIZE = 700;
let resizeFactor = SIZE / 500;  // 500 is the galaxy size
let playerColors = {};
let app = new PIXI.Application({ width: SIZE, height: SIZE});
document.getElementById("visualization").appendChild(app.view);
app.stage.scale.set(resizeFactor);

function renderTheGalaxy(simulationStep) {
    data.turns[simulationStep].galaxy.things.forEach(
        (thing, index) => {
            let texture = thing.thing_type == "planet"
                ? textures.planets[index % 3]
                : textures.ships[0]
            let sprite = new PIXI.TilingSprite(texture);
            sprite.anchor.set(0.5);
            sprite.scale.set(0.1);
            if (thing.player) {
                sprite.tint = playerColors[thing.player];
            }
            if (thing.thing_type == "planet" && data.turns[simulationStep].explosions.length > 0) {
                let explosion = data.turns[simulationStep].explosions.find(
                    explosion => explosion.ship.position[0] == thing.position[0]
                                && explosion.ship.position[1] == thing.position[1]
                )
                if (explosion) {
                    sprite.scale.set(0.05 * Math.log(explosion.total_attack));
                    sprite.tint = 0xFF0000;
                }

            }
            sprite.position = {
                x: thing.position[0],
                y: thing.position[1]
            };
            app.stage.addChild(sprite);
        });
}

/**
 * CONTROLS
 */

var timer;
let DEFAULT_DELAY = 500;  // milliseconds
var counter = 0; 

let stepInputElem = document.getElementById("step-slider");
let stepLabelElem = document.getElementById("step-label");
let animationControlElem = document.getElementById("animation-control");
let animationPrevElem = document.getElementById("animation-prev");
let animationNextElem = document.getElementById("animation-next");
let animationPlaying = true;

function renderStep(n) {
    app.stage.removeChildren();
    renderTheGalaxy(n);
    stepInputElem.value = n;
    stepLabelElem.innerText = n;
};

function playNext(){
    counter++;
    let step = counter % data.turns.length;
    renderStep(step);
}

function playPrevious(){
    counter--;
    if (counter < 0) {
        counter = data.turns.length - 1;
    }
    let step = counter % data.turns.length;
    renderStep(step);
}

function pause(){
    // el timer global
    clearInterval(timer);
    animationControlElem.innerHTML = "&#x23EF; Play";
    animationControlElem.classList.add("btn-success")
    animationControlElem.classList.remove("btn-primary")
};

animationControlElem.onclick = () => {
    if (animationPlaying) {  // Pause pressed
        animationPlaying = false;
        pause();
    } else {
        animationPlaying = true;
        timer = setInterval(playNext, DEFAULT_DELAY);
        animationControlElem.innerHTML = "&#x23EF; Pause";
        animationControlElem.classList.remove("btn-success")
        animationControlElem.classList.add("btn-primary")
    }
    animationNextElem.disabled = animationPlaying;
    animationPrevElem.disabled = animationPlaying;
};

document.getElementById("fullscreen-input").onclick = () => {
    app.view.requestFullscreen();            
};

animationNextElem.onclick = playNext;
animationPrevElem.onclick = playPrevious;
stepInputElem.onchange = function(e) {
    let step = e.srcElement.value;
    renderStep(step);
    counter = step;
    stepLabelElem.innerText = step;
}



// Create the application helper and add its render target to the page
const textures = {};
const loader = PIXI.Loader.shared;
loader.add('planet01', 'assets/planet01.png');
loader.add('planet02', 'assets/planet02.png');
loader.add('planet03', 'assets/planet03.png');
loader.add('ship01', 'assets/ship01.png');

loader.load((loader, resources) => {
    textures.planets = [
        resources.planet01.texture,
        resources.planet02.texture,
        resources.planet03.texture,
    ];
    textures.ships = [
        resources.ship01.texture,
    ];
});

window.onload = function() {
    document.getElementById("galaxy-name-placeholder").innerText = data.meta.galaxy;

    const colors = [0x00AAFF, 0xFFAA00, 0x03fc0f, 0xbf061b, 0xdb12db, 0x308c0e, 0x1cbed4];
    const colorsStr = ["#00AAFF", "#FFAA00", "#03fc0f", "#bf061b", "#db12db", "#308c0e", "#1cbed4"];

    let botsListElem = document.getElementById("bots-list");
    data.meta.players.forEach((bot, idx) => {
        let i = idx % colors.length;  // As we only have a limited number of colors, they may be reused...
        playerColors[bot] = colors[i];
        var li = document.createElement("li");
        li.innerHTML = "&#9632;" + bot;
        li.style = "color:" + colorsStr[i];
        botsListElem.appendChild(li);
    });

    loader.onComplete.add(() => {
        renderStep(0);
        timer = setInterval(playNext, DEFAULT_DELAY);
    });    
};