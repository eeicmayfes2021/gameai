from aiohttp import web
import socketio
import math
import threading

sio = socketio.AsyncServer(async_mode='aiohttp',logger=True, engineio_logger=True)
app = web.Application()
sio.attach(app)

WIDTH=600
HEIGHT=1000
BALL_RADIUS=50

class Stone:
    def __init__(self,camp,v,theta):
        self.camp=camp
        self.y=0
        self.x=WIDTH/2
        if self.camp=="AI":
            self.y=HEIGHT
        self.v=v
        self.theta=theta #thetaの方向に速度がv
        self.radius=BALL_RADIUS
    def move(self):
        if self.v>0:
            self.v=max(0,self.v-0.05)
        self.x+=self.v*math.cos(math.radians(self.theta))
        self.y+=self.v*math.sin(math.radians(self.theta))
        if self.x>WIDTH: #x軸方向に反転
            self.x=2*WIDTH-self.x
            self.theta=2*90-self.theta
        if self.x<0: #x軸方向に反転
            self.x=-self.x
            self.theta=2*90-self.theta
        if self.y>HEIGHT: #y軸方向に反転
            self.y=2*HEIGHT-self.y
            self.theta=-self.theta
        if self.y<0: #y軸方向に反転
            self.y=-self.y
            self.theta=-self.theta
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
            if stone.v!=0:
                stillmove=True
        if not stillmove:
            break
    #相手が打つ
    situations[sid].append( Stone("AI",5,-40) )
    while True:
        await sio.emit('move_stones', {'stones': [stone.encode() for stone in situations[sid]]},room=sid)
        sio.sleep(10)
        print("move!")
        stillmove = False
        for stone in situations[sid]:
            stone.move()
            if stone.v!=0:
                stillmove=True
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
