import { Stone } from './models/common';

const FRICTION = 0.008;

/** タッチ開始点との最大距離 */
const EPSILON = 40;

/** フリック距離と投射距離の比 */
const FLICK_RATIO = 2;

export class Stage2D {
    private canvas: HTMLCanvasElement;
    private context: CanvasRenderingContext2D;
    private pointerX: number;
    private pointerY: number;
    private stones: Stone[];
    private touching: boolean;

    /**
     * Initialize Stage2D.
     */
    constructor(canvasId: string, private onFlick?: (theta: number, velocity: number) => void) {
        this.canvas = document.getElementById(canvasId) as HTMLCanvasElement;
        
        this.context = this.canvas.getContext('2d')!;
        
        this.canvas.addEventListener('touchstart', (e) => this.onTouchStart(e));
        this.canvas.addEventListener('touchmove', (e) => this.onTouchMove(e));
        this.canvas.addEventListener('touchend', (e) => this.onTouchEnd(e));
        
        this.stones = [];
        this.touching = false;
        this.pointerX = this.pointerY = 0;
    }

    private drawBase() {
        this.context.save();
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.context.lineWidth = 10;
        this.context.beginPath();
        this.context.rect(0, 0, this.canvas.width, this.canvas.height);
        this.context.closePath();
        this.context.stroke(); 
        this.fillarc(this.canvas.width / 2, this.canvas.height / 2, 250, 'darkblue');
        this.fillarc(this.canvas.width / 2, this.canvas.height / 2, 200, 'white');
        this.fillarc(this.canvas.width / 2, this.canvas.height / 2, 100, 'brown');
        this.fillarc(this.canvas.width / 2, this.canvas.height / 2, 50, 'white');
        this.fillarc(this.canvas.width / 2, this.canvas.height, EPSILON, 'gray');
        this.context.restore();
    }
    
    private drawStones() {
        this.stones.forEach((stone) => {
            this.context.beginPath();
            this.context.fillStyle = (stone.camp === 'you') ? 'red' : 'blue';
            this.context.arc(stone.x, this.canvas.height - stone.y, stone.radius, 0, 2 * Math.PI);
            this.context.fill();
        });
    }
    
    private drawPointer() {
        const startX = this.canvas.width / 2;
        const startY = this.canvas.height;

        this.context.lineWidth = 5;
        this.context.beginPath();
        this.context.moveTo(startX, startY);
        this.context.lineTo(startX + this.pointerX, startY + this.pointerY);
        this.context.closePath();
        this.context.stroke();
        this.context.lineWidth = 10;
    }
    
    private drawStage() {
        this.drawBase();
        this.drawStones();
        //this.drawPointer();
    }
    
    private onTouchStart(e: TouchEvent) {
        if(e.changedTouches.length !== 1) return;
        
        const [x, y] = this.getRelativePos(e.changedTouches[0]);
        const startX = this.canvas.width / 2;
        const startY = this.canvas.height;
        
        if((x - startX)**2 + (y - startY)**2 > EPSILON**2) return;
        
        this.touching = true;
        
        console.log('touch start');
    }
    
    private onTouchMove(e: TouchEvent) {
        if(!this.touching) return;
        
        e.preventDefault();
    }
    
    private onTouchEnd(e: TouchEvent) {
        if(!this.touching) return;
        
        if(e.changedTouches.length !== 1) return;

        const [x, y] = this.getRelativePos(e.changedTouches[0]);
        const startX = this.canvas.width / 2;
        const startY = this.canvas.height;
        
        const dx = (x - startX) * FLICK_RATIO;
        const dy = (y - startY) * FLICK_RATIO;

        const theta = Math.atan2(dy, dx) * (180 / Math.PI);
        const length = Math.sqrt(dx**2 + dy**2);
        const velocity = Math.sqrt(length * 2 * FRICTION);    
        
        this.onFlick?.(theta, velocity);
        
        this.touching = false;
        
        console.log('touch end');
    }

    /**
     * Update Stones' positions.
     */
    updateStones(stones: Stone[]) {
        this.stones = stones;

        this.drawStage();
    }

    /**
     * Update pointer direction and length.
     */
    updatePointer(theta: number, velocity: number) {
        const radTheta = theta * (Math.PI / 180);
        const length = velocity * (velocity/FRICTION) / 2;

        this.pointerX = length * Math.cos(radTheta);
        this.pointerY = -length * Math.sin(radTheta);

        this.drawStage();
    }
    
    private fillarc(x: number, y: number, size: number, color: string) {
        this.context.fillStyle = color;
        this.context.beginPath();
        this.context.arc(x, y, size, 0, 2 * Math.PI);
        this.context.closePath();
        this.context.fill();
    }
    
    private getRelativePos(e: Touch): [number, number] {
        const x = e.clientX - this.canvas.getBoundingClientRect().left;
        const y = e.clientY - this.canvas.getBoundingClientRect().top;
        
        const ratio = this.canvas.width / this.canvas.clientWidth;
        
        return [x * ratio, y * ratio];
    }
}