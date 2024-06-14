import sys
import math

left = "LEFT"
right = "RIGHT"
down = "DOWN"
up = "UP"

HURDLE = {left: 1, down: 2, right: 3, up: 2}
HURDLE_OBSTACLE = '#'
VAL_ACT = [left,down,right,up]

# Heuristics:
# 1. If we are stunned the value of our move should be 0
# 2. Archery value should increase the more the turn run towards the end.
# 3. We need AT LEAST one silver medal for each game else our score is ZERO! 
#   -> Get the silver+gold medals for each game and prioritize the ones in which you suck.
# 4. Let's try to assign the value to be proportional to the position I am in the game.
#   - If I am in first position every move has value 1
#   - If I am in another position then I have to consider what I need to do.
# 5. In archery if turns remaining is more than 6, value is 0
# 6. In diving, if I am sure of winning, values should be 0
# 7. No matter what, we strive not to get dead last.
# 8. Or actually keep pushing!
# 9. But If this round it's too late to catch up then we should give up.

def argmax(iterable):
    return max(enumerate(iterable), key=lambda x: x[1])[0]

def argmin(iterable):
    return min(enumerate(iterable), key=lambda x: x[1])[0]

def dist(curr_x,curr_y,target_x,target_y):
    return math.sqrt(math.pow(target_x-curr_x,2)+math.pow(target_y-curr_y,2))

def debug(msg):
    print(msg, file=sys.stderr, flush=True)

def get_scores(score: str):
    return [int(s) for s in score.split(' ')]

def sum_values(values1,values2):
    return [x+y for x,y in zip(values1,values2)]

def compute_multipliers(scores):
    
    mults = [1,1,1,1]

    for n, i in enumerate(range(1,len(scores),3)):
        gold_and_silver = sum(scores[i:i+2])
        total_games = sum(scores[i:i+3])
        if total_games > 0:
            mults[n] = (total_games - gold_and_silver)/total_games

    return mults

def apply_multiplier(values: list,multiplier: float):
    return [v*multiplier for v in values]

def am_i_last(pos:list,my_idx):
    return argmin(pos) == my_idx

def am_i_first(pos:list,my_idx):
    # Note. This does not make sense for archery
    return argmax(pos) == my_idx

def second_player(points:dict):
    return sorted(points, key=lambda x: points[x])[1]

def hurdle_move_value(track,pos,is_stunned,multiplier,first,last) -> list:

    max_pos = len(track)

    debug(f"track: {track}")
    debug(f"pos: {pos}")

    if is_stunned:
        values = [0,0,0,0]
    elif pos+1 < max_pos and track[pos+1] == HURDLE_OBSTACLE:
        values = [0,0,0,2] 
    elif pos+2 < max_pos and track[pos+2] == HURDLE_OBSTACLE:
        values = [1,0,0,0]
    elif pos+3 < max_pos and track[pos+3] == HURDLE_OBSTACLE:
        values = [1,2,0,2]
    else:
        values = [1,2,3,2]

    # if last:
    #     multiplier *= 1.5 # We do not want to be last

    return apply_multiplier(values,multiplier)

def archery_move_value(curr_wind,x,y,total_turns,turn_remaining,multiplier) -> list:

    curr_dist = dist(x,y,0,0)

    values = []

    if turn_remaining > 8:
        return [0,0,0,0]
    
    f = ((total_turns-turn_remaining)/total_turns)**2

    values.append((curr_dist - dist(x-curr_wind,y,0,0))*f)
    values.append((curr_dist - dist(x,y+curr_wind,0,0))*f)
    values.append((curr_dist - dist(x+curr_wind,y,0,0))*f)
    values.append((curr_dist - dist(x,y-curr_wind,0,0))*f)

    return apply_multiplier(values,multiplier)

def skate_move_value(risks,is_stunned,multiplier,first,last):

    if is_stunned:
        values = [0,0,0,0]

    value_dict = {0:1,1:2,2:8/5,3:7/3}
    
    left_idx = risks.index('L')
    right_idx = risks.index('R')
    up_idx = risks.index('U')
    down_idx = risks.index('D')

    values = [value_dict[left_idx],
            value_dict[down_idx],
            value_dict[right_idx],
            value_dict[up_idx]]

    # if last:
    #     multiplier *= 2

    return apply_multiplier(values,multiplier)

