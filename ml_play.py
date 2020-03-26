"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)
from pygame.math import Vector2


def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False

    last_ball_pos = (0, 0)
    #down = False
    action = PlatformAction.NONE
    platform_width = 40
    ball_width = 5

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()
        ball_pos = scene_info.ball
        platform_pos = scene_info.platform
        
        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        fall_point = calculate_fall_point(last_ball_pos, ball_pos)
        if fall_point > platform_pos[0] + platform_width / 2:
            action = PlatformAction.MOVE_RIGHT
        elif fall_point < platform_pos[0] + platform_width / 2:
            action = PlatformAction.MOVE_LEFT
        else:
            action = PlatformAction.NONE
        last_ball_pos = ball_pos

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:
            comm.send_instruction(scene_info.frame, action)

def calculate_fall_point(last_ball_pos, ball_pos):
    if last_ball_pos[1] >= ball_pos[1]: 
        return 100
    else:
        m = (last_ball_pos[1] - ball_pos[1]) / (last_ball_pos[0] - ball_pos[0])
        b = ball_pos[1] - m * ball_pos[0]
        x = (400 - b) / m
        if x < 200 and x > 0:
            return x
        else: 
            if m < 0: #move left
                if x < -200:
                    return 200 + (x + 200)
                else:
                    return -x
            else: #move right
                if x > 400:
                    return x - 400
                else:
                    return 200 - (x - 200)
