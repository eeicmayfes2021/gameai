import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { Reflector } from 'three/examples/jsm/objects/Reflector';
import { Stone } from './models/common';
import { isPhone } from './helpers/util';

const FRICTION = 0.008;
const STONE_Y = 10;

/**
 * 注意 : Stage2D とは座標系が異なるため、x の値を反転させている。
 */
export class Stage3D {
    private canvas: HTMLCanvasElement;
    private scene: THREE.Scene;
    private renderer: THREE.WebGLRenderer;
    private camera: THREE.PerspectiveCamera;
    private controls: OrbitControls;
    private stageSize: THREE.Vector2;
    private stones: THREE.Object3D[];
    private line: THREE.Line;
    private skybox: THREE.Texture;

    /**
     * Initialize Stage2D.
     */
    constructor(stageWidth: number, stageHeight: number, appendTo: string) {
        this.scene = new THREE.Scene();
        this.stageSize = new THREE.Vector2(stageWidth, stageHeight);
        
        this.skybox = this.setupSkybox();
        this.scene.background = this.skybox;

        this.constructStage();
        
        this.line = this.setupPointer();
        
        this.canvas = document.getElementById(appendTo) as HTMLCanvasElement;
        
        this.camera = new THREE.PerspectiveCamera(75, this.canvas.clientWidth / this.canvas.clientHeight, 10, 10000);
        this.camera.position.set(-this.stageSize.x / 2, 400, -250);
        
        this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true });
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        
        this.controls = new OrbitControls(this.camera, this.canvas);
        this.controls.target = new THREE.Vector3(-this.stageSize.x / 2, 0, this.stageSize.y / 2);

        this.stones = [];
        
        this.render();
    }
    
    private constructStage() {
        const loader = new THREE.TextureLoader();

        const base = new THREE.Mesh(
            new THREE.PlaneGeometry(this.stageSize.x, this.stageSize.y),
            new THREE.MeshPhongMaterial({
                map: loader.load('/dist/board.png'),
                transparent: true,
                opacity: 0.5
            })
        );
        base.quaternion.setFromAxisAngle(new THREE.Vector3(1, 0, 0), -Math.PI / 2);
        base.position.x = - this.stageSize.x / 2;
        base.position.z = this.stageSize.y / 2;
        base.receiveShadow = true;
        this.scene.add(base);
        
        const ref = new Reflector(
            new THREE.PlaneGeometry(this.stageSize.x, this.stageSize.y),
            { }
        );
        
        ref.position.x = - this.stageSize.x / 2;
        ref.position.z = this.stageSize.y / 2;
        ref.position.y = -1;
        ref.quaternion.setFromAxisAngle(new THREE.Vector3(1, 0, 0), -Math.PI / 2);
        
        this.scene.add(ref);
        
        const light = new THREE.DirectionalLight(0xffffff, 1);
        light.position.set(400, 500, 300);
        light.target.position.set(-this.stageSize.x / 2, 0, this.stageSize.y / 2);

        light.castShadow = true;
        light.shadow.camera.near = 10;
        light.shadow.camera.far = 1500;
        light.shadow.camera.left = -600;
        light.shadow.camera.right = 600;
        light.shadow.camera.top = 300;
        light.shadow.camera.bottom = -300;

        this.scene.add(light);
        this.scene.add(light.target);
        
        const ambient = new THREE.AmbientLight(0xffffff, 0.3);
        this.scene.add(ambient);
    }
    
    private setupPointer(): THREE.Line {
        const material = new THREE.LineBasicMaterial({ color: 0x0000ff });
        //TODO: remove magic number (15)
        const points = [
            new THREE.Vector3(0, 0, 0),
            new THREE.Vector3(-1, 0, 0)
        ];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const line = new THREE.Line(geometry, material);    
        line.position.x = -this.stageSize.x / 2;
        line.position.y = 15;
        
        this.scene.add(line);
        
        return line;
    }
    
    private setupSkybox(): THREE.Texture {
        const loader = new THREE.CubeTextureLoader();
        const urls = [
            '/dist/skybox/px.png', '/dist/skybox/nx.png',
            '/dist/skybox/py.png', '/dist/skybox/ny.png',
            '/dist/skybox/pz.png', '/dist/skybox/nz.png',
        ];
        const texture = loader.load(urls);
        texture.mapping = THREE.CubeReflectionMapping;
        return texture;
    }
    
    private render() {
        requestAnimationFrame(() => { this.render(); });
        
        if (this.resizeRendererToDisplaySize()) {
            this.camera.aspect = this.canvas.clientWidth / this.canvas.clientHeight;
            this.camera.updateProjectionMatrix();
        }
        
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Update Stones' positions.
     */
    updateStones(stones: Stone[]) {
        stones.forEach((stone, i) => {
            if(i < this.stones.length) {
                this.stones[i].position.set(-stone.x, STONE_Y, stone.y);
            }else {
                this.instantiateStone(stone);
                
                console.log('stone added!');
            }
        });
    }
    
    private instantiateStone(stone: Stone) {
        const newStone = new THREE.Mesh(
            new THREE.CylinderGeometry(stone.radius, stone.radius, 20),
            new THREE.MeshPhongMaterial({
                color: stone.camp === 'you' ? 'red': 'blue',
                envMap: this.skybox,
                combine: THREE.MixOperation,
                reflectivity: 0.5
            })
        );
        newStone.position.set(-stone.x, STONE_Y, stone.y);
        newStone.castShadow = true;
        newStone.receiveShadow = true;

        this.scene.add(newStone);
        this.stones.push(newStone);
    }

    /**
     * Update pointer direction and length.
     */
    updatePointer(theta: number, velocity: number) {
        this.line.quaternion.setFromAxisAngle(
            new THREE.Vector3(0, 1, 0),
            theta * THREE.MathUtils.DEG2RAD
        );
        
        const length = velocity * (velocity/FRICTION) / 2;
        this.line.scale.setScalar(length);
    }
    
    // 参考 : https://threejsfundamentals.org/threejs/lessons/ja/threejs-responsive.html
    private resizeRendererToDisplaySize() {
        const [width, height] = isPhone()
            ? [window.innerWidth, window.innerHeight]
            : [this.canvas.clientWidth, this.canvas.clientHeight];

        const needResize = this.canvas.width !== width || this.canvas.height !== height;
        if (needResize) {
            this.renderer.setSize(width, height, false);
        }
        return needResize;
    }
}