"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import math
import random
from mlgame.gamedev import physics
from pygame import Rect
from pygame.math import Vector2



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

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here

    # 2. Inform the game process that ml process is ready
    NEED_SLICE = True
    ball_served = False
    platform_1P_y = 420
    platform_2P_y = 50
    random.seed = 2
    lastX, lastY, x, y = 100, 415, 100, 415
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()
        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            ball_served = False
            NEED_SLICE = True
            lastX, lastY, x, y = 98, 415, 98, 415
            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue
        #TODO blocker edge, let ball can over the blocker, use the enemy possible point average, blue has bug in reflection
        # 3.3. Put the code here to handle the scene information
        if scene_info["frame"] != 0 and (scene_info["blocker"][0] > last_block or scene_info["blocker"][0] == 0):
            blockDirection = True
        else:
            blockDirection = False
        last_block = scene_info["blocker"][0]
        #x = Rect(56,261,5,5)
        #y = Rect(63,254,5,5)
        #z = Rect(62,240,30,20)
        #print(predict(x, y, z))
        lastX, lastY = x, y
        x, y = scene_info['ball']

        lastRect = Rect(63, 254, 5, 5)
        xRect = Rect(70, 247, 5, 5)
        blockRect = Rect(160, 240, 30, 20)
        if side == '1P':
            times = (2 if scene_info['ball_speed'][1] < 0 else 1)
            fall_point, d, blockDirection, blockPosX, speed, _ = predict(lastX, lastY, x, y, scene_info['ball_speed'][0], scene_info['ball_speed'][1], blockDirection, scene_info['blocker'][0], times, side)
            fall_point = 5 * round(fall_point / 5.0)
            if scene_info['ball'][1] + 5 >= 420 - scene_info['ball_speed'][1] and fall_point == scene_info["platform_1P"][0] + 20:
                case = chooseCase(d, 415, blockDirection, blockPosX, scene_info, speed)
                if case == 1:
                    action = 1 if scene_info["ball_speed"][0] > 0 else 2
                elif case == 2:
                    action = 0
                else:
                    action = 1 if scene_info["ball_speed"][0] < 0 else 2
            elif fall_point > scene_info["platform_1P"][0] + 20:
                action = 1
            elif fall_point < scene_info["platform_1P"][0] + 20:
                action = 2
            else:
                action = 0
        else:
            times = (2 if scene_info['ball_speed'][1] > 0 else 1)
            fall_point, d, blockDirection, blockPosX, speed, _ = predict(lastX, lastY, x, y, scene_info['ball_speed'][0], scene_info['ball_speed'][1], blockDirection, scene_info['blocker'][0], times)

            fall_point = 5 * round(fall_point / 5.0)
            if scene_info['ball'][1] + scene_info['ball_speed'][1] <= 80 and fall_point == scene_info["platform_2P"][0] + 20:
                case = chooseCase(d, 80, blockDirection, blockPosX, scene_info, speed)
                if case == 1:
                    action = 1 if scene_info["ball_speed"][0] > 0 else 2
                elif case == 2:
                    action = 0
                else:
                    action = 1 if scene_info["ball_speed"][0] < 0 else 2
            elif fall_point > scene_info["platform_2P"][0] + 20:
                action = 1
            elif fall_point < scene_info["platform_2P"][0] + 20:
                action = 2
            else:
                action = 0
        if not ball_served:
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            ball_served = True
        else:
            #if side == '1P':
                #print(scene_info['frame'])
                #print(scene_info['ball'], scene_info['platform_1P'], s_fall_point, '1p')
                #print(scene_info['ball'], scene_info['platform_2P'], s_fall_point, '2p')
            if action == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            elif action == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            else :
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})


