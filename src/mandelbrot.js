// Find the latest version by visiting https://unpkg.com/ The URL will
// redirect to the newest stable release.
import {
    Mesh,
    PlaneGeometry,
    ShaderMaterial,
    OrthographicCamera,
    Scene,
    WebGLRenderer,
    Vector2
} from 'https://cdn.skypack.dev/three@0.132.2';

var camera, scene, renderer;
var geometry, material, mesh;
var uniforms;
var aspect = window.innerWidth / window.innerHeight;
var dilation = 1.0;

// variables for mouse drag
var isDragging = false;
var previousMousePosition = { x: 0, y: 0 };

function init() {
    setup();

    uniforms = {
        res: {
            type: 'vec2',
            value: new Vector2(window.innerWidth, window.innerHeight)
        },
        aspect: {
            type: 'float',
            value: aspect
        },
        offset: {
            type: 'vec2',
            value: new Vector2(0, 0)
        },
        dilation: {
            type: 'float',
            value: dilation
        }
    };

    geometry = new PlaneGeometry(2, 2);
    material = new ShaderMaterial({
        fragmentShader: fragmentShader(),
        uniforms: uniforms
    });
    mesh = new Mesh(geometry, material);
    scene.add(mesh);
    animate();
}

// event handlers ======================================

// event listeners for mouse drag
document.addEventListener('mousedown', (event) => {
    isDragging = true;
    previousMousePosition = {
        x: event.clientX,
        y: event.clientY
    };
});

document.addEventListener('mouseup', () => {
    isDragging = false;
});

document.addEventListener('mousemove', (event) => {
    if (!isDragging) return;

    const deltaX = 
        (event.clientX - previousMousePosition.x)
        * 0.005 / uniforms.dilation.value;
    const deltaY = 
        (event.clientY - previousMousePosition.y)
        * 0.005 / uniforms.dilation.value;

    // move the view
    uniforms.offset.value.x -= deltaX;
    uniforms.offset.value.y += deltaY;

    // update the previous mouse position
    previousMousePosition = {
        x: event.clientX,
        y: event.clientY
    };
});

// Key press detection
document.addEventListener('keydown', (event) => {
    const keyCode = event.keyCode;

    switch (keyCode) {
        case 49: // '1' key
            uniforms.dilation.value *= 2;
            break;
        case 50: // '2' key
            uniforms.dilation.value /= 2;
            break;
    }
});

// shader ==============================================

function fragmentShader() {
    return `
    precision highp float;
    uniform vec2 res;
    uniform float aspect;
    uniform vec2 offset;
    uniform float dilation;

    float mandelbrot(vec2 c){
        float alpha = 1.0;
        vec2 z = vec2(0.0 , 0.0);

        for(int i=0; i < 200; i++){  // i < max iterations
       
            float x_sq = z.x*z.x;
            float y_sq = z.y*z.y;
            vec2 z_sq = vec2(x_sq - y_sq, 2.0*z.x*z.y);
            z = z_sq + c;

            if(x_sq + y_sq > 4.0){
                alpha = float(i)/200.0;
                break;
            }
        }
    return alpha;
    }
   
    void main(){ // gl_FragCoord in [0,1]
        vec2 uv = 
            4.0 * vec2(aspect, 1.0) * gl_FragCoord.xy / res 
            - 2.0 * vec2(aspect, 1.0);
        float s = mandelbrot((uv / dilation) + offset);

        vec3 coord = vec3(s, s, s);
        gl_FragColor = vec4(pow(coord, vec3(5.0, 5.0, 1.0)), 1.0);
    }
  `
}

// setup ==============================================

function animate() {
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
}

function setup() {
    camera = new OrthographicCamera(-1, 1, 1, -1, -1, 1);
    scene = new Scene();
    renderer = new WebGLRenderer({ antialias: false, precision: 'highp' });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);
}
init();