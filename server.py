from aiohttp import web
import socketio
import math
import threading
import itertools
import numpy as np
import random
import torch
from torch import nn, optim

from ddqn_curling_discrete import CNNQNetwork

sio = socketio.AsyncServer(async_mode='aiohttp')#,logger=True, engineio_logger=True
app = web.Application()
sio.attach(app)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
net_load =  torch.load("models/model_016000.pt") #34000あたりが一番強そう…（謎）

WIDTH=600
HEIGHT=1000
BALL_RADIUS=30
FRICTION=0.01
STONE_NUM=5
class Stone:
    def __init__(self,camp,v,theta):
        self.camp=camp
        self.y=0
        self.x=WIDTH/2
        if self.camp=="AI":
            self.y=HEIGHT
        self.v=np.array([v*math.cos(math.radians(theta)),v*math.sin(math.radians(theta))])
        self.radius=BALL_RADIUS
    def move(self):
        vnorm=np.linalg.norm(self.v, ord=2)
        if vnorm>FRICTION:
            self.v=self.v*(vnorm-FRICTION)/vnorm #0.05減速
        else:
            self.v=np.array([0,0])#停止
        self.x+=self.v[0]
        self.y+=self.v[1]
        if self.x>WIDTH: #x軸方向に反転
            self.x=2*WIDTH-self.x
            self.v[0]=-self.v[0]
        if self.x<0: #x軸方向に反転
            self.x=-self.x
            self.v[0]=-self.v[0]
        if self.y>HEIGHT: #y軸方向に反転
            self.y=2*HEIGHT-self.y
            self.v[1]=-self.v[1]
        if self.y<0: #y軸方向に反転
            self.y=-self.y
            self.v[1]=-self.v[1]
    def collision(self,other):
        dist=math.sqrt( (self.x-other.x)**2+(self.y-other.y)**2 )
        if dist>self.radius+other.radius:
            return
        #衝突している時
        #運動方程式解いた
        e=np.divide(np.array([self.x-other.x,self.y-other.y]), dist, where=dist!=0)
        t=np.dot(self.v,e)-np.dot(other.v,e)
        self.v=self.v-t*e
        other.v=self.v+t*e
    def return_dist(self):
        dist=math.sqrt( (self.x-WIDTH/2)**2+(self.y-HEIGHT/2)**2 )
        return dist
    def encode(self):
        return {'x': self.x,
            'y': self.y,
            'radius':self.radius,
            'camp':self.camp}

def stonesToObs(stones): #Stoneの塊をobs(numpy.ndarray)に変換する
    obs=np.array([-1 for i in range(STONE_NUM*4)])
    i_you=0
    i_AI=STONE_NUM
    for stone in stones:
        if stone.camp=='you' and i_you<STONE_NUM:
            obs[i_you*2]=stone.x
            obs[i_you*2+1]=stone.y
            i_you+=1
        if stone.camp=='AI' and i_AI<STONE_NUM*2:
            obs[i_AI*2]=stone.x
            obs[i_AI*2+1]=stone.y
            i_AI+=1
    return obs


situations={}#盤面ごとに存在するカーリングの球の状態を記録する

async def background_task():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        await sio.sleep(10)
        count += 1
        await sio.emit('my_response', {'data': 'Server generated event'})

async def index(request):
    """Serve the client-side application."""
    with open('dist/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

@sio.event
def connect(sid, environ):
    print("connect ", sid)
    situations[sid]=[]

@sio.event
async def game_start(sid, data): 
    print("message ", data['test'])
    #ここで準備
    #球を打っていいよの合図
    await sio.emit('your_turn',room=sid)


    
@sio.event
async def hit_stone(sid,data):
    print("hit_stone")
    situations[sid].append( Stone("you",data["velocity"],data["theta"]) )
    while True:
        await sio.emit('move_stones', {'stones': [stone.encode() for stone in situations[sid]]},room=sid)
        await sio.sleep(0.001)
        stillmove = False
        for stone in situations[sid]:
            stone.move()
            if stone.v[0]!=0 or stone.v[1]!=0:
                stillmove=True
        for pair in itertools.combinations(situations[sid], 2): #衝突判定
            pair[0].collision(pair[1])
        if not stillmove:
            break
    #相手が打つ
    obs=stonesToObs(situations[sid])
    action = net_load.act(torch.from_numpy(obs.astype(np.float32)).clone().float().to(device),0)
    situations[sid].append( Stone("AI",action[0],action[1]) )
    
    while True:
        await sio.emit('move_stones', {'stones': [stone.encode() for stone in situations[sid]]},room=sid)
        await sio.sleep(0.001)
        stillmove = False
        for stone in situations[sid]:
            stone.move()
            if stone.v[0]!=0 or stone.v[1]!=0:
                stillmove=True
        for pair in itertools.combinations(situations[sid], 2): #衝突判定
            pair[0].collision(pair[1])
        if not stillmove:
            break
    if len(situations[sid])==STONE_NUM*2 :
        #ゲーム終わり
        player1_min_dist=1001001001
        player2_min_dist=1001001001
        for stone in situations[sid]:
            dist=stone.return_dist()
            if stone.camp=='you':
                player1_min_dist=min(player1_min_dist,dist)
            else:
                player2_min_dist=min(player2_min_dist,dist)
        score=0
        if player1_min_dist<player2_min_dist : #win player 1
            for stone in situations[sid]:
                dist=stone.return_dist()
                if stone.camp=='you' and dist<player2_min_dist:
                    score+=1 #player1のreward
            await sio.emit('you_win',{"score":score},room=sid)
        else: #win player 2
            for stone in situations[sid]:
                dist=stone.return_dist()
                if stone.camp=='AI' and dist<player1_min_dist:
                    score-=1 #player1のreward
            await sio.emit('AI_win',{"score":score},room=sid)            
    else:
        await sio.emit('your_turn',room=sid)
        
        


@sio.event
def disconnect(sid):
    print('disconnect ', sid)

app.router.add_static('/dist', 'dist')
app.router.add_static('/node_modules', 'node_modules')
app.router.add_get('/', index)

if __name__ == '__main__':
    #sio.start_background_task(background_task)
    web.run_app(app)