def predict3(scene_info, move_direction): #block pos need update
    x, y = scene_info['ball']
    speedX, speedY = abs(scene_info['speed'][0]), abs(scene_info['speed'][1])
    if scene_info['speed'][1] > 0:
        if scene_info['speed'][0] < 0: #left-down
            success, pos = check_botton(x, y, speedX, speedY, 'left-down', ball_direction, move_direction, blockPosX)
            if success:
                return pos
            success, pos = check_edge()
            if success:
                return pos
            pos = check_wall()
            return pos
        else: #right-down
            success, pos = check_botton()
            if success:
                return pos
            success, pos = check_edge()
            if success:
                return pos
            pos = check_wall()
            return pos
    else:
        if scene_info['speed'][0] < 0: #left-up
            success, pos = check_botton()
            if success:
                return pos
            success, pos = check_edge()
            if success:
                return pos
            pos = check_wall()
            return pos
        else: #right-up
            success, pos = check_botton()
            if success:
                return pos
            success, pos = check_edge()
            if success:
                return pos
            pos = check_wall()
            return pos

def check_botton(x, y, speedX, speedY, ballDirection : str, blockDirection : bool, blockPosX : int) -> (bool, (int, int)):
    if ballDirection == 'left-down' or ballDirection == 'right-down':
        (lower, upper), blockDirection = predict_block(x, y, speedY, True, blockDirection, blockPosX)
        f_length = math.floor((240 - y - 5) / float(speedY))
        c_length = math.ceil((240 - y - 5) / float(speedY))
        remainder = (240 - y - 5) % speedY
    else:
        (lower, upper), blockDirection = predict_block(x, y, speedY, False, blockDirection, blockPosX)
        f_length = math.floor((y - 260) / float(speedY))
        c_length = math.ceil((y - 260) / float(speedY))
        remainder = (y - 260) % speedY

    if ballDirection == 'left-down' and y <= 235: # <= or < ?
        predictX, predictY = x - f_length * speedX, y + f_length * speedY
        if lower - 2 <= predictX - remainder <= upper + 2 and bounce_off_ip(predictX, predictY, -speedX, speedY, blockDirection, lower): # let range bigger
            return (True, (x - c_length * speedX, 235))
    elif ballDirection == 'right-down' and y <= 235:
        predictX, predictY = x + f_length * speedX, y + f_length * speedY
        if lower - 2 <= predictX + remainder <= upper + 2 and bounce_off_ip(predictX, predictY, speedX, speedY, blockDirection, lower): # the range need to edit
            return (True, (x + c_length * speedX, 235))
    elif ballDirection == 'left-top' and y >= 260:
        predictX, predictY = x - f_length * speedX, y - f_length * speedY
        if lower - 2 <= predictX - remainder <= upper + 2 and bounce_off_ip(predictX, predictY, -speedX, -speedY, blockDirection, lower): # check
            return (True, (x - c_length * speedX, 260))
    elif ballDirection == 'right-down' and y >= 260:
        predictX, predictY = x + f_length * speedX, y - f_length * speedY
        if lower - 2 <= predictX + remainder <= upper + 2 and bounce_off_ip(predictX, predictY, speedX, -speedY, blockDirection, lower): # check
            return (True, (x + c_length * speedX, 260))
    return (False, (0, 0))

def check_edge(x, y, speedX, speedY, ballDirection : str, blockDirection : bool, blockPosX : int) -> (bool, (int, int)):
    bx = blockPosX
    #if ballDirection == 'left-down':
        
def check_wall():
    pass

def predict_block(length, blockDirection, blockPosX):
    if blockDirection:
        if math.ceil((170 - blockPosX) / 3.0) < length:
            lower = 170 - 3 * (length - math.ceil((170 - blockPosX) / 3.0))
            upper = lower + 30
        else:
            lower = blockPosX + (length) * 3
            upper = lower + 30
    else:
        if math.ceil((blockPosX - 0) / 3.0) < length:
            lower = 0 + 3 * (length - math.ceil((blockPosX - 0) / 3.0))
            upper = lower + 30
        else:
            lower = blockPosX - (length) * 3
            upper = lower + 30
    return (lower, upper), blockDirection