def diving_move_value(goal,multiplier,first,curr_combo,second_combo,my_points,second_points,remaining_turns):

    max_possible_second_points = second_points + sum(range(second_combo,second_combo+remaining_turns))
    debug(f"max_possible_second_points: {max_possible_second_points}")
    if max_possible_second_points < my_points:
        values = [0,0,0,0]
    # elif first:
    #     values = [0,0,0,0]
    elif goal == 'L':
        values = [curr_combo+1,1,1,1]
    elif goal == 'D':
        values = [1,curr_combo+1,1,1]
    elif goal == 'R':
        values = [1,1,curr_combo+1,1]
    elif goal == 'U':
        values = [1,1,1,curr_combo+1]
    else :
        values = [0,0,0,0]

    return apply_multiplier(values,multiplier)

player_idx = int(input())
regs = [0,0,0,0,0,0,0]
nb_games = int(input())

act = None

total_archery_rounds = 0
# game loop
while True:

    values = [0,0,0,0]

    actions = []

    for i in range(3):
        score_info = input()
        if i == player_idx:
            scores = get_scores(score_info)
            multipliers = compute_multipliers(scores)

    for i in range(nb_games):
        inputs = input().split()
        gpu = inputs[0]
        regs[0] = int(inputs[1])
        regs[1] = int(inputs[2])
        regs[2] = int(inputs[3])
        regs[3] = int(inputs[4])
        regs[4] = int(inputs[5])
        regs[5] = int(inputs[6])
        regs[6] = int(inputs[7])

        if gpu == "GAME_OVER":
            if i == 1:
                total_archery_rounds = 0
            continue

        if i == 0:
            is_stunned = regs[player_idx+3] > 0
            am_first = am_i_first(regs[0:3],player_idx)
            am_last = am_i_last(regs[0:3],player_idx)
            my_pos = regs[player_idx]
            values = sum_values(values,hurdle_move_value(gpu,my_pos,is_stunned,multipliers[i],am_first,am_last))
            debug(f"hurdle values: {values}")
        if i == 1:
            if total_archery_rounds == 0:
                total_archery_rounds = len(gpu)
                remaining_rounds = len(gpu)
            else:
                remaining_rounds = len(gpu)
            values = sum_values(values,
                                archery_move_value(
                                    int(gpu[0]),regs[player_idx*2],regs[player_idx*2+1],
                                    total_archery_rounds,
                                    remaining_rounds,
                                    multipliers[i]))
            debug(f"archery values: {values}")
        if i == 2:
            is_stunned = regs[player_idx+3] < 0
            am_first = am_i_first(regs[0:3],player_idx)
            am_last = am_i_last(regs[0:3],player_idx)
            values = sum_values(values,skate_move_value(gpu,is_stunned,multipliers[i],am_first,am_last))
            debug(f"skating values: {values}")
        if i == 3:
            am_first = am_i_first(regs[0:3],player_idx)
            points = {0:regs[0],1:regs[1],2:regs[2]}
            second_player_idx = second_player(points)
            values = sum_values(values,diving_move_value(
                gpu[0],multipliers[i],am_first,
                regs[player_idx+3],
                regs[second_player_idx+3],
                regs[player_idx],
                regs[second_player_idx],
                len(gpu)))
            debug(f"diving values: {values}")

    debug(values)
    act = VAL_ACT[argmax(values)]
    print(act)


# def best_move(gpu,pos):
    
#     max_pos = len(gpu) - 1
#     if pos < max_pos and gpu[pos+1] == '#':
#         act = up
#     elif pos+2 < max_pos and gpu[pos+1] == '.' and gpu[pos+2] == '#':
#         act = left
#     elif pos+3 < max_pos and gpu[pos+1] == '.' and gpu[pos+2] == '.' and gpu[pos+3] == '#':
#         act = down
#     else:
#         act = right    
    
#     return act
