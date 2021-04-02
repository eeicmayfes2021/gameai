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
        this.data_storage = null;
    }

    /**
     * Fill arc.
     * @param {number} x center x
     * @param {number} y center y
     * @param {number} size arc radius
     * @param {string} color arc color
     */
    fillarc(x, y, size, color) {
        this.context.fillStyle = color;
        this.context.beginPath();
        this.context.arc(x, y, size, 0, 2 * Math.PI);
        this.context.closePath();
        this.context.fill();
    }

    /**
     * Clear and write stage.
     */
    clearAndWriteStage() {
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
        this.context.restore();
    }

    /**
     * Rewrite stage with given data.
     * @param {any} data 
     */
    rewriteSituation(data) {
        this.clearAndWriteStage();
        if(data === null) return;
        Object.values(data.stones).forEach((stone) => {
            this.context.beginPath();
            if(stone.camp === 'you') this.context.fillStyle = 'red';
            else this.context.fillStyle = 'blue';
            this.context.arc(stone.x, this.canvas.height - stone.y, stone.radius, 0, 2 * Math.PI);
            this.context.fill();
        });
    }

    /**
     * Draw pointer.
     * @param {number} theta 
     * @param {number} velocity 
     */
    writePointer(theta, velocity) {
        this.rewriteSituation(this.data_storage);//再描写（いい方法があれば変えたい…）
        const length = velocity * (velocity/FRICTION) / 2;
        this.context.lineWidth = 5;
        const endx = this.canvas.width/2 + length * Math.cos(theta*(Math.PI/180));
        const endy = this.canvas.height - length * Math.sin(theta*(Math.PI/180));
        this.context.beginPath();
        this.context.moveTo(this.canvas.width/2, this.canvas.height);
        this.context.lineTo(endx, endy);
        this.context.closePath();
        this.context.stroke();
        this.context.lineWidth = 10;
    }
    
    /**
     * Update data storage.
     * @param {any} data 
     */
    updateDataStorage(data) {
        this.data_storage = data;
    }
}