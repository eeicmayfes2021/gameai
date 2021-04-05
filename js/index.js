import { io } from 'socket.io-client';

import { Stage2D } from './stage2d';
import { Stage3D } from './stage3d';
import { clamp } from './util';

const socket = io();
// const stage = new Stage2D('canvas-2d');
const stage = new Stage3D(500, 400, 600, 1000, 'canvas-3d');

let playercursor = 90;
let playervelocity = 3;

const onConnect = (received) => {
    console.log('gameStart!', received);
    const data = { test: 'yes' };
    socket.emit('game_start', data);
};

const onYourTurn = (data) => {
    playercursor = 90;
    playervelocity = 3;
    stage.writePointer(playercursor, playervelocity);
    
    /** @param {KeyboardEvent} event */
    const onKeyDown = (event) => {
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
        
        stage.writePointer(playercursor, playervelocity);

        event.preventDefault();
    };

    document.addEventListener('keydown', onKeyDown);
};

const onMoveStones = (data) => {
    stage.rewriteSituation(data);
    stage.updateDataStorage(data);
};

const onYouWin = (data) => {
    console.log('you win! score:', data.score);
    const scoreboard = document.getElementById('scoreboard');
    scoreboard.innerHTML = `${data.score}点であなたの勝利です．`;
};

const onAIWin = (data) => {
    console.log('AI win! score:', data.score);
    const scoreboard = document.getElementById('scoreboard');
    scoreboard.innerHTML = `${data.score}点であなたの負けです．`;
};

window.onload = () => {
    console.log('Page is loaded');

    socket.on('connect', onConnect);
    socket.on('your_turn', onYourTurn);
    socket.on('move_stones', onMoveStones);
    socket.on('you_win', onYouWin);
    socket.on('AI_win', onAIWin);
};
