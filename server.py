from aiohttp import web
import socketio
import math
import threading
import itertools
import numpy as np

sio = socketio.AsyncServer(async_mode='aiohttp',logger=True, engineio_logger=True)
app = web.Application()
sio.attach(app)

WIDTH=600
HEIGHT=1000
BALL_RADIUS=30
FRICTION=0.01
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
        e=np.array([self.x-other.x,self.y-other.y])/dist
        t=np.dot(self.v,e)-np.dot(other.v,e)
        self.v=self.v-t*e
        other.v=self.v+t*e
    def encode(self):
        return {'x': self.x,
            'y': self.y,
            'radius':self.radius,
            'camp':self.camp}




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
    with open('static/index.html') as f:
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
        sio.sleep(10)
        print("move!")
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
    situations[sid].append( Stone("AI",3,-40) )
    while True:
        await sio.emit('move_stones', {'stones': [stone.encode() for stone in situations[sid]]},room=sid)
        sio.sleep(10)
        print("move!")
        stillmove = False
        for stone in situations[sid]:
            stone.move()
            if stone.v[0]!=0 or stone.v[1]!=0:
                stillmove=True
        for pair in itertools.combinations(situations[sid], 2): #衝突判定
            pair[0].collision(pair[1])
        if not stillmove:
            break
    await sio.emit('your_turn',room=sid)
        
        


@sio.event
def disconnect(sid):
    print("situation:",situations.pop(sid,"Not Found"))
    print("situations:",situations)
    print('disconnect ', sid)

app.router.add_static('/static', 'static')
app.router.add_static('/node_modules', 'node_modules')
app.router.add_get('/', index)

if __name__ == '__main__':
    #sio.start_background_task(background_task)
    web.run_app(app)
