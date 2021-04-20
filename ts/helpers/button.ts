const HOLD_TIME = 200;
const INTERVAL = 100;

interface Listener { (): void };

export const addIntervalListener = (target: HTMLElement, listener: Listener) => {
    let handler: number;
    target.addEventListener('touchstart', (event) => {
        event.preventDefault();
        listener();
        let time = 0;
        handler = window.setInterval(() => {
            time += INTERVAL;
            if(time >= HOLD_TIME) listener();
        }, INTERVAL);
    });
    target.addEventListener('touchend', (event) => {
        event.preventDefault();
        window.clearInterval(handler);
    });
};