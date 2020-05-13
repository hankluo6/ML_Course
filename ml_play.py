"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.externals import joblib
from os import path
import numpy as np

def ml_loop(side: str):
    """
    The main loop for the machine learning process
    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```
    @param side The side which this script is executed for. Either "1P" or "2P".
    """
    class Model(nn.Module): #model4
        def __init__(self, input_shape):
            super().__init__()
            self.nn1 = nn.Linear(input_shape, 128)
            self.nn2 = nn.Linear(128, 256)
            self.nn3 = nn.Linear(256, 512)
            self.nn4 = nn.Linear(512, 1024)
            self.nn5 = nn.Linear(1024, 1)
        def forward(self, x):
            x = F.relu(self.nn1(x))
            x = F.relu(self.nn2(x))
            x = F.relu(self.nn3(x))
            x = F.relu(self.nn4(x))
            x = self.nn5(x)
            return x
            
 
    '''class Model(nn.Module): #model5
        def __init__(self, input_shape):
            super().__init__()
            self.nn1 = nn.Linear(input_shape, 256)
            self.nn2 = nn.Linear(256, 512)
            self.nn3 = nn.Linear(512, 1024)
            self.nn4 = nn.Linear(1024, 3)
        def forward(self, x):
            x = F.relu(self.nn1(x))
            x = F.relu(self.nn2(x))
            x = F.relu(self.nn3(x))
            x = self.nn4(x)
            return x'''
    class ActionModel(nn.Module):
        def __init__(self, input_shape):
            super().__init__()
            self.nn1 = nn.Linear(input_shape, 128)
            self.nn2 = nn.Linear(128, 3)
        def forward(self, x):
            x = F.relu(self.nn1(x))
            x = self.nn2(x)
            return x
    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    filename = path.join(path.dirname(__file__), 'save', 'model.ckpt')
    model = Model(6).to(device)
    model.load_state_dict(torch.load(filename))
    filename = path.join(path.dirname(__file__), 'save', 'nn_scaler.pickle')
    scaler = joblib.load(filename) 
    filename = path.join(path.dirname(__file__), 'save', 'ActionModel.ckpt')
    actionModel = ActionModel(5).to(device)
    actionModel.load_state_dict(torch.load(filename))
    filename = path.join(path.dirname(__file__), 'save', 'ActionNN_scaler.pickle')
    actionScaler = joblib.load(filename) 

    direction = True

    def move_to(player, pred):
    #move platform to predicted position to catch ball 
        if player == '1P':
            if scene_info["platform_1P"][0]+20  > (pred-10) and scene_info["platform_1P"][0]+20 < (pred+10): return 0 # NONE
            elif scene_info["platform_1P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left
        else :
            if scene_info["platform_2P"][0]+20  > (pred-10) and scene_info["platform_2P"][0]+20 < (pred+10): return 0 # NONE
            elif scene_info["platform_2P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left

    def ml_loop_for_1P():
        '''if scene_info['ball_speed'][0] > 0 and scene_info['ball_speed'][1] > 0:
            ballDirection = 0
        if scene_info['ball_speed'][0] > 0 and scene_info['ball_speed'][1] < 0:
            ballDirection = 1
        if scene_info['ball_speed'][0] < 0 and scene_info['ball_speed'][1] > 0:
            ballDirection = 2
        if scene_info['ball_speed'][0] < 0 and scene_info['ball_speed'][1] < 0:
            ballDirection = 3'''
        x = scene_info['ball'] + scene_info['ball_speed'] + (scene_info['blocker'][0],) + ((1,) if direction else (0,))
        #x = scene_info['ball'] + scene_info['ball_speed'] + (scene_info['platform_1P'][0],) + (scene_info['blocker'][0],) + ((1,) if direction else (0,)) + (ballDirection,)
        x = torch.tensor(x).reshape(1, -1)
        x = scaler.transform(x)
        x = torch.tensor(x).reshape(1, -1).float()
        y = model(x)
        '''y = torch.max(y, 1)[1]
        if y == 0:
            return 0
        elif y == 1:
            return 1
        else:
            return 2'''
        y = 5 * round(y.item() / 5.0)
        if y < 0:
            y = 0
        elif y > 195:
            y = 195
        if scene_info['ball'][1] >= 415 - scene_info['ball_speed'][1] and scene_info["platform_1P"][0] < y < scene_info["platform_1P"][0] + 40:
            x = (scene_info['ball'][0],) + scene_info['ball_speed'] + (scene_info['blocker'][0],) + ((1,) if direction else (0,))
            x = torch.tensor(x).reshape(1, -1)
            x = actionScaler.transform(x)
            x = torch.tensor(x).reshape(1, -1).float()
            case = actionModel(x)
            case = torch.max(case, 1)
            case = case[1].item()
            if case == 0:
                return 1
            elif case == 1:
                return 2
            else:
                return 0
        elif scene_info['platform_1P'][0] + 20 > y:
            return 2
        elif scene_info['platform_1P'][0] + 20 < y:
            return 1
        else:
            return 0

    def ml_loop_for_2P():  # as same as 1P
        if scene_info["ball_speed"][1] > 0 : 
            return move_to(player = '2P',pred = 100)
        else : 
            x = ( scene_info["platform_2P"][1]+30-scene_info["ball"][1] ) // scene_info["ball_speed"][1] 
            pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x) 
            bound = pred // 200 
            if (bound > 0):
                if (bound%2 == 0):
                    pred = pred - bound*200 
                else :
                    pred = 200 - (pred - 200*bound)
            elif (bound < 0) :
                if bound%2 ==1:
                    pred = abs(pred - (bound+1) *200)
                else :
                    pred = pred + (abs(bound)*200)
            return move_to(player = '2P',pred = pred)

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()
        if scene_info['frame'] == 1:
            if scene_info['blocker'][0] > last_block:
                direction = True
            else:
                direction = False
        last_block = scene_info["blocker"][0]

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            ball_served = True
        else:
            if side == "1P":
                command = ml_loop_for_1P()
            else:
                command = ml_loop_for_2P()
            if command == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            elif command == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            else:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})