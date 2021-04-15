const FRICTION = 0.01;

export class Stage2D {
    /**
     * Initialize Stage2D.
     * @param {string} canvasId 
     */
    constructor(canvasId) {
        /** @type {HTMLCanvasElement} */
        this.canvas = document.getElementById(canvasId);

        this.context = this.canvas.getContext('2d');
        
        this.stones = [];
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
        this._drawPointer();
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
}