def predict(lastX, lastY, x, y, speedX, speedY, blockDirection, blockPosX, times, side = '2P'):
    pred = 0
    bomb = False
    if speedX == 0:
        return 100, 100, blockDirection, blockPosX, bomb, speedX
    while times > 0:
        x += speedX
        y += speedY
        if blockPosX + 3 >= 170 and blockDirection:
            blockPosX = 170
            blockDirection = False
        elif blockPosX - 3 <= 0 and not blockDirection:
            blockPosX = 0
            blockDirection = True
        else:
            blockPosX = blockPosX + (3 if blockDirection else -3)
        
        # ball hits the play_area
        if x <= 0:
            x = 0
            speedX *= -1
        elif x >= 195:
            x = 195
            speedX *= -1
        
        # ball hits the platform
        if y <= 80:
            if times != 1:
                y = 80
                speedY *= -1
            else:
                pred = (x - speedX) + ((y - speedY) - 80) if speedX > 0 else (x - speedX) - ((y - speedY) - 80) # check
                Rpred = x
            times -= 1
        elif y >= 415:
            if times != 1:
                y = 415
                speedY *= -1
            else:
                pred = (x - speedX) + (415 - (y - speedY)) if speedX > 0 else (x - speedX) - (415 - (y - speedY)) # check
                Rpred = x
            times -= 1

        # ball hits the blocker
        lastRect = Rect(lastX, lastY, 5, 5)
        xRect = Rect(x, y, 5, 5)
        blockRect = Rect(blockPosX, 240, 30, 20)
        if moving_collide_or_contact(lastRect, xRect, blockRect):
            x, y, speedX, tmp_speedY = bounce_off_ip(x, y, speedX, speedY, blockDirection, blockPosX)
            if times == 1 and tmp_speedY != speedY:
                times += 1
            elif times == 2 and tmp_speedY != speedY:
                times -= 1
                bomb = True
            speedY = tmp_speedY
        lastX = x
        lastY = y
    
    return pred, Rpred, blockDirection, blockPosX, speedX, bomb


