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
