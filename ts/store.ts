import { clamp } from './helpers/util';

const INITIAL_ANGLE = 90;
const INITIAL_VELOCITY = 3;
const ANGLE_STEP = 1;
const VELOCITY_STEP = 0.25;

export class PointerState {
    private _enable = false;
    private _angle = INITIAL_ANGLE;
    private _velocity = INITIAL_VELOCITY;
    
    constructor(
        private onChange?: (angle: number, velocity: number) => void,
        private onEnableChange?: (enable: boolean) => any
    ) {}
    
    get enable(): boolean {
        return this._enable;
    }
    
    get angle(): number {
        return this._angle;
    }
    
    get velocity(): number {
        return this._velocity;
    }

    start() {
        this._enable = true;
        this._angle = INITIAL_ANGLE;
        this._velocity = INITIAL_VELOCITY;        
        this.onEnableChange?.(this._enable);
        this.postProcess();
    }
    
    stop() {
        this._enable = false;
        this.onEnableChange?.(this._enable);
    }

    turnLeft() {
        if(!this._enable) return;

        this._angle += ANGLE_STEP;
        this.postProcess();
    }

    turnRight() {
        if(!this._enable) return;

        this._angle -= ANGLE_STEP;
        this.postProcess();
    }

    strengthen() {
        if(!this._enable) return;

        this._velocity += VELOCITY_STEP;
        this.postProcess();
    }

    weaken() {
        if(!this._enable) return;

        this._velocity -= VELOCITY_STEP;
        this.postProcess();
    }
    
    private postProcess() {
        this._angle = clamp(this._angle, 45, 135);
        this._velocity = clamp(this._velocity, 2, 4);

        this.onChange?.(this._angle, this._velocity);
    }
}
