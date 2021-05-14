export class ResultDialog {
    private container: HTMLElement;
    private title: HTMLElement;
    private content: HTMLElement;
    
    constructor(onReturn: () => any, onRestart: () => any) {
        // /dist/main.js は body の最後で読み込まれるので、これらの要素は存在すると仮定
        // （class として作っているのに動的に生成しないのはおかしいのだが…）
        this.container = document.getElementById('dialog-container')!;
        this.title = document.getElementById('dialog-title')!;
        this.content = document.getElementById('dialog-content')!;
        
        const returnButton = document.getElementById('button-return')!;
        returnButton.addEventListener('click', (_) => {
            this.hide();
            onReturn();
        });

        const restartButton = document.getElementById('button-restart')!;
        restartButton.addEventListener('click', (_) => {
            this.hide();
            onRestart();
        });
    }

    show(win: boolean, score: number) {
        if(win) {
            this.title.innerText = 'Win!';
            this.content.innerText = `${score}点であなたの勝ちです！`;
        }else {
            this.title.innerText = 'Lose!';
            this.content.innerText = `${score}点であなたの負けです！`;
        }
        this.container.style.display = 'flex';
    }

    hide() {
        this.container.style.display = 'none';
    }
}

export class SelectDialog {
    private container: HTMLElement;
    private title: HTMLElement;
    private content: HTMLElement;
    
    constructor(onSelecton: () => any, onSelectoff: () => any) {
        // /dist/main.js は body の最後で読み込まれるので、これらの要素は存在すると仮定
        // （class として作っているのに動的に生成しないのはおかしいのだが…）
        this.container = document.getElementById('dialog-container2')!;
        this.title = document.getElementById('dialog-title2')!;
        this.content = document.getElementById('dialog-content2')!;
        
        const  onButton = document.getElementById('button-on')!;
        onButton.addEventListener('click', (_) => {
            this.hide();
            onSelecton();
        });

        const offButton = document.getElementById('button-off')!;
        offButton.addEventListener('click', (_) => {
            this.hide();
            onSelectoff();
        });
    }

    show() {
        this.container.style.display = 'flex';
    }

    hide() {
        this.container.style.display = 'none';
    }
}

export class GraphDialog {
    private container: HTMLElement;
    
    constructor() {
        // /dist/main.js は body の最後で読み込まれるので、これらの要素は存在すると仮定
        // （class として作っているのに動的に生成しないのはおかしいのだが…）
        this.container = document.getElementById('graph-container')!;
        
        const  hideButton = document.getElementById('button-graph-back')!;
        hideButton.addEventListener('click', (_) => {
            this.hide();
        });
        const  showButton = document.getElementById('button-graph')!;
        showButton.addEventListener('click', (_) => {
            this.show();
        });
    }

    show() {
        this.container.style.display = 'flex';
    }

    hide() {
        this.container.style.display = 'none';
    }
}