def predict2(lastX, lastY, x, y, speedX, speedY, blockDirection, blockPosX, times, side):
    pred = 0
    if speedX == 0:
        return 100
    while times > 0:
        if speedY > 0:
            # check collide blocker
            length = math.floor((240 - y - 5) / abs(speedY))
            (lower, upper), direction = predict_block(math.ceil((240 - y - 5) / abs(speedY)), blockDirection, blockPosX)
            newLastX = x + length * speedX
            newLastY = y + length * speedY
            newX = newLastX + speedX
            newY = newLastY + speedY
            lastRect = Rect(newLastX, newLastY, 5, 5)
            xRect = Rect(newX, newY, 5, 5)
            blockRect = Rect(lower, 240, 30, 20)
            if side == '1P':
                print(newLastX, newLastY, newX, newY, times)
            if 195 >= newLastX >= 0 and 195 >= newX >= 0 and 415 >= newLastY >= 80 and 415 >= newY >= 80 and moving_collide_or_contact(lastRect, xRect, blockRect):
                afterX, afterY, afterSpeedX, afterSpeedY = bounce_off_ip(newX, newY, speedX, speedY, direction, blockPosX)
                if afterSpeedY != speedY:
                    if times == 1:
                        times += 1
                    elif times == 2:
                        times -= 1
                    x = afterX
                    y = afterY
                    speedX = afterSpeedX
                    speedY = afterSpeedY
                elif afterSpeedX != speedX:
                    x = afterX
                    y = afterY
                    speedX = afterSpeedX
                    speedY = afterSpeedY
            else:
                # check collide edge
                lx = blockPosX
                bx = x
                by = y
                direction = blockDirection
                if speedX > 0:
                    while bx + 5 <= lx and y <= 260: # <= or <
                        bx += speedX
                        by += speedY
                        if lx + 3 >= 170 and direction:
                            lx = 170
                        elif lx - 3 <= 0 and not direction:
                            lx = 0
                        else:
                            lx = lx + (3 if direction else -3)
                else:
                    while bx >= lx + 30 and y <= 260: # <= or <
                        bx += speedX
                        by += speedY
                        if lx + 3 >= 170 and direction:
                            lx = 170
                        elif lx - 3 <= 0 and not direction:
                            lx = 0
                        else:
                            lx = lx + (3 if direction else -3)
                newLastX = x - speedX
                newLastY = y - speedY
                newX = bx
                newY = by
                lastRect = Rect(newLastX, newLastY, 5, 5)
                xRect = Rect(newX, newY, 5, 5)
                blockRect = Rect(lx, 240, 30, 20) 
                if moving_collide_or_contact(lastRect, xRect, blockRect):
                    afterX, afterY, afterSpeedX, afterSpeedY = bounce_off_ip(newX, newY, speedX, speedY, direction, blockPosX)
                    if afterSpeedY != speedY:
                        if times == 1:
                            times += 1
                        elif times == 2:
                            times -= 1
                        x = afterX
                        y = afterY
                        speedX = afterSpeedX
                        speedY = afterSpeedY
                    elif afterSpeedX != speedX:
                        x = afterX
                        y = afterY
                        speedX = afterSpeedX
                        speedY = afterSpeedY
                else:
                    if speedX > 0:
                        w_length = math.floor((195 - x) / abs(speedX))
                        p_length = math.floor((415 - y - 5) / abs(speedY))
                        if w_length <= p_length:
                            x = 195
                            y = y + math.ceil((195 - x) / abs(speedX)) * speedY
                            speedX *= -1
                        if p_length <= w_length:
                            if times != 1:
                                x = x + math.ceil((415 - y - 5) / abs(speedY)) * speedX
                            else:
                                pred = x + p_length * speedX + (415 - math.floor((415 - y - 5) / abs(speedY)))
                            y = 415
                            speedY *= -1
                            times -= 1
                    else:
                        w_length = math.floor((x - 0) / abs(speedX))
                        p_length = math.floor((415 - y - 5) / abs(speedY))
                        if w_length <= p_length:
                            x = 0
                            y = y + math.ceil((x - 0) / abs(speedX)) * speedY
                            speedX *= -1
                        if p_length <= w_length:
                            if times != 1:
                                x = x + math.ceil((415 - y - 5) / abs(speedY)) * speedX
                            else:
                                pred = x + p_length * speedX - (415 - math.floor((415 - y - 5) / abs(speedY)))
                            y = 415
                            speedY *= -1
                            times -= 1
        else:
            # check collide blocker
            length = math.floor((y - 260) / abs(speedY))
            (lower, upper), direction = predict_block(math.ceil((y - 260) / abs(speedY)), blockDirection, blockPosX)
            newLastX = x + length * speedX
            newLastY = y + length * speedY
            newX = newLastX + speedX
            newY = newLastY + speedY
            lastRect = Rect(newLastX, newLastY, 5, 5)
            xRect = Rect(newX, newY, 5, 5)
            blockRect = Rect(lower, 240, 30, 20)
            if side == '1P':
                print(newLastX, newLastY, newX, newY, times)
            if 195 >= newLastX >= 0 and 195 >= newX >= 0 and 415 >= newLastY >= 80 and 415 >= newY >= 80 and moving_collide_or_contact(lastRect, xRect, blockRect):
                afterX, afterY, afterSpeedX, afterSpeedY = bounce_off_ip(newX, newY, speedX, speedY, direction, blockPosX)
                if afterSpeedY != speedY:
                    if times == 1:
                        times += 1
                    elif times == 2:
                        times -= 1
                    x = afterX
                    y = afterY
                    speedX = afterSpeedX
                    speedY = afterSpeedY
                elif afterSpeedX != speedX:
                    x = afterX
                    y = afterY
                    speedX = afterSpeedX
                    speedY = afterSpeedY
            else:
                # check collide edge
                lx = blockPosX
                bx = x
                by = y
                direction = blockDirection
                if speedX > 0:
                    while bx + 5 <= lx and y >= 235: # <= or <
                        bx += speedX
                        by += speedY
                        if lx + 3 >= 170 and direction:
                            lx = 170
                        elif lx - 3 <= 0 and not direction:
                            lx = 0
                        else:
                            lx = lx + (3 if direction else -3)
                else:
                    while bx >= lx + 30 and y >= 235: # <= or <
                        bx += speedX
                        by += speedY
                        if lx + 3 >= 170 and direction:
                            lx = 170
                        elif lx - 3 <= 0 and not direction:
                            lx = 0
                        else:
                            lx = lx + (3 if direction else -3)
                newLastX = x - speedX
                newLastY = y - speedY
                newX = bx
                newY = by
                lastRect = Rect(newLastX, newLastY, 5, 5)
                xRect = Rect(newX, newY, 5, 5)
                blockRect = Rect(lx, 240, 30, 20) 
                if moving_collide_or_contact(lastRect, xRect, blockRect):
                    afterX, afterY, afterSpeedX, afterSpeedY = bounce_off_ip(newX, newY, speedX, speedY, direction, blockPosX)
                    if afterSpeedY != speedY:
                        if times == 1:
                            times += 1
                        elif times == 2:
                            times -= 1
                        x = afterX
                        y = afterY
                        speedX = afterSpeedX
                        speedY = afterSpeedY
                    elif afterSpeedX != speedX:
                        x = afterX
                        y = afterY
                        speedX = afterSpeedX
                        speedY = afterSpeedY
                else:
                    if speedX > 0:
                        w_length = math.floor((195 - x) / abs(speedX))
                        p_length = math.floor((y - 80) / abs(speedY))
                        if w_length <= p_length:
                            x = 195
                            y = y + math.ceil((195 - x) / abs(speedX)) * speedY
                            speedX *= -1
                        if p_length <= w_length:
                            if times != 1:
                                x = x + math.ceil((y - 80) / abs(speedY)) * speedX
                            else:
                                pred = x + p_length * speedX + (80 - math.floor((y - 80) / abs(speedY)))
                            y = 415
                            speedY *= -1
                            times -= 1
                    else:
                        w_length = math.floor((x - 0) / abs(speedX))
                        p_length = math.floor((y - 80) / abs(speedY))
                        if w_length <= p_length:
                            x = 0
                            y = y + math.ceil((x - 0) / abs(speedX)) * speedY
                            speedX *= -1
                        if p_length <= w_length:
                            if times != 1:
                                x = x + math.ceil((y - 80) / abs(speedY)) * speedX
                            else:
                                pred = x + p_length * speedX - (80 - math.floor((y - 80) / abs(speedY)))
                            y = 415
                            speedY *= -1
                            times -= 1
    return pred

