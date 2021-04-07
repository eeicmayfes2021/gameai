const FRICTION = 0.01;

/** タッチ開始点との最大距離 */
const EPSILON = 40;

/** フリック距離と投射距離の比 */
const FLICK_RATIO = 2;

export class Stage2D {
    /**
     * Initialize Stage2D.
     * @param {string} canvasId 
     * @param {(theta: number, velocity: number) => void} [onFlick]
     */
    constructor(canvasId, onFlick) {
        /** @type {HTMLCanvasElement} */
        this.canvas = document.getElementById(canvasId);
        
        this.context = this.canvas.getContext('2d');
        
        this.canvas.addEventListener('touchstart', (e) => this._onTouchStart(e));
        this.canvas.addEventListener('touchmove', (e) => this._onTouchMove(e));
        this.canvas.addEventListener('touchend', (e) => this._onTouchEnd(e));
        
        this.stones = [];
        this.touching = false;
        this.onFlick = onFlick;
    }

    _drawBase() {
        this.context.save();
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.context.lineWidth = 10;
        this.context.beginPath();
        this.context.rect(0, 0, this.canvas.width, this.canvas.height);
        this.context.closePath();
        this.context.stroke(); 
        this._fillarc(this.canvas.width / 2, this.canvas.height / 2, 250, 'darkblue');
        this._fillarc(this.canvas.width / 2, this.canvas.height / 2, 200, 'white');
        this._fillarc(this.canvas.width / 2, this.canvas.height / 2, 100, 'brown');
        this._fillarc(this.canvas.width / 2, this.canvas.height / 2, 50, 'white');
        this._fillarc(this.canvas.width / 2, this.canvas.height, EPSILON, 'gray');
        this.context.restore();
    }
    
    _drawStones() {
        this.stones.forEach((stone) => {
            this.context.beginPath();
            this.context.fillStyle = (stone.camp === 'you') ? 'red' : 'blue';
            this.context.arc(stone.x, this.canvas.height - stone.y, stone.radius, 0, 2 * Math.PI);
            this.context.fill();
        });
    }
    
    _drawPointer() {
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
    
    _drawStage() {
        this._drawBase();
        this._drawStones();
        //this._drawPointer();
    }
    
    /**
     * Handle touch start.
     * @param {TouchEvent} e event
     */
    _onTouchStart(e) {
        if(e.changedTouches.length !== 1) return;
        
        const [x, y] = this._getRelativePos(e.changedTouches[0]);
        const startX = this.canvas.width / 2;
        const startY = this.canvas.height;
        
        if((x - startX)**2 + (y - startY)**2 > EPSILON**2) return;
        
        this.touching = true;
        
        console.log('touch start');
    }
    
    /**
     * Handle touch move.
     * @param {TouchEvent} e event
     */
    _onTouchMove(e) {
        if(!this.touching) return;
        
        e.preventDefault();
    }
    
    /**
     * Handle touch end.
     * @param {TouchEvent} e event
     */
    _onTouchEnd(e) {
        if(!this.touching) return;
        
        if(e.changedTouches.length !== 1) return;

        const [x, y] = this._getRelativePos(e.changedTouches[0]);
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
     * @param {any} data 
     */
    updateStones(data) {
        this.stones = data?.stones ?? [];

        this._drawStage();
    }

    /**
     * Update pointer direction and length.
     * @param {number} theta 
     * @param {number} velocity 
     */
    updatePointer(theta, velocity) {
        const radTheta = theta * (Math.PI / 180);
        const length = velocity * (velocity/FRICTION) / 2;

        this.pointerX = length * Math.cos(radTheta);
        this.pointerY = -length * Math.sin(radTheta);

        this._drawStage();
    }
    
    /**
     * Fill arc.
     * @param {number} x center x
     * @param {number} y center y
     * @param {number} size arc radius
     * @param {string} color arc color
     */
    _fillarc(x, y, size, color) {
        this.context.fillStyle = color;
        this.context.beginPath();
        this.context.arc(x, y, size, 0, 2 * Math.PI);
        this.context.closePath();
        this.context.fill();
    }
    
    /**
     * @param {Touch} e event
     * @returns {[number, number]}
     */
    _getRelativePos(e) {
        const x = e.clientX - this.canvas.getBoundingClientRect().left;
        const y = e.clientY - this.canvas.getBoundingClientRect().top;
        
        const ratio = this.canvas.width / this.canvas.clientWidth;
        
        return [x * ratio, y * ratio];
    }
}