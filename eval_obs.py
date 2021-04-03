import sys
import math
import numpy as np
import itertools
import random
import tensorflow as tf
import copy
import matplotlib.pyplot as plt

WIDTH=600
HEIGHT=1000
BALL_RADIUS=30
FRICTION=0.01
STONE_NUM=5
velocity_choices=[2.0,2.25,2.5,2.75,3.0,3.25,3.5,3.75,4.0]
theta_choices=[i for i in range(45,136,5)]

episode_num=100000
match_per_episode=100
SAVE_NUM=10 #モデルを保存する
EVAL_NUM=10 #モデルを評価する

#ランダムと
epsilon_begin = 1.0
epsilon_end = 0.3
epsilon_decay = episode_num
epsilon_func = lambda step: max(epsilon_end, epsilon_begin - (epsilon_begin - epsilon_end) * (step / epsilon_decay))

model = tf.keras.models.Sequential([
  #tf.keras.layers.Flatten(),
  tf.keras.layers.InputLayer(input_shape=(STONE_NUM*4,)),
  tf.keras.layers.Dense(STONE_NUM*4, activation=tf.nn.relu),
  tf.keras.layers.Dropout(0.2),
  tf.keras.layers.Dense(STONE_NUM*2+1, activation=tf.nn.softmax)
])
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

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
    obs=np.array([-1 for i in range(STONE_NUM*4)],dtype=np.float32)
    i_you=0
    i_AI=STONE_NUM
    for stone in stones:
        if stone.camp=='you' and i_you<STONE_NUM:#check!正規化するかどうか？
            obs[i_you*2]=stone.x/WIDTH
            obs[i_you*2+1]=stone.y/HEIGHT
            i_you+=1
        if stone.camp=='AI' and i_AI<STONE_NUM*2:
            obs[i_AI*2]=stone.x/WIDTH
            obs[i_AI*2+1]=stone.y/HEIGHT
            i_AI+=1
    return obs

def calculatePoint(stones):
    score=0
    player1_min_dist=1001001001
    player2_min_dist=1001001001
    for stone in stones:
        dist=stone.return_dist()
        if stone.camp=='you':
            player1_min_dist=min(player1_min_dist,dist)
        else:
            player2_min_dist=min(player2_min_dist,dist)
    score=0
    if player1_min_dist<player2_min_dist : #win player 1
        for stone in stones:
            if stone.camp=='you' and stone.return_dist()<player2_min_dist:
                score+=1 #player1のreward
    else: #win player 2
        for stone in stones:
            if stone.camp=='AI' and stone.return_dist()<player1_min_dist:
                score-=1 #player1のreward
    return score

def movestones(stones):
    while True:
        stillmove = False
        for stone in stones:
            stone.move()
            if stone.v[0]!=0 or stone.v[1]!=0:
                stillmove=True
        for pair in itertools.combinations(stones, 2): #衝突判定
            pair[0].collision(pair[1])
        if not stillmove:
            return

def choiceSecond(stones):#後攻を選ぶ
    max_velocity=-1
    max_theta=-1
    max_score=-1001001001
    obs_list=[]
    for velocity in velocity_choices:
        for theta in theta_choices:
            temp_stones=copy.deepcopy(stones)
            temp_stones.append(Stone("AI",velocity,theta))
            movestones(temp_stones)
            obs=stonesToObs(temp_stones)
            obs_list.append(obs)
    #https://note.nkmk.me/python-tensorflow-keras-basics/
    next_score_probs=model.predict(np.asarray(obs_list))
    itr=0
    for velocity in velocity_choices:
        for theta in theta_choices:
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

def choiceFirst(stones):#先攻を選ぶ
    max_velocity=-1
    max_theta=-1
    max_score=-1001001001
    obs_list=[]
    for velocity in velocity_choices:
        for theta in theta_choices:
            temp_stones=copy.deepcopy(stones)
            temp_stones.append(Stone("AI",velocity,theta))
            movestones(temp_stones)
            obs=stonesToObs(temp_stones)
            obs_list.append(obs)
    #https://note.nkmk.me/python-tensorflow-keras-basics/
    next_score_probs=model.predict(np.asarray(obs_list))
    itr=0
    for velocity in velocity_choices:
        for theta in theta_choices:
            next_score=0.0
            for i in range(STONE_NUM*2+1):
                next_score+=next_score_probs[itr][i]*(i-STONE_NUM)
            next_score=-next_score #先攻なので！
            #print(next_score)
            if next_score>max_score:
                max_score=next_score
                max_theta=theta
                max_velocity=velocity
            itr+=1
    return max_velocity,max_theta


scores_list=[]
for episode in range(episode_num):
    print("episode:",episode)
    obs_list=[]
    scores=[]
    for match in range(match_per_episode):
        #一回プレイする
        stones=[]
        side=1
        while len(stones)<STONE_NUM*2:
            camp= "you" if side==1 else "AI"
            if random.random()<epsilon_func(episode):#Stoneをランダムに追加
                velocity=random.choice( velocity_choices )
                theta=random.choice( theta_choices )
            else: #評価関数に従って追加
                velocity,theta= choiceFirst(stones) if side==1 else choiceSecond(stones)    
            stones.append(Stone(camp,velocity,theta))
            #運動
            movestones(stones)
            #obs_listに記録
            obs_list.append(stonesToObs(stones))
            side=-side
        #(後攻にとっての)終局時の得点を計算
        score=calculatePoint(stones)
        score=-score#後攻にとってのreward
        #終局時の点数と各状況を紐付けてネットワークを学習させる
        for i in range(STONE_NUM*2):
            scores.append(score+STONE_NUM)
    obs_list=np.asarray(obs_list,dtype=np.float32)
    scores=np.asarray(scores)
    model.fit(obs_list,scores,epochs=10)
    #EVAL_NUMエピソードごとに10回プレイした平均点を記録してplot
    if episode%EVAL_NUM==0:
        print("evaluating...",episode)
        total_score=0
        plays=10
        for play in range(plays):
            stones=[]
            side=1
            while len(stones)<STONE_NUM*2:
                camp= "you" if side==1 else "AI"
                if side==1:
                    #先手はランダム
                    velocity=random.choice( [2.0,2.25,2.5,2.75,3.0,3.25,3.5,3.75,4.0] )#2~4,0.25刻み
                    theta=random.randrange(45,136,5)#45,50,55,...,135
                    stones.append(Stone(camp,velocity,theta))
                else:
                    velocity,theta=choiceSecond(stones)
                    stones.append(Stone(camp,velocity,theta))
                movestones(stones) 
                side=-side
            score=-calculatePoint(stones)
            total_score+=score
        print("average_score:",total_score/plays)
        scores_list.append(total_score/plays)
        x=[i*EVAL_NUM for i in range(len(scores_list))]
        plt.plot(x,scores_list,'b+')
        plt.savefig("graphs/eval_obs.png")
    #SAVE_NUMエピソードごとにモデルを保存 https://www.tensorflow.org/guide/saved_model
    if episode%SAVE_NUM==0:
        tf.saved_model.save(model, 'models/eval_obs_{:0=6}/'.format(episode))
        print("saved ",'models/eval_obs_{:0=6}/'.format(episode))