def moving_collide_or_contact(lastRect, curMoveRect, spriteRect):
    """
    Check if the moving sprite collides or contacts another sprite.

    @param moving_sprite The sprite that moves in the scene.
           It must contain `rect` and `last_pos` attributes, which both are `pygame.Rect`.
    @param sprite The sprite that will be collided or contacted by `moving_sprite`.
           It must contain `rect` attribute, which is also `pygame.Rect`.
    """
    # Generate the routine of 4 corners of the moving sprite
    move_rect = curMoveRect
    move_last_pos = lastRect
    routines = (
        (Vector2(move_last_pos.topleft), Vector2(move_rect.topleft)),
        (Vector2(move_last_pos.topright), Vector2(move_rect.topright)),
        (Vector2(move_last_pos.bottomleft), Vector2(move_rect.bottomleft)),
        (Vector2(move_last_pos.bottomright), Vector2(move_rect.bottomright))
    )
    # Check any of routines collides the rect
    ## Take the bottom and right into account when using the API of pygame
    rect_expanded = spriteRect.inflate(1, 1)
    for routine in routines:
        # Exclude the case that the `moving_sprite` goes from the surface of `sprite`
        if (not rect_expanded.collidepoint(routine[0]) and
            rect_collideline(spriteRect, routine)):
            return True

    return False

