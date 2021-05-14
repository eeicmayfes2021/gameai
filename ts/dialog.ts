export class ResultDialog {
    private container: HTMLElement;
    private title: HTMLElement;
    private content: HTMLElement;
    private sharebutton: HTMLAnchorElement;
    
    constructor(onReturn: () => any, onRestart: () => any) {
        // /dist/main.js は body の最後で読み込まれるので、これらの要素は存在すると仮定
        // （class として作っているのに動的に生成しないのはおかしいのだが…）
        this.container = document.getElementById('dialog-container')!;
        this.title = document.getElementById('dialog-title')!;
        this.content = document.getElementById('dialog-content')!;
        this.sharebutton = document.getElementById('dialog-sharebutton') as HTMLAnchorElement;
        
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

    show(win: boolean, score: number, ifmodelon: boolean, model_epoch: number) {
        if(win) {
            this.title.innerText = 'Win!';
            this.content.innerText = `${score}点であなたの勝ちです！`;
            this.sharebutton.href = `http://twitter.com/share?url=${encodeURIComponent('https://2021.eeic.jp/')}&text=${encodeURIComponent(`${ifmodelon ? model_epoch + "回学習した" : "学習前の" }ゲームAIに${score}点で勝った！`)}&hashtags=${encodeURIComponent('eeic_gameai,電気の展覧会')}`
        }else {
            this.title.innerText = 'Lose!';
            this.content.innerText = `${score}点であなたの負けです！`;
            this.sharebutton.href = `http://twitter.com/share?url=${encodeURIComponent('https://2021.eeic.jp/')}&text=${encodeURIComponent(`${ifmodelon ? model_epoch + "回学習した" : "学習前の" }ゲームAIに${score}点で負けた…`)}&hashtags=${encodeURIComponent('eeic_gameai,電気の展覧会')}`
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
