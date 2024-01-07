# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 14:25:04 2023

@author: BR11WP
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 13:47:21 2023

@author: BR11WP
"""


# Q learning for the 4x4 Gridworld example


import numpy as np

episodes = 10000 # Number of episodes 

n_states = 15 # Number of states: 14 nomral states and two terminal states (represented by state 0) 

n_actions = 4 # Number of total actions

# we initialise the q table with zeros. The q table is a matrix with n_states rows and n_actions columns
q = np.random.uniform( low = 0, high = 0, size = ( n_states, n_actions)) # initializing the q table

# Assign equal probability to each action
p_a = 0.25 * np.ones(4)

A = [0,1,2,3] # 4 actions 0- Up, 1- Down, 2- right, 3-left

S = [1,2,3,4,5,6,7,8,9,10,11,12,13,14] # states

# Probability of each state
p_s = (1/14) * np.ones(14)

# Number of steps in each episode
K = 100

# The greedy action is chosen with probability 1-epsilon and a random action is chosen with probability epsilon
epsilon = 0.8

# This is the learning rate
alpha = 0.01 # learning rate


h = np.zeros(episodes)

# The action state is a vector that stores the action taken at each state
action_state = np.zeros(n_states)






# To generate the dynamics

def n_state(state,action):
        
    
    if state == 1:
        
        if action == 0:
            
            next_state = 1
            
            r = -1
            
        elif action == 1:
            
            next_state = 5
            
            r = -1
            
        elif action == 2:
            
            next_state = 2
            
            r = -1
            
        else:
            
            next_state = 0
            
            r = -1
            
    elif state == 2:
        
        if action == 0:
            
            next_state = 2
            
            r = -1
            
        elif action == 1:
            
            next_state = 6
            
            r = -1
            
        elif action == 2:
            
            next_state = 3
            
            r = -1
            
        else:
            
            next_state = 1
            
            r = -1 
            
    elif state == 3:
        
        if action == 0:
            
            next_state = 3
            
            r = -1
            
        elif action == 1:
            
            next_state = 7
            
            r = -1
            
        elif action == 2:
            
            next_state = 3
            
            r = -1
            
        else:
            
            next_state = 2
            
            r = -1 
            
    elif state == 4:
        
        if action == 0:
            
            next_state = 0
            
            r = -1
            
        elif action == 1:
            
            next_state = 8
            
            r = -1
            
        elif action == 2:
            
            next_state = 5
            
            r = -1
            
        else:
            
            next_state = 4
            
            r = -1 
            
    elif state == 5:
        
        if action == 0:
            
            next_state = 1
            
            r = -1
            
        elif action == 1:
            
            next_state = 9
            
            r = -1
            
        elif action == 2:
            
            next_state = 6
            
            r = -1
            
        else:
            
            next_state = 4
            
            r = -1 
            
    elif state == 6:
        
        if action == 0:
            
            next_state = 2
            
            r = -1
            
        elif action == 1:
            
            next_state = 10
            
            r = -1
            
        elif action == 2:
            
            next_state = 7
            
            r = -1
            
        else:
            
            next_state = 5
            
            r = -1 
            
    elif state == 7:
        
        if action == 0:
            
            next_state = 3
            
            r = -1
            
        elif action == 1:
            
            next_state = 11
            
            r = -1
            
        elif action == 2:
            
            next_state = 7
            
            r = -1
            
        else:
            
            next_state = 6
            
            r = -1 
            
    elif state == 8:
        
         
        if action == 0:
             
            next_state = 4
             
            r = -1
             
        elif action == 1:
             
            next_state = 12
             
            r = -1
             
        elif action == 2:
             
            next_state = 9
             
            r = -1
             
        else:
             
            next_state = 8
             
            r = -1 
             
    elif state == 9:
        
            
        if action == 0:
            
            next_state = 5
             
            r = -1
             
        elif action == 1:
             
            next_state = 13
             
            r = -1
             
        elif action == 2:
             
            next_state = 10
             
            r = -1
             
        else:
             
            next_state = 8
             
            r = -1 
            
            
    elif state == 10:
        
            
        if action == 0:
            
            next_state = 6
             
            r = -1
             
        elif action == 1:
             
            next_state = 14
             
            r = -1
             
        elif action == 2:
             
            next_state = 11
             
            r = -1
             
        else:
             
            next_state = 9
             
            r = -1 
            
            
    elif state == 11:
        
            
        if action == 0:
            
            next_state = 7
             
            r = -1
             
        elif action == 1:
             
            next_state = 0
             
            r = -1
             
        elif action == 2:
             
            next_state = 11
             
            r = -1
             
        else:
             
            next_state = 10
             
            r = -1 
            
            
    elif state == 12:
        
        if action == 0:
            
            next_state = 8
             
            r = -1
             
        elif action == 1:
             
            next_state = 12
             
            r = -1
             
        elif action == 2:
             
            next_state = 13
             
            r = -1
             
        else:
             
            next_state = 12
             
            r = -1 
            
            
    elif state == 13:
        
        if action == 0:
            
            next_state = 9
             
            r = -1
             
        elif action == 1:
             
            next_state = 13
             
            r = -1
             
        elif action == 2:
             
            next_state = 14
             
            r = -1
             
        else:
             
            next_state = 12
             
            r = -1 
            
            
            
    else:
        
        if action == 0:
            
            next_state = 10
             
            r = -1
             
        elif action == 1:
             
            next_state = 14
             
            r = -1
             
        elif action == 2:
             
            next_state = 0
             
            r = -1
             
        else:
             
            next_state = 13
             
            r = -1 
        
        
        
        
        
        
            
    return next_state,r
            
    
action = np.random.choice(A, p = p_a) # initial action is randomly chosen

for i in range(n_actions):
    
    action_state[i] = action


# Main loop for learning optimal action

for i in range(episodes):
    
    # If the number of episodes is greater than half of the total number of episodes, then we reduce the epsilon and alpha values to have a more greedy action selection
    if i > episodes/2:
        
        epsilon = 1/i
        
        alpha = 1/ i
    
    # Initialisze the state in this episode randomly, assing equal probability to each state with p
    state = np.random.choice(S, p = p_s)
    

    # store the expected rewawrd for each episode for state 3 and action 3
    h[i] = q[3,3]
    
    
    # Execute the entire episode
    for j in range(K):
        
        # epsilon-greedy action selection
        
        # This determines the explore or exploit action
        if np.random.random() < 1 - epsilon: 
            
            # Select the action with the highest q value for the current state
            action = np.argmax(q[state]) # Greedy action
            action_state[state] = action
            
        else:
            
            action = np.random.choice(A, p = p_a) # Random action for exploration
            action_state[state] = action            
        
        # Generate the next state and reward
            
        transition = n_state(state, action) 
        print(f"transition: {transition}")
        
        print(state,action)
        
        next_state = transition[0]
        r = transition[1]
        
        # Update the q values 
        
        # Temporal difference error
        td = r + np.max(q[next_state]) - q[state,action]
        print(f"td: {td}")


        # SARSA with discount factor gamma = 1
        gamma = 1
        q[state,action] = (1-alpha) * q[state,action] + alpha * (r + gamma * q[next_state, action_state[next_state].astype(int)])
        # Q-learning
        # q[state,action] = q[state,action] + alpha * (r + gamma * np.max(q[next_state]) - q[state,action])
        
        state = next_state
        
        
        # Terminate the episode if the terminal state 0 is reached
        
        if state == 0:
            
            break


# Value function
V = np.zeros(n_states)
# Optimal policy
pi = np.zeros(n_states)

for i in range(n_states):
  V[i] = np.max(q[i])
  pi[i] = np.argmax(q[i])


print(f"q: {q}")

print(f"V: {V}")
print(f"pi: {pi}")

import matplotlib.pyplot as plt
plt.plot(h)
plt.show()