def bounce_off_ip(x, y, speedX, speedY, blockDirection, blockPosX):
    """
    Calculate the speed and position of the `bounce_obj` after it bounces off the `hit_obj`.
    The position of `bounce_obj_rect` and the value of `bounce_obj_speed` will be updated.

    This function should be called only when two objects are colliding.

    @param bounce_obj_rect The Rect of the bouncing object
    @param bounce_obj_speed The 2D speed vector of the bouncing object.
    @param hit_obj_rect The Rect of the hit object
    @param hit_obj_speed The 2D speed vector of the hit object
    """
    # Treat the hit object as an unmovable object
    speed_diff_x = speedX - (3 if blockDirection else -3)
    speed_diff_y = speedY
    # The relative position between top and bottom, and left and right
    # of two objects at the last frame
    rect_diff_bT_hB = 260 - y + speed_diff_y
    rect_diff_bB_hT = 240 - (y + 5) + speed_diff_y
    rect_diff_bL_hR = blockPosX + 30 - x + speed_diff_x
    rect_diff_bR_hL = blockPosX - (x + 5) + speed_diff_x
    # Get the surface distance from the bouncing object to the hit object
    # and the new position for the bouncing object if it really hit the object
    # according to their relative position
    ## The bouncing object is at the bottom
    if rect_diff_bT_hB < 0 and rect_diff_bB_hT < 0:
        surface_diff_y = rect_diff_bT_hB
        extract_pos_y = 260
    ## The bouncing object is at the top
    elif rect_diff_bT_hB > 0 and rect_diff_bB_hT > 0:
        surface_diff_y = rect_diff_bB_hT
        extract_pos_y = 240 - 5
    else:
        surface_diff_y = -1 if speed_diff_y > 0 else 1

    ## The bouncing object is at the right
    if rect_diff_bL_hR < 0 and rect_diff_bR_hL < 0:
        surface_diff_x = rect_diff_bL_hR
        extract_pos_x = blockPosX + 30
    ## The bouncing object is at the left
    elif rect_diff_bL_hR > 0 and rect_diff_bR_hL > 0:
        surface_diff_x = rect_diff_bR_hL
        extract_pos_x = blockPosX - 5
    else:
        surface_diff_x = -1 if speed_diff_x > 0 else 1


    # Calculate the duration to hit the surface for x and y coordination.
    time_hit_y = surface_diff_y / speed_diff_y
    time_hit_x = surface_diff_x / speed_diff_x

    # Squeeze to up or down
    if time_hit_y >= 0 and time_hit_y >= time_hit_x:
        speedY *= -1
        y = extract_pos_y

    # Squeeze to left or right
    if time_hit_x >= 0 and time_hit_y <= time_hit_x:
        speedX *= -1
        x = extract_pos_x
    return x, y, speedX, speedY

'''def moving_collide_or_contact(moving_sprite: Sprite, sprite: Sprite) -> bool:
    """
    Check if the moving sprite collides or contacts another sprite.

    @param moving_sprite The sprite that moves in the scene.
           It must contain `rect` and `last_pos` attributes, which both are `pygame.Rect`.
    @param sprite The sprite that will be collided or contacted by `moving_sprite`.
           It must contain `rect` attribute, which is also `pygame.Rect`.
    """
    # Generate the routine of 4 corners of the moving sprite
    move_rect = moving_sprite.rect
    move_last_pos = moving_sprite.last_pos
    routines = (
        (Vector2(move_last_pos.topleft), Vector2(move_rect.topleft)),
        (Vector2(move_last_pos.topright), Vector2(move_rect.topright)),
        (Vector2(move_last_pos.bottomleft), Vector2(move_rect.bottomleft)),
        (Vector2(move_last_pos.bottomright), Vector2(move_rect.bottomright))
    )

    # Check any of routines collides the rect
    ## Take the bottom and right into account when using the API of pygame
    rect_expanded = sprite.rect.inflate(1, 1)
    for routine in routines:
        # Exclude the case that the `moving_sprite` goes from the surface of `sprite`
        if (not rect_expanded.collidepoint(routine[0]) and
            rect_collideline(sprite.rect, routine)):
            return True

    return False'''

