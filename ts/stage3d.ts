import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { Reflector } from 'three/examples/jsm/objects/Reflector';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import Stats from 'three/examples/jsm/libs/stats.module';
import { Stone } from './models/common';
import { isPhone } from './helpers/util';

const FRICTION = 0.008;
const STONE_Y = 0;

/**
 * 注意 : Stage2D とは座標系が異なるため、x の値を反転させている。
 */
export class Stage3D {
    private canvas: HTMLCanvasElement;
    private scene: THREE.Scene;
    private renderer: THREE.WebGLRenderer;
    private camera: THREE.PerspectiveCamera;
    private topCamera: THREE.PerspectiveCamera;
    private useTopCamera: boolean = false;
    // private controls: OrbitControls;
    private stageSize: THREE.Vector2;
    private stones: THREE.Object3D[];
    private line: THREE.Line;
    private skybox: THREE.Texture;
    
    private stats: Stats;

    private stoneRedModel?: THREE.Object3D;
    private stoneBlueModel?: THREE.Object3D;
    
    private isIntro: boolean;
    private onIntroEnd?: () => any;
    private rotated: number = 0;

    /**
     * Initialize Stage2D.
     */
    constructor(stageWidth: number, stageHeight: number, appendTo: string) {
        this.scene = new THREE.Scene();
        this.stageSize = new THREE.Vector2(stageWidth, stageHeight);
        
        this.skybox = this.setupSkybox();
        // this.scene.background = this.skybox;

        this.constructStage(!isPhone());
        
        this.line = this.setupPointer();
        
        this.canvas = document.getElementById(appendTo) as HTMLCanvasElement;
        
        this.camera = new THREE.PerspectiveCamera(75, this.canvas.clientWidth / this.canvas.clientHeight, 10, 10000);
        this.camera.position.set(-this.stageSize.x / 2, 600, -950);
        this.camera.lookAt(-this.stageSize.x / 2, 600, this.stageSize.y / 2);
        
        this.topCamera = new THREE.PerspectiveCamera(75, this.canvas.clientWidth / this.canvas.clientHeight, 10, 10000);
        this.topCamera.position.set(-this.stageSize.x / 2, 800, this.stageSize.y / 2);
        this.topCamera.rotation.set(Math.PI / 2, Math.PI, 0);
        
        this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true });
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        
        // this.controls = new OrbitControls(this.camera, this.canvas);
        // this.controls.target = new THREE.Vector3(-this.stageSize.x / 2, 0, this.stageSize.y / 2);

        this.stones = [];
        
        this.stats = Stats();
        this.stats.showPanel(0);
        this.stats.dom.style.top = 'auto';
        this.stats.dom.style.bottom = '120';
        document.body.appendChild(this.stats.dom);
        
        this.isIntro = false;
        
        this.setupModels().then((_) => this.render());
    }
    
    private constructStage(isPC: boolean, useShadow: boolean = false) {
        const loader = new THREE.TextureLoader();
        const gltfLoader = new GLTFLoader();
        
        const background = isPC ? '/dist/models/background.glb'
            : '/dist/models/background_nolight.glb';
        gltfLoader.loadAsync(background).then((gltf) => {
            const model = gltf.scene;
            model.scale.setScalar(100);
            model.rotateY(-Math.PI / 2);
            this.scene.add(model);
        });

        const base = new THREE.Mesh(
            new THREE.PlaneGeometry(this.stageSize.x, this.stageSize.y),
            new THREE.MeshPhongMaterial({
                map: loader.load('/dist/board.png'),
                transparent: isPC,
                opacity: 0.7
            })
        );
        base.quaternion.setFromAxisAngle(new THREE.Vector3(1, 0, 0), -Math.PI / 2);
        base.position.x = - this.stageSize.x / 2;
        base.position.z = this.stageSize.y / 2;
        base.receiveShadow = true;
        this.scene.add(base);
        
        if(isPC) {
            const ref = new Reflector(
                new THREE.PlaneGeometry(this.stageSize.x, this.stageSize.y),
                {
                    textureWidth: window.innerWidth * window.devicePixelRatio,
                    textureHeight: window.innerHeight * window.devicePixelRatio
                }
            );
            
            ref.position.x = - this.stageSize.x / 2;
            ref.position.z = this.stageSize.y / 2;
            ref.position.y = -1;
            ref.quaternion.setFromAxisAngle(new THREE.Vector3(1, 0, 0), -Math.PI / 2);
            
            this.scene.add(ref);
        }
        
        const light = new THREE.DirectionalLight(0xffffff, 2);
        light.position.set(400, 500, 300);
        light.target.position.set(-this.stageSize.x / 2, 0, this.stageSize.y / 2);

        if(useShadow) {
            light.castShadow = true;
            light.shadow.camera.near = 10;
            light.shadow.camera.far = 1500;
            light.shadow.camera.left = -600;
            light.shadow.camera.right = 600;
            light.shadow.camera.top = 300;
            light.shadow.camera.bottom = -300;
        }

        if(!isPC) {
            this.scene.add(light);
            this.scene.add(light.target);
        }
        
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
        line.visible = false;
        
        this.scene.add(line);
        
        return line;
    }
    
    private setupSkybox(): THREE.Texture {
        const loader = new THREE.CubeTextureLoader();
        const urls = [
            '/dist/skybox/px.jpg', '/dist/skybox/nx.jpg',
            '/dist/skybox/py.jpg', '/dist/skybox/ny.jpg',
            '/dist/skybox/pz.jpg', '/dist/skybox/nz.jpg',
        ];
        const texture = loader.load(urls);
        texture.mapping = THREE.CubeReflectionMapping;
        return texture;
    }

    private async setupModels() {
        const loader = new GLTFLoader();
        const textureLoader = new THREE.TextureLoader();
        
        const fakeShadow = new THREE.Mesh(
            new THREE.PlaneGeometry(50, 50),
            new THREE.MeshBasicMaterial({
                map: textureLoader.load('/dist/roundshadow.png'),
                transparent: true,
                depthWrite: false
            })
        );
        fakeShadow.position.y = 0.1;
        fakeShadow.quaternion.setFromAxisAngle(new THREE.Vector3(1, 0, 0), -Math.PI / 2);

        const paths = [
            '/dist/models/stone-red.glb',
            '/dist/models/stone-blue.glb'
        ];
        
        const promises = paths.map(async (path) => {
            const gltf = await loader.loadAsync(path);
            const model = gltf.scene;

            // TODO: remove setScalar
            model.scale.setScalar(1.5);
            model.traverse((object) => {
                if(object instanceof THREE.Mesh) {
                    object.castShadow = true;
                    
                    if(object.material instanceof THREE.MeshStandardMaterial) {
                        object.material.envMap = this.skybox;
                    }
                }
            });
            model.children.push(fakeShadow);
            
            return model;
        });
        
        [this.stoneRedModel, this.stoneBlueModel] = await Promise.all(promises);
    }
    
    private render() {
        requestAnimationFrame(() => { this.render(); });
        
        const camera = this.useTopCamera ? this.topCamera : this.camera;

        if (this.resizeRendererToDisplaySize()) {
            camera.aspect = this.canvas.clientWidth / this.canvas.clientHeight;
            camera.updateProjectionMatrix();
        }
        
        if(this.isIntro) {
            this.intro();
        }
        
        this.stats.update();
        // this.controls.update();
        this.renderer.render(this.scene, camera);
    }
    
    startIntro(onEnd: () => any) {
        this.isIntro = true;
        this.onIntroEnd = onEnd;
    }
    
    private intro() {
        if(this.rotated > 30) {
            this.isIntro = false;
            this.onIntroEnd?.();
        }

        this.camera.rotateX(-1 * THREE.MathUtils.DEG2RAD);
        this.camera.translateZ(-20);
        this.rotated += 1;
    }
    
    changeCamera() {
        this.useTopCamera = !this.useTopCamera;
    }

    /**
     * Update Stones' positions.
     */
    updateStones(stones: Stone[]) {
        // restart
        if(stones.length < this.stones.length) {
            this.removeStones();
        }

        stones.forEach((stone, i) => {
            if(i < this.stones.length) {
                this.stones[i].position.set(-stone.x, STONE_Y, stone.y);
            }else {
                this.instantiateStone(stone);
                
                console.log('stone added!');
            }
        });
    }
    
    /**
     * Remove all stones.
     */
    removeStones() {
        this.stones.forEach((stone) => this.scene.remove(stone));
        this.stones = [];
    }
    
    private instantiateStone(stone: Stone) {
        const model = stone.camp === 'you' ? this.stoneRedModel : this.stoneBlueModel;
        if(!model) {
            console.error('model not loaded');
            return;
        }
        const newStone = model.clone(true);
        newStone.position.set(-stone.x, STONE_Y, stone.y);

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
    
    enablePointer(enable: boolean) {
        this.line.visible = enable;
    }
    
    // 参考 : https://threejsfundamentals.org/threejs/lessons/ja/threejs-responsive.html
    private resizeRendererToDisplaySize() {
        const [width, height] = [window.innerWidth, window.innerHeight];

        const needResize = this.canvas.width !== width || this.canvas.height !== height;
        if (needResize) {
            this.renderer.setSize(width, height, false);
        }
        return needResize;
    }
}