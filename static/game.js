'use strict';

const socket = io();
const canvas = $('#canvas-2d')[0];
const context = canvas.getContext('2d');
const playerImage = $('#player-image')[0];
let movement = {};

function gameStart(){
    console.log("gameStart!");
    var data={"test":"yes"};
    socket.emit("game_start",data);
}

socket.on('connect', gameStart);
