window.onload = function() {

// Create the application helper and add its render target to the page
let SIZE = 700;
let resizeFactor = SIZE / 500;  // 500 is the galaxy size
let app = new PIXI.Application({ width: SIZE, height: SIZE});
document.getElementById("visualization").appendChild(app.view);

app.stage.scale.set(resizeFactor);
const textures = {};
const playerColors = [0x00AAFF, 0xFFAA00]

function renderTheGalaxy(simulationStep) {
    data[simulationStep].things.forEach((p, index, array) => {
        let sprite;
        if (p.thing_type == "planet") {
            sprite = new PIXI.TilingSprite(textures.planets[index % 3]);
            sprite.anchor.set(0.5);
            sprite.scale.set(0.1);
            if (p.player !== null) {
                sprite.tint = playerColors[0];
            }
        } else {
            sprite = new PIXI.TilingSprite(textures.ships[0]);
            sprite.anchor.set(0.5);
            sprite.scale.set(0.1);
            sprite.tint = playerColors[0];
        }
        sprite.position = {
            x: p.position[0],
            y: p.position[1]
        };
        app.stage.addChild(sprite);
    });
}

function main() {
    let N_STEPS = data.length;
    let DEFAULT_DELAY = 500;  // milliseconds
    var counter = 0;
    let stepInputElem = document.getElementById("step-input");
    let animationControlElem = document.getElementById("animation-control");
    let animationPlaying = true;
    
    function renderStep(n) {
        // Every `DEFAULT_DELAY` milliseconds clear the Galaxy
        // and render the simulation step given by `counter`
        app.stage.removeChildren();
        renderTheGalaxy(n);
        stepInputElem.value = n;
    };

    function play(){
        // Every `DEFAULT_DELAY` milliseconds clear the Galaxy
        // and render the simulation step given by `counter`
        let step = counter % N_STEPS;
        renderStep(step);
        counter++;
    }

    function pause(){
        clearInterval(timer);
        animationControlElem.innerHTML = "&#x23EF; Play";
        animationControlElem.classList.add("btn-success")
        animationControlElem.classList.remove("btn-primary")
    };

    var timer = setInterval(play, DEFAULT_DELAY);
    animationControlElem.onclick = () => {
        if (animationPlaying) {
            animationPlaying = false;
            pause();
        } else {
            animationPlaying = true;
            timer = setInterval(play, DEFAULT_DELAY);
            animationControlElem.innerHTML = "&#x23EF; Pause";
            animationControlElem.classList.remove("btn-success")
            animationControlElem.classList.add("btn-primary")
        }
    };
}

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
loader.onComplete.add(main);

document.getElementById("fullscreen-input").onclick = () => {
    app.view.requestFullscreen();            
};

};