import { io } from 'socket.io-client';
//import { Stage2D } from './stage2d';
import { Stage3D } from './stage3d';
import { clamp } from './util';
import { MoveStonesMessage, WinMessage, ModelMessage } from './models/socket';

const socket = io();
//const stage = new Stage2D('canvas-2d', (dx, dy) => onFlick(dx, dy));
const stage = new Stage3D(600, 1000, 'canvas-2d');

let playercursor = 90;
let playervelocity = 3;

const onConnect = () => {
    console.log('gameStart!');
    const data = { test: 'yes' };
    socket.emit('game_start', data);
};

const onYourTurn = () => {
    playercursor = 90;
    playervelocity = 3;
    stage.updatePointer(playercursor, playervelocity);
    
    const onKeyDown = (event: KeyboardEvent) => {
        switch(event.key) {
            case 'ArrowLeft':
                playercursor += 1.0;
                break;
            case 'ArrowRight':
                playercursor -= 1.0;
                break;
            case 'ArrowDown':
                playervelocity -= 0.25;
                break;
            case 'ArrowUp':
                playervelocity += 0.25;
                break;
            case ' ':
                console.log('hit stone');
                socket.emit('hit_stone', { theta: playercursor, velocity: playervelocity });
                document.removeEventListener('keydown', onKeyDown);
                break;
            default:
                return;
        }
        
        playercursor = clamp(playercursor, 45, 135);
        playervelocity = clamp(playervelocity, 2, 4);
        
        stage.updatePointer(playercursor, playervelocity);

        event.preventDefault();
    };

    document.addEventListener('keydown', onKeyDown);
};

const onMoveStones = (data?: MoveStonesMessage) => {
    stage.updateStones(data?.stones ?? []);
};

const onYouWin = (data: WinMessage) => {
    console.log('you win! score:', data.score);
    const scoreboard = document.getElementById('scoreboard')!;
    scoreboard.innerHTML = `${data.score}点であなたの勝利です．`;
};

const onAIWin = (data: WinMessage) => {
    console.log('AI win! score:', data.score);
    const scoreboard = document.getElementById('scoreboard')!;
    scoreboard.innerHTML = `${data.score}点であなたの負けです．`;
};

const onFlick = (theta: number, velocity: number) => {
    socket.emit('hit_stone', { theta, velocity });
};

const onModelLoad = (data:ModelMessage) => {
    console.log('model:', data.model_path);
};

window.onload = () => {
    console.log('Page is loaded');

    socket.on('connect', onConnect);
    socket.on('model_load', onModelLoad);
    socket.on('your_turn', onYourTurn);
    socket.on('move_stones', onMoveStones);
    socket.on('you_win', onYouWin);
    socket.on('AI_win', onAIWin);
};
