from libc.math cimport sin,cos,pi,sqrt
import itertools
cpdef int WIDTH=600
cpdef int HEIGHT=1000
cpdef int BALL_RADIUS=30
cpdef float FRICTION=0.008

cdef class Stone:
    cdef public str camp
    cdef public double x[2]
    cdef public double v[2]
    cdef public int radius
    def __init__(self,camp,v,theta):
        self.camp=camp
        self.x=[WIDTH/2.0,BALL_RADIUS]
        if self.camp=="AI":
            self.x=[WIDTH/2,HEIGHT-BALL_RADIUS]
        self.v=[v*cos(theta*pi/180),v*sin(theta*pi/180)]
        self.radius=BALL_RADIUS
    cpdef move(self):
        vnorm= sqrt(self.v[0]*self.v[0]+self.v[1]*self.v[1])
        if vnorm>FRICTION:
            self.v=[self.v[0]*(vnorm-FRICTION)/vnorm,self.v[1]*(vnorm-FRICTION)/vnorm] #0.05減速
        else:
            self.v=[0,0]#停止
            return False
        self.x[0]+=self.v[0]
        self.x[1]+=self.v[1]
        if self.x[0]>WIDTH-self.radius: #x軸方向に反転
            self.x[0]=2*(WIDTH-self.radius)-self.x[0]
            self.v[0]=-self.v[0]
        elif self.x[0]<0+self.radius: #x軸方向に反転
            self.x[0]=2*(0+self.radius)-self.x[0]
            self.v[0]=-self.v[0]
        if self.x[1]>HEIGHT-self.radius: #y軸方向に反転
            self.x[1]=2*(HEIGHT-self.radius)-self.x[1]
            self.v[1]=-self.v[1]
        elif self.x[1]<0+self.radius: #y軸方向に反転
            self.x[1]=2*(0+self.radius)-self.x[1]
            self.v[1]=-self.v[1]
        return True
    cpdef collision(self,other):
        dist=sqrt( (self.x[0]-other.x[0])*(self.x[0]-other.x[0])+(self.x[1]-other.x[1])*(self.x[1]-other.x[1]))
        if dist>self.radius+other.radius or dist==0:
            return
        #衝突している時
        #運動方程式解いた
        e = [(other.x[0] - self.x[0])/dist,(other.x[1] - self.x[1])/dist] #逆向き
        t = (self.v[0]*e[0]+self.v[1]*e[1])-(other.v[0]*e[0]+other.v[1]*e[1])

        avex = [self.x[0]/2 + other.x[0]/2, self.x[1]/2 + other.x[1]/2] #平均
        avev = [self.v[0]/2 + other.v[0]/2, self.v[1]/2 + other.v[1]/2] #平均

        rev1 = [self.v[0] - avev[0], self.v[1] - avev[1]]
        rev2 = [other.v[0] - avev[0], other.v[1] - avev[1]]

        if rev1[0] * e[0] + rev1[1]*e[1] < 0 and rev2[0]*e[0] + rev2[1]*e[1]>0:
            return

        self.v=[self.v[0]-t*e[0],self.v[1]-t*e[1]]
        other.v=[other.v[0]+t*e[0],other.v[1]+t*e[1]]
    cpdef return_dist(self):
        center=[WIDTH/2,HEIGHT/2]
        dist=sqrt( (self.x[0]-center[0])*(self.x[0]-center[0])+(self.x[1]-center[1])*(self.x[1]-center[1]))
        return dist
    cpdef encode(self):
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

cpdef movestones(list stones):#ボトルネック#400ループぐらいする
    while True:
        stillmove=False
        for stone in stones:
            stone.move()
            stillmove= stillmove or stone.v[0]!=0 or stone.v[1]!=0
        for pair in itertools.combinations(stones, 2): #衝突判定
            pair[0].collision(pair[1])
        if not stillmove:
            return
