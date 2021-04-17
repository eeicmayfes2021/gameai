from aiohttp import web
import socketio
import math
import itertools
import numpy as np
import random
import tensorflow as tf
import copy
import os

from cdefinitions import *
from variables import *

DEBUG = os.getenv('APP_DEBUG') == '1'

sio = socketio.AsyncServer(async_mode='aiohttp', ping_timeout=10, ping_interval=30)#,logger=True, engineio_logger=True
app = web.Application()
sio.attach(app)
# model_load= tf.keras.models.load_model('models/eval_obs_002160')

# モデルの一覧を返します。
def get_model_list():
    epoches = 0
    base_path = "./models/eval_obs_"
    models = []
    while os.path.exists(base_path + str(epoches).zfill(6)):
        model_path = base_path + str(epoches).zfill(6)
        models.append(model_path)
        epoches += 10
    return models

print("search models")
models = get_model_list()
model_path = models[-1]
print("model path: ", model_path)

# よくないが仮置きしている…
model_load = tf.keras.models.Sequential([
  #tf.keras.layers.Flatten(),
  tf.keras.layers.InputLayer(input_shape=(STONE_NUM*4,)),
  tf.keras.layers.Dense(STONE_NUM*4, activation=tf.nn.relu),
  tf.keras.layers.Dropout(0.2),
  tf.keras.layers.Dense(STONE_NUM*2+1, activation=tf.nn.softmax)
])
model_load.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
# tf.keras.models.load_model('models/eval_obs_000010')

if model_path:
    print("find model")
    flag = False  
    model_load = tf.keras.models.load_model(model_path)

#stonesToObsとmovestonesはモデルと同じにする
def stonesToObs(stones): #Stoneの塊をobs(numpy.ndarray)に変換する
    obs=np.array([-1 for i in range(STONE_NUM*4)],dtype=np.float32)
    i_you=0
    i_AI=STONE_NUM
    for stone in stones:
        if stone.camp=='you' and i_you<STONE_NUM:#check!正規化するかどうか？
            obs[i_you*2]=stone.x[0]/WIDTH
            obs[i_you*2+1]=stone.x[1]/HEIGHT
            i_you+=1
        if stone.camp=='AI' and i_AI<STONE_NUM*2:
            obs[i_AI*2]=stone.x[0]/WIDTH
            obs[i_AI*2+1]=stone.x[1]/HEIGHT
            i_AI+=1
    return obs
    

def test_multi(m):
    stones,velocity,theta=m
    temp_stones=copy.deepcopy(stones)
    temp_stones.append(Stone("AI",velocity,theta))
    movestones(temp_stones)
    obs=stonesToObs(temp_stones)
    return obs

def choiceSecond(stones):#後攻を選ぶ
    max_velocity=-1
    max_theta=-1
    max_score=-1001001001
    obs_list=[]
    vtheta_list=[]
    for velocity in velocity_choices:
        for theta in theta_choices:
            vtheta_list.append((velocity,theta))
            obs_list.append( test_multi((stones,velocity,theta)) )
    #https://note.nkmk.me/python-tensorflow-keras-basics/
    next_score_probs=model_load.predict(np.asarray(obs_list))
    itr=0
    for velocity,theta in vtheta_list:
        next_score=0.0
        for i in range(STONE_NUM*2+1):
            next_score+=next_score_probs[itr][i]*(i-STONE_NUM)
        #print(next_score)
        if next_score>max_score:
            max_score=next_score
            max_theta=theta
            max_velocity=velocity
        itr+=1
    return max_velocity,max_theta

def test_multi2(m):
    stones,velocity,theta=m
    temp_stones=copy.deepcopy(stones)
    temp_stones.append(Stone("AI",velocity,theta))
    movestones(temp_stones)
    score=-calculatePoint(temp_stones)
    return score,velocity,theta
def choiceSecond_absolute(stones):
    max_velocity=-1
    max_theta=-1
    max_score=-1001001001
    score_list=[]
    for velocity in velocity_choices:
        for theta in theta_choices:
            score_list.append( test_multi2((stones,velocity,theta)) )
    for score,velocity,theta in score_list:
        if score>max_score:
            max_theta=theta
            max_velocity=velocity
            max_score=score
    return max_velocity,max_theta

situations={}#盤面ごとに存在するカーリングの球の状態を記録する

async def index(request):
    """Serve the client-side application."""
    with open('dist/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

async def model_list(request):
    return web.json_response(models)

@sio.event
def connect(sid, environ):
    print("connect ", sid)
    situations[sid]=[]
    
    print("search models")

    models = get_model_list()
    new_model_path = models[-1]
    print("model path: ", new_model_path)

    if new_model_path and new_model_path != model_path:
        print("change model")
        model_load = tf.keras.models.load_model(new_model_path)

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
    #velocity,theta=choiceSecond(situations[sid])
    velocity,theta=choiceSecond_absolute(situations[sid]) if len(situations[sid])==STONE_NUM*2-1 else choiceSecond(situations[sid])
    situations[sid].append(Stone("AI",velocity,theta))
    
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

if DEBUG:
    app.router.add_static('/dist', 'dist')
    app.router.add_get('/', index)
    app.router.add_get('/api/models', model_list)

if __name__ == '__main__':
    web.run_app(app)

