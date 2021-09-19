import { io } from 'socket.io-client';
//import { Stage2D } from './stage2d';
import { Stage3D } from './stage3d';
import { PointerState } from './store';
import { keyBoardHelper } from './helpers/keyboard';
import { addIntervalListener } from './helpers/button';
import { MoveStonesMessage, WinMessage, ModelMessage, LeftMessage,XYLIST } from './models/socket';
import { ResultDialog,SelectDialog } from './dialog';
import Chart from 'chart.js';

const socket = io();
//const stage = new Stage2D('canvas-2d', (dx, dy) => onFlick(dx, dy));
const stage = new Stage3D(600, 1000, 'canvas-2d');

const pointerState = new PointerState((angle, velocity) => {
    stage.updatePointer(angle, velocity);
}, (enable) => {
    stage.enablePointer(enable);
});

const resultDialog = new ResultDialog(() => onReturn(), () => onRestart());
const selectDialog = new SelectDialog(() => onSelecton(), () => onSelectoff());
let ifmodelon=true;
let model_epoch = 0;

const onConnect = () => {
    console.log("Connect")
    // do nothing
};

const initialize = () => {
    socket.emit('init');
    console.log("Init")
    selectDialog.show();
};
const onMakeGraph = (data:XYLIST) => {
    //グラフの表示
    //var url="https://0k33okho4j.execute-api.ap-northeast-1.amazonaws.com/api/model"
    const scoregraph = <HTMLCanvasElement> document.getElementById("scoregraph")!;
    const ctx = scoregraph.getContext("2d")!;
    var img = new Image();
    console.log(data.xlist)
    console.log(data.ylist)
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.xlist,
            datasets: [{
                label: 'AIの勝率',
                data: data.ylist,
                borderColor:'rgb(255, 0, 0)',
                backgroundColor:'rgb(255, 0, 0,0.1)',
            }]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero:true
                    }
                }]
            }
        }
    });
};

const onSelecton = () => {
    console.log('gameStart!');
  
    stage.startIntro(() => {
        const data = { model: 'on' };
        socket.emit('game_start', data);
      ifmodelon=true;
    });
};
const onSelectoff = () => {
    console.log('gameStart!');
    
    stage.startIntro(() => {
        const data = { model: 'off' };
        socket.emit('game_start', data);
        ifmodelon=false;
    });
};

const onYourTurn = (data:LeftMessage) => {
    const leftstone = document.getElementById('leftstone')!;
    leftstone.innerHTML = `あと${data.left}回なげられます`;
    pointerState.start();
};

const onMoveStones = (data?: MoveStonesMessage) => {
    stage.updateStones(data?.stones ?? []);
};

const onYouWin = (data: WinMessage) => {
    console.log('you win! score:', data.score);
    changeUIVisibility(false);
    resultDialog.show(true, data.score, ifmodelon, model_epoch);
};

const onAIWin = (data: WinMessage) => {
    console.log('AI win! score:', data.score);
    changeUIVisibility(false);
    resultDialog.show(false, data.score, ifmodelon, model_epoch);
};

const changeUIVisibility = (visible: boolean) => {
    const targets = Array.from(document.getElementsByClassName('hide-on-finish')) as HTMLElement[];
    targets.forEach((t) => {
        t.style.visibility = visible ? 'visible' : 'hidden';
    });
};

const onFlick = (theta: number, velocity: number) => {
    socket.emit('hit_stone', { theta, velocity });
};

const onModelLoad = (data:ModelMessage) => {
    console.log('model:', data.model_path);
    const model_message = document.getElementById('model_message')!;
    if(ifmodelon && data.model_path){
        model_epoch=parseInt(data.model_path.substring(18))*100
        model_message.innerHTML = `現在のモデルは${model_epoch}試合分学習したもの`;
    }else{
        model_message.innerHTML = `現在のモデルは0試合分学習したもの`;
    }
};

const onHit = () => {
    if(!pointerState.enable) return;
    
    console.log('hit stone');
    socket.emit('hit_stone', { theta: pointerState.angle, velocity: pointerState.velocity });
    
    pointerState.stop();
};

// ResultDialog で「戻る」ボタンを押したとき
const onReturn = () => {
    const container = document.getElementById('restart-button-container')!;
    container.style.display = 'block';
};

// ResultDialog で「もう一度」ボタンを押したとき
const onRestart = () => {
    const container = document.getElementById('restart-button-container')!;
    container.style.display = 'none';

    stage.removeStones();
    changeUIVisibility(true);
    initialize();
};

const onToggleGraph = () => {
    const dom = document.getElementById('graph-content')!;
    dom.classList.toggle('active');
};

const handleInputs = () => {
    const inputs = [
        {
            id: 'button-right',
            key: 'ArrowRight',
            action: () => pointerState.turnRight()
        },
        {
            id: 'button-left',
            key: 'ArrowLeft',
            action: () => pointerState.turnLeft()
        },
        {
            id: 'button-up',
            key: 'ArrowUp',
            action: () => pointerState.strengthen()
        },
        {
            id: 'button-down',
            key: 'ArrowDown',
            action: () => pointerState.weaken()
        },
        {
            id: 'button-hit',
            key: ' ',
            action: () => onHit()
        },
        {
            id: 'button-graph',
            action: () => onToggleGraph()
        },
        {
            id: 'button-camera',
            action: () => stage.changeCamera()
        },
        {
            id: 'button-restart-lb',
            action: () => onRestart()
        }
    ];
    
    inputs.forEach(({ id, key, action }) => {
        // for smartphones
        const button = document.getElementById(id);
        if(button) addIntervalListener(button, action);

        // for PCs
        if(key) keyBoardHelper.addListener(key, action);
    });
};
document.domain="2021.eeic.jp";
window.onload = () => {
    console.log('Page is loaded');
    
    handleInputs();
    socket.on('make_graph', onMakeGraph);
    initialize();
    socket.on('connect', onConnect);
    socket.on('model_load', onModelLoad);
    socket.on('your_turn', onYourTurn);
    socket.on('move_stones', onMoveStones);
    socket.on('you_win', onYouWin);
    socket.on('AI_win', onAIWin);
};
