from aiohttp import web
import socketio
import math
import itertools
import numpy as np
import random
import tensorflow as tf
import copy
import os
import subprocess
import datetime
import requests
import json
import requests
import json

from cdefinitions import *
from variables import *

DEBUG = os.getenv('APP_DEBUG') == '1'
MODEL_BUCKET_NAME = os.getenv('MODEL_BUCKET_NAME')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
API_URL = 'https://0k33okho4j.execute-api.ap-northeast-1.amazonaws.com/api'
API_TOKEN = 'qYpG2xGo8osuyQqYLLa3Ehp32HLdL2eGHT2YJrC2rHj3P82X9w'

sio = socketio.AsyncServer(async_mode='aiohttp', ping_timeout=10, ping_interval=30)#,logger=True, engineio_logger=True
app = web.Application()
sio.attach(app)
# model_load= tf.keras.models.load_model('models/eval_obs_002160')

# awsの認証情報の取得
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    aws_dir = os.path.abspath('./.aws')
    with open(os.path.join(aws_dir, "credentials"), mode="w") as f:
        f.write("[default]\n")
        f.write(f"aws_access_key_id={AWS_ACCESS_KEY_ID}\n")
        f.write(f"aws_secret_access_key={AWS_SECRET_ACCESS_KEY}\n")
    with open(os.path.join(aws_dir, "config"), mode="w") as f:
        f.write("[default]\n")
        f.write(f"region=ap-northeast-1\n")
        f.write(f"output=json\n")

model_last_get = None
def get_model_from_s3():
    global model_last_get
    if model_last_get != None and datetime.datetime.now() - model_last_get < datetime.timedelta(minutes=5):
        return
    model_last_get = datetime.datetime.now()
    if MODEL_BUCKET_NAME:
        try:
            # コマンドインジェクション攻撃を防ぐため、絶対ここにユーザーから受け取った変数を用いてはいけない
            command = f'aws s3 sync s3://{MODEL_BUCKET_NAME} {os.path.abspath("./models")}'
            print(f"Running $ {command}")
            res = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            print(res)
        except:
            print("Error in syncing with s3.")

# モデルの一覧を返します。
def get_model_list():
    epoches = 10
    base_path = "./models/eval_obs_"
    models = []

    get_model_from_s3()

    while os.path.exists(base_path + str(epoches).zfill(6)):
        model_path = base_path + str(epoches).zfill(6)
        models.append(model_path)
        epoches += 10
    return models

print("search models")
models = get_model_list()
model_path = models[-1] if len(models)>0 else None
print("model path: ", model_path)

