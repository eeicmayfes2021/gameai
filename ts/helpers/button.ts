const HOLD_TIME = 200;
const INTERVAL = 100;
const HOVER_CLASS = 'button-hover';

interface Listener { (): void };

export const addIntervalListener = (target: HTMLElement, listener: Listener) => {
    let handler: number;
    target.addEventListener('click', (event) => {
        event.preventDefault();
        listener();
    });
    target.addEventListener('touchstart', (event) => {
        event.preventDefault();
        target.classList.add(HOVER_CLASS);
        listener();
        let time = 0;
        handler = window.setInterval(() => {
            time += INTERVAL;
            if(time >= HOLD_TIME) listener();
        }, INTERVAL);
    });
    target.addEventListener('touchend', (event) => {
        event.preventDefault();
        target.classList.remove(HOVER_CLASS);
        window.clearInterval(handler);
    });
};