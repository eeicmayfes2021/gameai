import random

import cv2
import gym
import numpy as np

import torch
from torch import nn, optim
import math

from IPython.display import HTML
import curlingenv

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

env = gym.make('curlingenv-v0')
STONE_NUM=8

class PrioritizedReplayBuffer(object):
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.index = 0                
        self.buffer = []               
        self.priorities = np.zeros(buffer_size, dtype=np.float32)
        self.priorities[0] = 1.0         
    
    def __len__(self):
        return len(self.buffer)

    def push(self, experience):
        if len(self.buffer) < self.buffer_size:
            self.buffer.append(experience)
        else:
            self.buffer[self.index] = experience
        self.priorities[self.index] = self.priorities.max()
        self.index = (self.index + 1) % self.buffer_size 
    
    def sample(self, batch_size, alpha=0.6, beta=0.4):
        priorities = self.priorities[: self.buffer_size if len(self.buffer) == self.buffer_size else self.index] 
        priorities = priorities ** alpha 
        prob = priorities / priorities.sum()

        indices = np.random.choice(len(self.buffer),size=batch_size,p=prob)

        weights = (len(self.buffer)*prob[indices])**(-beta)
        weights = weights / max(weights)

        obs, action, reward, next_obs, done = zip(*[self.buffer[i] for i in indices])

        return (torch.stack(obs),
                torch.as_tensor(action), 
                torch.as_tensor(reward, dtype=torch.float32),
                torch.stack(next_obs), 
                torch.as_tensor(done, dtype=torch.uint8),
                indices,
                torch.as_tensor(weights, dtype=torch.float32))
    def update_priorities(self, indices, priorities):
        self.priorities[indices] = priorities + 1e-4

"""
    Dueling Networkを用いたQ関数を実現するためのニューラルネットワークをクラスとして記述します. 
"""
class CNNQNetwork(nn.Module):
    def __init__(self, state_shape, n_action):
        super(CNNQNetwork, self).__init__()
        self.state_shape = state_shape
        self.n_action = n_action

        self.fc_state = nn.Sequential(
            nn.Linear(STONE_NUM*4, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        self.fc_advantage = nn.Sequential(
            nn.Linear(STONE_NUM*4, 64),
            nn.ReLU(),
            nn.Linear(64, n_action)
        )
    
    def forward(self, obs):
        feature = obs
        feature = feature.view(feature.size(0), -1) 
        state_values = self.fc_state(feature) 
        advantage = self.fc_advantage(feature)
        action_values = state_values + advantage - torch.mean(advantage, dim=1, keepdim=True)
        return action_values

    def act(self, obs, epsilon):
        if random.random() < epsilon:
            action = random.randrange(self.n_action)
            theta=action//10+10
            velocity=(action%10)*0.5+0.5
            action=(velocity,theta)
        else:
            with torch.no_grad():
                action = torch.argmax(self.forward(obs.unsqueeze(0))).item()
                #print(action)#action=((theta-10)//10)*10+((velocity-0.5)/0.5)
                theta=(action//10)*10+10
                velocity=(action%10)*0.5+0.5
                action=(velocity,theta)
        return action

buffer_size = 1000#00 
initial_buffer_size = 100#00 
replay_buffer = PrioritizedReplayBuffer(buffer_size)

net = CNNQNetwork(env.observation_space.shape, n_action=161*10).to(device)
target_net = CNNQNetwork(env.observation_space.shape, n_action=161*10).to(device)
target_update_interval = 2000 

optimizer = optim.Adam(net.parameters(), lr=1e-4) 
loss_func = nn.SmoothL1Loss(reduction='none') 

gamma = 0.99 
batch_size = 32
n_episodes = 100000 #100000とかでやりたい
SAVE_NUM=1000

beta_begin = 0.4
beta_end = 1.0
beta_decay = n_episodes*16
beta_func = lambda step: min(beta_end, beta_begin + (beta_end - beta_begin) * (step / beta_decay))

epsilon_begin = 1.0
epsilon_end = 0.01
epsilon_decay =  n_episodes*16
epsilon_func = lambda step: max(epsilon_end, epsilon_begin - (epsilon_begin - epsilon_end) * (step / epsilon_decay))


def update(batch_size, beta):
    obs, action, reward, next_obs, done, indices, weights = replay_buffer.sample(batch_size, beta)
    obs, action, reward, next_obs, done, weights \
        = obs.float().to(device), action.to(device), reward.to(device), next_obs.float().to(device), done.to(device), weights.to(device)

    q_values = net(obs).gather(1, action.unsqueeze(1)).squeeze(1)
    
    with torch.no_grad():
        greedy_action_next = torch.argmax(net(next_obs),dim=1)
        q_values_next = target_net(next_obs).gather(1, greedy_action_next.unsqueeze(1)).squeeze(1)
    target_q_values = reward + gamma * q_values_next * (1 - done)
    optimizer.zero_grad()
    loss = (weights * loss_func(q_values, target_q_values)).mean()
    loss.backward()
    optimizer.step()
    replay_buffer.update_priorities(indices, (target_q_values - q_values).abs().detach().cpu().numpy())

    return loss.item()

if __name__=="__main__":
    step = 0
    rewards=[]
    for episode in range(n_episodes+1):
        obs = env.reset()
        done = False
        total_reward = 0
        camp=1
        while not done:
            if camp==1:
                action = env.action_space.sample()
                cmp,act=action
                action=(camp,act)
                #print(action)
                next_obs, reward, done, _ = env.step(action)
                #total_reward += reward
                obs = next_obs
            else:#後手について学習する
                action = net.act(torch.from_numpy(obs.astype(np.float32)).clone().float().to(device), epsilon_func(step))
                action=(camp,action)
                next_obs, reward, done, _ = env.step(action)
                total_reward += reward
                action_num= ((action[1][1]-10)//10)*10+int((action[1][0]-0.5)*2)#action=((theta-10)//10)*10+((velocity-0.5)/0.5)
                replay_buffer.push([torch.from_numpy(obs.astype(np.float32)).clone(), action_num, reward, torch.from_numpy(next_obs.astype(np.float32)).clone(), done])
                obs = next_obs

            # ネットワークを更新            
            if len(replay_buffer) > initial_buffer_size:
                #print("update")
                update(batch_size, beta_func(step))
            if (step + 1) % target_update_interval == 0:
                target_net.load_state_dict(net.state_dict())
            
            step += 1
            camp=-camp

        print('Episode: {},  Step: {},  Reward: {}'.format(episode + 1, step + 1, total_reward))
        rewards.append(total_reward)
        if episode%SAVE_NUM==0:
            torch.save(net, 'models/model_{:0=6}.pt'.format(episode))
            torch.save(target_net, 'models/target_model_{:0=6}.pt'.format(episode))
