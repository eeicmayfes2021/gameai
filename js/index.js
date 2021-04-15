'use strict';
import io from 'socket.io-client'
const socket = io.connect();
const canvas = $('#canvas-2d')[0];
const context = canvas.getContext('2d');
const playerImage = $('#player-image')[0];
let playercursor=90;
let playervelocity=3;
let data_storage=null;
const FRICTION=0.008
//球を打つ
function fillarc(x,y,size,color){
    context.fillStyle =color;
    context.beginPath();
    context.arc(x, y,size,0,2*Math.PI);
    context.closePath();
    context.fill();
}
function clearAndWriteStage(){
    context.save();
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.lineWidth = 10;
    context.beginPath();
    context.rect(0, 0, canvas.width, canvas.height);
    context.closePath();
    context.stroke(); 
    fillarc(canvas.width/2, canvas.height/2,250,'darkblue');
    fillarc(canvas.width/2, canvas.height/2,200,'white');
    fillarc(canvas.width/2, canvas.height/2,100,'brown');
    fillarc(canvas.width/2, canvas.height/2,50,'white');
    context.restore();
}

function rewriteSituation(data){
    clearAndWriteStage();
    if(data===null)return;
    Object.values(data.stones).forEach((stone)=>{
        context.beginPath();
        if(stone.camp==='you')context.fillStyle = 'red';
        else context.fillStyle = 'blue';
        context.arc(stone.x,canvas.height-stone.y,stone.radius,0,2*Math.PI);
        context.fill();
    });
}
function writePointer(theta,velocity){
    rewriteSituation(data_storage);//再描写（いい方法があれば変えたい…）
    var length=velocity*(velocity/FRICTION)/2;
    context.lineWidth = 5;
    var endx=canvas.width/2+length*Math.cos(theta*(Math.PI/180));
    var endy=canvas.height-length*Math.sin(theta*(Math.PI/180));
    context.beginPath();
    context.moveTo(canvas.width/2,canvas.height);
    context.lineTo(endx,endy);
    context.closePath();
    context.stroke();
    context.lineWidth = 10;
}
$(document).ready(function(){
    console.log("Page is loaded");
    clearAndWriteStage();
    socket.on('connect', (data)=>{
        console.log("gameStart!",data);
        var data={"test":"yes"};
        socket.emit("game_start",data);
    });
    socket.on('your_turn', (data) =>{
        playercursor=90;
        playervelocity=3;
        writePointer(playercursor,playervelocity);
        $(document).on('keydown keyup', (event) => {
            //console.log("keydown,keyup");
            if(event.key === 'ArrowLeft'&& event.type === 'keydown'){
                if(playercursor<135)playercursor+=1;
                writePointer(playercursor,playervelocity);
            }
            if(event.key === 'ArrowRight'&& event.type === 'keydown'){
                if(playercursor>45)playercursor-=1;
                writePointer(playercursor,playervelocity);
            }
            if(event.key === 'ArrowDown'&& event.type === 'keydown'){
                if(playervelocity>2)playervelocity-=0.25;
                writePointer(playercursor,playervelocity);
            }
            if(event.key === 'ArrowUp'&& event.type === 'keydown'){
                if(playervelocity<4)playervelocity+=0.25;
                writePointer(playercursor,playervelocity);
            }
            if(event.key === ' ' && event.type === 'keydown'){
                console.log("hit stone");
                socket.emit("hit_stone",{"theta":playercursor,"velocity":playervelocity});
                $(document).off('keydown keyup');
            }
        });
    });
    socket.on('move_stones', (data) =>{
        rewriteSituation(data);
        data_storage=data;
    });
    socket.on('you_win', (data) =>{
        console.log("you win! score:",data["score"])
        const scoreboard = document.getElementById("scoreboard");
        scoreboard.innerHTML=data["score"]+"点であなたの勝利です．";
    });
    socket.on('AI_win', (data) =>{
        console.log("AI win! score:",data["score"])
        const scoreboard = document.getElementById("scoreboard");
        scoreboard.innerHTML=data["score"]+"点であなたの負けです．";
    });
});