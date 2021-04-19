import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { Stone } from './models/common';

const FRICTION = 0.008;

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

    /**
     * Initialize Stage2D.
     */
    constructor(stageWidth: number, stageHeight: number, appendTo: string) {
        this.scene = new THREE.Scene();
        this.stageSize = new THREE.Vector2(stageWidth, stageHeight);
        
        this.constructStage();
        
        this.line = this.setupPointer();
        
        this.canvas = document.getElementById(appendTo) as HTMLCanvasElement;
        
        this.camera = new THREE.PerspectiveCamera(75, this.canvas.clientWidth / this.canvas.clientHeight, 10, 10000);
        this.camera.position.set(-this.stageSize.x / 2, 400, -250);
        
        this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true });
        this.renderer.setPixelRatio(window.devicePixelRatio);
        
        this.controls = new OrbitControls(this.camera, this.canvas);
        this.controls.target = new THREE.Vector3(-this.stageSize.x / 2, 0, this.stageSize.y / 2);

        this.stones = [];
        
        this.render();
    }
    
    private constructStage() {
        const loader = new THREE.TextureLoader();

        const base = new THREE.Mesh(
            new THREE.BoxGeometry(this.stageSize.x, 10, this.stageSize.y),
            new THREE.MeshStandardMaterial({
                map: loader.load('/dist/board.png')
            })
        );
        base.position.x = - this.stageSize.x / 2;
        base.position.z = this.stageSize.y / 2;
        this.scene.add(base);
        
        const light = new THREE.DirectionalLight(0xffffff, 1);
        light.position.set(4000, 5000, 3000);
        this.scene.add(light);
        
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
                this.stones[i].position.set(-stone.x, 20, stone.y);
            }else {
                this.instantiateStone(stone);
                
                console.log('stone added!');
            }
        });
    }
    
    private instantiateStone(stone: Stone) {
        //TODO: remove magic number (20)
        const newStone = new THREE.Mesh(
            new THREE.CylinderGeometry(stone.radius, stone.radius, 20),
            new THREE.MeshStandardMaterial({ color: stone.camp === 'you' ? 'red': 'blue' })
        );
        newStone.position.set(-stone.x, 20, stone.y);

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
        const needResize = this.canvas.width !== this.canvas.clientWidth
                        || this.canvas.height !== this.canvas.clientHeight;
        if (needResize) {
          this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight, false);
        }
        return needResize;
    }
}