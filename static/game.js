'use strict';
const socket = io.connect();
const canvas = $('#canvas-2d')[0];
const context = canvas.getContext('2d');
const playerImage = $('#player-image')[0];
let playercursor=90;
let data_storage=null;
//球を打つ
function clearAndWriteStage(){
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.lineWidth = 10;
    context.beginPath();
    context.rect(0, 0, canvas.width, canvas.height);
    context.closePath();
    context.stroke(); 
}

function rewriteSituation(data){
    clearAndWriteStage();
    if(data===null)return;
    Object.values(data.stones).forEach((stone)=>{
        console.log(stone);
        context.beginPath();
        if(stone.camp==='you')context.fillStyle = 'red';
        else context.fillStyle = 'blue';
        context.arc(stone.x,canvas.height-stone.y,stone.radius,0,2*Math.PI);
        context.fill();
    });
}
function writePointer(theta){
    console.log(theta);
    rewriteSituation(data_storage);//再描写（いい方法があれば変えたい…）
    var length=300;
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
        writePointer(playercursor);
        $(document).on('keydown keyup', (event) => {
            //console.log("keydown,keyup");
            if(event.key === 'ArrowLeft'&& event.type === 'keydown'){
                if(playercursor<170)playercursor+=1;
                writePointer(playercursor);
            }
            if(event.key === 'ArrowRight'&& event.type === 'keydown'){
                if(playercursor>10)playercursor-=1;
                writePointer(playercursor);
            }
            if(event.key === ' ' && event.type === 'keydown'){
                console.log("hit stone");
                socket.emit("hit_stone",{"theta":playercursor,"velocity":7});
                $(document).off('keydown keyup');
            }
        });
    });
    socket.on('move_stones', (data) =>{
        rewriteSituation(data);
        data_storage=data;
    });
});