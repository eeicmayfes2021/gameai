interface Handler { (): void };

class KeyBoardHelper {
    private listeners = new Map<string, Handler[]>();
    
    constructor() {
        document.addEventListener('keydown', this.handleEvents.bind(this));
    }

    addListener(key: string, handler: Handler) {
        const target = this.listeners.get(key);

        if(target) target.push(handler);
        else       this.listeners.set(key, [handler]);
    }
    
    private handleEvents(event: KeyboardEvent) {
        const targets = this.listeners.get(event.key);
        if(!targets) return;

        targets.forEach(f => f());
        event.preventDefault();
    }
}

export const keyBoardHelper = new KeyBoardHelper();