# よくないが仮置きしている…
model_load = tf.keras.models.Sequential([
  #tf.keras.layers.Flatten(),
  tf.keras.layers.InputLayer(input_shape=(HEIGHT//20,WIDTH//20,2)),
  tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(HEIGHT//20,WIDTH//20,2)),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
  tf.keras.layers.Flatten(),
  tf.keras.layers.Dense(64, activation=tf.nn.relu),
  tf.keras.layers.Dropout(0.2),
  tf.keras.layers.Dense(STONE_NUM*2+1, activation=tf.nn.softmax)
])
model_load.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
model_initial = tf.keras.models.Sequential([
  #tf.keras.layers.Flatten(),
  tf.keras.layers.InputLayer(input_shape=(HEIGHT//20,WIDTH//20,2)),
  tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(HEIGHT//20,WIDTH//20,2)),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
  tf.keras.layers.MaxPooling2D((2, 2)),
  tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
  tf.keras.layers.Flatten(),
  tf.keras.layers.Dense(64, activation=tf.nn.relu),
  tf.keras.layers.Dropout(0.2),
  tf.keras.layers.Dense(STONE_NUM*2+1, activation=tf.nn.softmax)
])
model_initial.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
# tf.keras.models.load_model('models/eval_obs_000010')

if model_path:
    print("find model")
    flag = False  
    model_load = tf.keras.models.load_model(model_path)

#stonesToObsとmovestonesはモデルと同じにする
def stonesToObs(stones): #Stoneの塊をobs(numpy.ndarray)に変換する
    obs=np.array([[[0 for k in range(2)] for j in range(WIDTH//20)] for i in range(HEIGHT//20)],dtype=np.uint8)
    i_you=0
    i_AI=STONE_NUM
    for stone in stones:
        w=int( min((WIDTH//20)-1,stone.x[0]//20) )
        h=int( min((HEIGHT//20)-1,stone.x[1]//20) )
        if stone.camp=='you':
            obs[h][w][0]=1
        else:
            obs[h][w][1]=1
    return obs

def test_multi(m):
    stones,velocity,theta=m
    temp_stones=copy.deepcopy(stones)
    temp_stones.append(Stone("AI",velocity,theta))
    movestones(temp_stones)
    obs=stonesToObs(temp_stones)
    return obs

def choiceSecond(stones,model_changer):#後攻を選ぶ
    max_velocity=-1
    max_theta=-1
    max_score=-1001001001
    obs_list=[]
    vtheta_list=[]
    for velocity in velocity_choices:
        for theta in theta_choices:
            vtheta_list.append((velocity,theta+180))
            obs_list.append( test_multi((stones,velocity,theta+180)) )
    #https://note.nkmk.me/python-tensorflow-keras-basics/
    if model_changer=='on':
        next_score_probs=model_load.predict(np.asarray(obs_list))
    else:
        next_score_probs=model_initial.predict(np.asarray(obs_list))
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

situations={}#盤面ごとに存在するカーリングの球の状態を記録する
ifmodelon={}
async def index(request):
    """Serve the client-side application."""
    with open('dist/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

async def model_list(request):
    return web.json_response(models)

def getscorejson():
    url="https://0k33okho4j.execute-api.ap-northeast-1.amazonaws.com/api/model"
    response = requests.get(url)
    jsonData = response.json()
    return jsonData

@sio.event
async def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def init(sid):
    print("init ", sid)
    situations[sid]=[]

@sio.event
async def game_start(sid, data): 
    #グラフを作成してdist/graph.pngに格納
    jsons=getscorejson()#"name":"./models/eval_obs_000450","total":4,"win":2,"lose":2
    xylist=[]
    for json in jsons:
        if json["total"]>0:
            winrate=json["win"]/json["total"]
            if json["name"]=="initial":
                xylist.append([0,winrate])
            elif json["name"][0:-6]=="./models/eval_obs_":
                xylist.append([int(json["name"][-6:])*100,winrate])
    xylist.sort()
    if len(xylist)>0:
        xlist,ylist=(list(x) for x in zip(*xylist))
        await sio.emit('make_graph', {'xlist': xlist, 'ylist':ylist},sid=sid)
    
    global model_path, model_load
    print("game_start model: ", data['model'])
    ifmodelon[sid]=data['model']
    if ifmodelon[sid]=='on':
        print("search models")
        models = get_model_list()
        new_model_path = models[-1] if len(models)>0 else None
        print("model path: ", new_model_path)

        if new_model_path and new_model_path != model_path:
            print("change model")
            model_load = tf.keras.models.load_model(new_model_path)
        model_path = new_model_path
        await sio.emit('model_load', {'model_path': new_model_path})#全てのroomでモデルが変更される

    #相手が打つ
    velocity,theta= choiceSecond(situations[sid],ifmodelon[sid])
    situations[sid] = [Stone("AI",velocity,theta)]
    
    send_cnt=0
    send_interval=10
    while True:
        if send_cnt%send_interval==0:
            await sio.emit('move_stones', {'stones': [stone.encode() for stone in situations[sid]]},room=sid)
        send_cnt+=1
        await sio.sleep(0.0015)
        stillmove = False
        for stone in situations[sid]:
            stone.move()
            stillmove= stillmove or stone.v[0]!=0 or stone.v[1]!=0
        for pair in itertools.combinations(situations[sid], 2): #衝突判定
            pair[0].collision(pair[1])
        if not stillmove:
            break
    await sio.emit('move_stones', {'stones': [stone.encode() for stone in situations[sid]]},room=sid)
    #球を打っていいよの合図
    await sio.emit('your_turn',{'left':STONE_NUM-(len(situations[sid])//2)},room=sid)


    
@sio.event
async def hit_stone(sid,data):
    print("hit_stone")
    situations[sid].append( Stone("you",data["velocity"],data["theta"]) )
    send_cnt=0
    send_interval=10
    #print("現在の石の個数： ", len(situations[sid]))
    #print("ここから\n\n=====================================================================================================")
    while True:
        # print("data", [[stone.encode(), stone.v[0], stone.v[1]] for stone in situations[sid]])
        if send_cnt%send_interval==0:
            await sio.emit('move_stones', {'stones': [stone.encode() for stone in situations[sid]]},room=sid)
        send_cnt+=1
        await sio.sleep(0.0015)
        stillmove = False
        for stone in situations[sid]:
            stone.move()
            stillmove= stillmove or stone.v[0]!=0 or stone.v[1]!=0
        for pair in itertools.combinations(situations[sid], 2): #衝突判定
            pair[0].collision(pair[1])
        if not stillmove:
            break
    await sio.emit('move_stones', {'stones': [stone.encode() for stone in situations[sid]]},room=sid)
    #相手が打つ
    if len(situations[sid])<STONE_NUM*2:
        velocity,theta=choiceSecond(situations[sid],ifmodelon[sid])
        situations[sid].append(Stone("AI",velocity,theta))
        
        send_cnt=0
        send_interval=10
        while True:
            if send_cnt%send_interval==0:
                await sio.emit('move_stones', {'stones': [stone.encode() for stone in situations[sid]]},room=sid)
            send_cnt+=1
            await sio.sleep(0.0015)
            stillmove = False
            for stone in situations[sid]:
                stone.move()
                stillmove= stillmove or stone.v[0]!=0 or stone.v[1]!=0
            for pair in itertools.combinations(situations[sid], 2): #衝突判定
                pair[0].collision(pair[1])
            if not stillmove:
                break
        await sio.emit('move_stones', {'stones': [stone.encode() for stone in situations[sid]]},room=sid)
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
            send_result(False, ifmodelon[sid]) # 結果を記録
            await sio.emit('you_win',{"score":score},room=sid)
        else: #win player 2
            for stone in situations[sid]:
                dist=stone.return_dist()
                if stone.camp=='AI' and dist<player1_min_dist:
                    score-=1 #player1のreward
            send_result(True, ifmodelon[sid]) # 結果を記録
            await sio.emit('AI_win',{"score":score},room=sid)            
    else:
        await sio.emit('your_turn',{'left':STONE_NUM-(len(situations[sid])//2)},room=sid)
        

# 結果をAPIに送信
def send_result(AI_win, ifmodelon):
    if not MODEL_BUCKET_NAME:
        return
    print(f"Result send AI: {AI_win} model: {model_path} ifmodelon: {ifmodelon}")
    response = requests.post(
        API_URL + "/result",
        json.dumps({
            "model": model_path if ifmodelon == "on" and model_path else "initial",
            "token": API_TOKEN,
            "win": AI_win,
            "lose": not AI_win, 
        }),
        headers={'Content-Type': 'application/json'},
    )


@sio.event
def disconnect(sid):
    print('disconnect ', sid)
    situations.pop(sid, "Not Found")
    ifmodelon.pop(sid, "Not Found")

if DEBUG:
    app.router.add_static('/dist', 'dist')
    app.router.add_get('/', index)
    app.router.add_get('/api/models', model_list)

if __name__ == '__main__':
    web.run_app(app)

