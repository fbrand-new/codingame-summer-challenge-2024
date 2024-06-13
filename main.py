import sys
import math

left = "LEFT"
right = "RIGHT"
down = "DOWN"
up = "UP"

HURDLE = {left: 1, down: 2, right: 3, up: 2}
HURDLE_OBSTACLE = '#'

# Values are [left,down,right,up]

def dist(curr_x,curr_y,target_x,target_y):
    return math.sqrt(math.pow(target_x-curr_x,2)+math.pow(target_y-curr_y,2))

def debug(msg):
    print(msg, file=sys.stderr, flush=True)

def hurdle_move_value(action,track,pos) -> list:

    max_pos = len(track)
    if pos < max_pos and track[pos+1] == HURDLE_OBSTACLE:
        return [1,1,1,2] # TODO: account for stun time
    if pos < max_pos and track[pos+2] == HURDLE_OBSTACLE:
        return [1,2,2,2]
    else : # TODO: account for stun time
        return [1,2,3,2]

def archery_move_value(action,curr_wind,x,y) -> list:

    # TODO: needs refactoring
    curr_dist = dist(x,y,0,0)

    if action == left:
        x -= curr_wind
    elif action == right:
        x += curr_wind
    elif action == up:
        y += curr_wind
    elif action == down:
        y -= curr_wind
    
    new_dist = dist(x,y,0,0)

    return curr_dist - new_dist

def skate_move_value(action,risks):
    value_dict = {0:1,1:2,2:8/5,3:7/3}
    
    left_idx = risks.index('L')
    right_idx = risks.index('R')
    up_idx = risks.index('U')
    down_idx = risks.index('D')

    return [value_dict[left_idx],
            value_dict[down_idx],
            value_dict[right_idx],
            value_dict[up_idx]]

def diving_move_value(goal,curr_combo):
    if goal == 'L':
        return [curr_combo+1,1,1,1]
    if goal == '':
        return [curr_combo+1,1,1,1]

def best_move(gpu,pos):
    
    max_pos = len(gpu) - 1
    if pos < max_pos and gpu[pos+1] == '#':
        act = up
    elif pos+2 < max_pos and gpu[pos+1] == '.' and gpu[pos+2] == '#':
        act = left
    elif pos+3 < max_pos and gpu[pos+1] == '.' and gpu[pos+2] == '.' and gpu[pos+3] == '#':
        act = down
    else:
        act = right

    return act

def max_policy(actions):
    return max(actions)

player_idx = int(input())
nb_games = int(input())

act = None

# game loop
while True:

    actions = []

    for i in range(3):
        score_info = input()
    for i in range(nb_games):
        inputs = input().split()
        gpu = inputs[0]
        reg_0 = int(inputs[1])
        reg_1 = int(inputs[2])
        reg_2 = int(inputs[3])
        reg_3 = int(inputs[4])
        reg_4 = int(inputs[5])
        reg_5 = int(inputs[6])
        reg_6 = int(inputs[7])

        # Consider the only the next possible moves and chose which one is best for 
        # the most races
        act = best_move(gpu,reg_0)
        actions.append(act)

    act = max_policy(actions)

    print(act)
