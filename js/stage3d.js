import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const FRICTION = 0.01;

/**
 * 注意 : Stage2D とは座標系が異なるため、x の値を反転させている。
 */
export class Stage3D {
    /**
     * Initialize Stage2D.
     * @param {number} stageWidth
     * @param {number} stageHeight
     * @param {string} appendTo
     */
    constructor(stageWidth, stageHeight, appendTo) {
        this.scene = new THREE.Scene();
        this.stageSize = new THREE.Vector2(stageWidth, stageHeight);
        
        this._constructStage();
        
        this._setupPointer();
        
        /** @type {HTMLCanvasElement} */
        // @ts-ignore
        this.canvas = document.getElementById(appendTo);
        
        this.camera = new THREE.PerspectiveCamera(75, this.canvas.clientWidth / this.canvas.clientHeight, 10, 10000);
        this.camera.position.set(-this.stageSize.x / 2, 400, -250);
        
        this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true });
        this.renderer.setPixelRatio(window.devicePixelRatio);
        
        this.controls = new OrbitControls(this.camera, this.canvas);
        this.controls.target = new THREE.Vector3(-this.stageSize.x / 2, 0, this.stageSize.y / 2);

        this.stones = [];
        
        this._render();
    }
    
    _constructStage() {
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
    
    _setupPointer() {
        const material = new THREE.LineBasicMaterial({ color: 0x0000ff });
        //TODO: remove magic number (15)
        const points = [
            new THREE.Vector3(0, 0, 0),
            new THREE.Vector3(-1, 0, 0)
        ];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        this.line = new THREE.Line(geometry, material);    
        this.line.position.x = -this.stageSize.x / 2;
        this.line.position.y = 15;
        
        this.scene.add(this.line);
    }
    
    _render() {
        requestAnimationFrame(() => { this._render(); });
        
        if (this._resizeRendererToDisplaySize()) {
            this.camera.aspect = this.canvas.clientWidth / this.canvas.clientHeight;
            this.camera.updateProjectionMatrix();
        }
        
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Update Stones' positions.
     * @param {any} data 
     */
    updateStones(data) {
        if(data === null) return;

        data.stones.forEach((stone, i) => {
            if(i < this.stones.length) {
                this.stones[i].position.set(-stone.x, 20, stone.y);
            }else {
                this._instantiateStone(
                    stone.radius, stone.camp, -stone.x, stone.y
                );
                
                console.log('stone added!');
            }
        });
    }
    
    /**
     * Instantiate a stone at a given position.
     * @param {number} radius stone radius
     * @param {string} camp stone owner
     * @param {number} x stone position x
     * @param {number} y stone position y
     */
    _instantiateStone(radius, camp, x, y) {
        //TODO: remove magic number (20)
        const newStone = new THREE.Mesh(
            new THREE.CylinderGeometry(radius, radius, 20),
            new THREE.MeshStandardMaterial({ color: camp === 'you' ? 'red': 'blue' })
        );
        newStone.position.set(x, 20, y);

        this.scene.add(newStone);
        this.stones.push(newStone);
    }

    /**
     * Update pointer direction and length.
     * @param {number} theta 
     * @param {number} velocity 
     */
    updatePointer(theta, velocity) {
        this.line.quaternion.setFromAxisAngle(
            new THREE.Vector3(0, 1, 0),
            theta * THREE.MathUtils.DEG2RAD
        );
        
        const length = velocity * (velocity/FRICTION) / 2;
        this.line.scale.setScalar(length);
    }
    
    // 参考 : https://threejsfundamentals.org/threejs/lessons/ja/threejs-responsive.html
    _resizeRendererToDisplaySize() {
        const needResize = this.canvas.width !== this.canvas.clientWidth
                        || this.canvas.height !== this.canvas.clientHeight;
        if (needResize) {
          this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight, false);
        }
        return needResize;
    }
}