def line_intersect(line_a, line_b) -> bool:
    """
    Check if two line segments intersect

    @param line_a A tuple (Vector2, Vector2) representing both end points
           of line segment
    @param line_b Same as `line_a`
    """
    # line_a and line_b have the same end point
    if (line_a[0] == line_b[0] or
        line_a[1] == line_b[0] or
        line_a[0] == line_b[1] or
        line_a[1] == line_b[1]):
        return True

    # Set line_a to (u0, u0 + v0) and p0 = u0 + s * v0, and
    # set line_b to (u1, u1 + v1) and p1 = u1 + t * v1,
    # where u, v, p are vectors and s, t is in [0, 1].
    # If line_a and line_b intersects, then p0 = p1
    # -> u0 - u1 = -s * v0 + t * v1
    # -> | u0.x - u1.x |   | v0.x  v1.x | |-s |
    #    | u0.y - u1.y | = | v0.y  v1.y | | t |
    #
    # If left-hand vector is a zero vector, then two line segments has the same end point.
    # If the right-hand matrix is not invertible, then two line segments are parallel.
    # If none of above conditions is matched, find the solution of s and t,
    # if both s and t are in [0, 1], then two line segments intersect.

    v0 = line_a[1] - line_a[0]
    v1 = line_b[1] - line_b[0]
    det = v0.x * v1.y - v0.y * v1.x
    # Two line segments are parallel
    if det == 0:
        # TODO Determine if two lines overlap
        return False

    du = line_a[0] - line_b[0]
    s_det = v1.x * du.y - v1.y * du.x
    t_det = v0.x * du.y - v0.y * du.x

    if ((det > 0 and 0 <= s_det <= det and 0 <= t_det <= det) or
        (det < 0 and det <= s_det <= 0 and det <= t_det <= 0)):
        return True

    return False

def rect_collideline(rect: Rect, line) -> bool:

    """
    Check if line segment intersects with a rect

    @param rect The Rect of the target rectangle
    @param line A tuple (Vector2, Vector2) representing both end points
           of line segment
    """
    # Either of line ends is in the target rect.
    rect_expanded = rect.inflate(1, 1)  # Take the bottom and right line into account
    if rect_expanded.collidepoint(line[0]) or rect_expanded.collidepoint(line[1]):
        return True

    line_top = (Vector2(rect.topleft), Vector2(rect.topright))
    line_bottom = (Vector2(rect.bottomleft), Vector2(rect.bottomright))
    line_left = (Vector2(rect.topleft), Vector2(rect.bottomleft))
    line_right = (Vector2(rect.topright), Vector2(rect.bottomright))
    return (line_intersect(line_top, line) or
        line_intersect(line_bottom, line) or
        line_intersect(line_left, line) or
        line_intersect(line_right, line))

def chooseCase(x, y, blockDirection, blockPosX, scene_info, speed):
    s = (True if abs(scene_info['ball_speed'][0]) != abs(scene_info['ball_speed'][1]) else False)
    if speed > 0:
        sliceSpeed = speed if s else speed + 3
        normalSpeed = speed if not s else speed - 3
    else:
        sliceSpeed = speed if s else speed - 3
        normalSpeed = speed if not s else speed + 3
    _, _, _, _, _, bomb = predict(x, y, x, y, sliceSpeed, -scene_info['ball_speed'][1], blockDirection, blockPosX, 2)
    case = 1
    if bomb:
        _, _, _, _, _, bomb = predict(x, y, x, y, normalSpeed, -scene_info['ball_speed'][1], blockDirection, blockPosX, 2)
        case = 2
    if bomb:
        _, _, _, _, _, bomb = predict(x, y, x, y, -normalSpeed, -scene_info['ball_speed'][1], blockDirection, blockPosX, 2)
        case = 3
    return case
