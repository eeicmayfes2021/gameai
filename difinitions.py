import math
import itertools
import numpy as np

WIDTH=600
HEIGHT=1000
BALL_RADIUS=30
FRICTION=0.01
STONE_NUM=5
velocity_choices=[2.0,2.25,2.5,2.75,3.0,3.25,3.5,3.75,4.0]
theta_choices=[i for i in range(45,136,5)]




class Stone:
    def __init__(self,camp,v,theta):
        self.camp=camp
        self.x=np.array([WIDTH/2,0],dtype=np.float16)
        if self.camp=="AI":
            self.x=np.array([WIDTH/2,HEIGHT],dtype=np.float16)
        self.v=np.array([v*math.cos(math.radians(theta)),v*math.sin(math.radians(theta))],dtype=np.float16)
        self.radius=BALL_RADIUS
    def move(self):
        vnorm=np.linalg.norm(self.v, ord=2)
        if vnorm>FRICTION:
            self.v=self.v*(vnorm-FRICTION)/vnorm #0.05減速
        else:
            self.v=np.array([0,0],dtype=np.float16)#停止
            return False
        self.x+=self.v
        if self.x[0]>WIDTH: #x軸方向に反転
            self.x[0]=2*WIDTH-self.x[0]
            self.v[0]=-self.v[0]
        elif self.x[0]<0: #x軸方向に反転
            self.x[0]=-self.x[0]
            self.v[0]=-self.v[0]
        if self.x[1]>HEIGHT: #y軸方向に反転
            self.x[1]=2*HEIGHT-self.x[1]
            self.v[1]=-self.v[1]
        elif self.x[1]<0: #y軸方向に反転
            self.x[1]=-self.x[1]
            self.v[1]=-self.v[1]
        return True
    def collision(self,other):
        dist=np.linalg.norm(self.x-other.x, ord=2)
        if dist>self.radius+other.radius:
            return
        #衝突している時
        #運動方程式解いた
        e=np.divide(self.x-other.x, dist, where=dist!=0)
        t=np.dot(self.v,e)-np.dot(other.v,e)
        self.v=self.v-t*e
        other.v=other.v+t*e
    def return_dist(self):
        center=np.array([WIDTH/2,HEIGHT/2],dtype=np.float16)
        dist=np.linalg.norm(self.x-center, ord=2)
        return dist
    def encode(self):
        return {'x': str(self.x[0]),
            'y': str(self.x[1]),
            'radius':self.radius,
            'camp':self.camp}


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

from concurrent.futures import ProcessPoolExecutor, Future, wait
import os
max_workers = os.cpu_count()
print(max_workers)

def movestones(stones):#ボトルネック#400ループぐらいする
    while True:
        isend=True
        iscollisionlist=[]
        for i in range(len(stones)):
            ismove=stones[i].move()
            if ismove:
                isend=False
                for j in range(len(stones)):
                    if i!=j and (j,i) not in iscollisionlist:
                        stones[i].collision(stones[j])
        if isend:
            return