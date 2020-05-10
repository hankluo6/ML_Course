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
import torch


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
    blockDirection = True
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
            blockDirection = True
            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        if scene_info['frame'] == 1:
            if scene_info['blocker'][0] > last_block:
                blockDirection = True
            else:
                blockDirection = False
        if (scene_info['frame'] > 1) and (scene_info['blocker'][0] == 170 or scene_info['blocker'][0] == 0):
            blockDirection = not blockDirection
        last_block = scene_info["blocker"][0]

        x, y = scene_info['ball']

        lastRect = Rect(63, 254, 5, 5)
        xRect = Rect(70, 247, 5, 5)
        blockRect = Rect(160, 240, 30, 20)
        if side == '1P':
            #print(scene_info['ball'], scene_info['blocker'], scene_info['frame'])
            times = (2 if scene_info['ball_speed'][1] < 0 else 1)
            fall_point, d, nextBlockDirection, blockPosX, speed, _, nextFrames = predict(x, y, scene_info['ball_speed'][0], scene_info['ball_speed'][1], blockDirection, scene_info['blocker'][0], times, scene_info['frame'])
            fall_point = 5 * round(fall_point / 5.0)
            if fall_point < 20:
                fall_point = 20
            elif fall_point > 180:
                fall_point = 180
            if scene_info['ball'][1] + 5 >= 420 - scene_info['ball_speed'][1] and fall_point == scene_info["platform_1P"][0] + 20:
                case = chooseCase(d, 415, nextBlockDirection, blockPosX, scene_info, speed, nextFrames)
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
            #print(scene_info['ball'], scene_info['blocker'])
            fall_point, d, nextBlockDirection, blockPosX, speed, _, nextFrames = predict(x, y, scene_info['ball_speed'][0], scene_info['ball_speed'][1], blockDirection, scene_info['blocker'][0], times, scene_info['frame'])
            fall_point = 5 * round(fall_point / 5.0)
            if fall_point < 20:
                fall_point = 20
            elif fall_point > 180:
                fall_point = 180
            if scene_info['ball'][1] + scene_info['ball_speed'][1] <= 80 and fall_point == scene_info["platform_2P"][0] + 20:
                case = chooseCase(d, 80, nextBlockDirection, blockPosX, scene_info, speed, nextFrames)
                #case = random.choice([1, 2, 3])
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

def old_predict(x, y, speedX, speedY, blockDirection, blockPosX, times, frames, side = '2P'):
    pred = 0
    bomb = False
    num = frames
    if speedX == 0:
        return 100, 100, blockDirection, blockPosX, speedX, bomb, num
    while times > 0:
        if num % 200 == 0 and num != 0:
            speedX = speedX + (1 if speedX > 0 else -1)
            speedY = speedY + (1 if speedY > 0 else -1)
        num += 1
        lastX = x
        lastY = y
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
                pred, Rpred, blockDirection, blockPosX, speedX, bomb, num = predict(x, y, sliceSpeed, speedY, blockDirection, blockPosX, 1, num)
                times = 0
            else:
                pred = (x - speedX) + ((y - speedY) - 80) if speedX > 0 else (x - speedX) - ((y - speedY) - 80) # check
                Rpred = x
            times -= 1
        elif y >= 415:
            if times != 1:
                y = 415
                speedY *= -1
                pred, Rpred, blockDirection, blockPosX, speedX, bomb, num = predict(x, y, speedX, speedY, blockDirection, blockPosX, 1, num)
                times = 0
            else:
                pred = (x - speedX) + (415 - (y - speedY)) if speedX > 0 else (x - speedX) - (415 - (y - speedY)) # check
                Rpred = x
            times -= 1
        # ball hits the blocker
        lastRect = Rect(lastX, lastY, 5, 5)
        xRect = Rect(x, y, 5, 5)
        blockRect = Rect(blockPosX, 240, 30, 20)
        #if (260 >= y >= 240 or 260 >= lastY >= 240) and moving_collide_or_contact(lastRect, xRect, blockRect):
        if moving_collide_or_contact(lastRect, xRect, blockRect):
            x, y, speedX, tmp_speedY = bounce_off_ip(x, y, speedX, speedY, blockDirection, blockPosX)
            if times == 1 and tmp_speedY != speedY:
                times += 1
            elif times == 2 and tmp_speedY != speedY:
                times -= 1
                bomb = True
            speedY = tmp_speedY
    if pred < 0:
        pred = 0
    if pred > 195:
        pred = 195
    return pred, Rpred, blockDirection, blockPosX, speedX, bomb, num

def predict(x, y, speedX, speedY, blockDirection, blockPosX, times, frames, side = '2P'):
    pred = 0
    bomb = False
    num = frames
    collide = False
    if speedX == 0 or speedY == 0:
        return 100, 100, blockDirection, blockPosX, speedX, bomb, num
    while times > 0:
        t = False
        if speedY > 0: # move down
            # check ball hits the blocker
            length = math.floor((240 - (y + 5)) / float(abs(speedY)))
            ceilLength = math.ceil((240 - (y + 5)) / float(abs(speedY)))
            currentBlockerPos, currentBlockerDirection = predict_blocker(blockDirection, blockPosX, ceilLength)
            lastX = x + length * speedX
            lastY = y + length * speedY
            currentX = lastX + speedX
            currentY = lastY + speedY
            lastRect = Rect(lastX, lastY, 5, 5)
            xRect = Rect(currentX, currentY, 5, 5)
            blockRect = Rect(currentBlockerPos, 240, 30, 20)
            if length >= 0 and moving_collide_or_contact(lastRect, xRect, blockRect):
                x, y, speedX, newSpeedY = bounce_off_ip(currentX, currentY, speedX, speedY, currentBlockerDirection, currentBlockerPos)
                if times == 1 and newSpeedY != speedY:
                    times += 1
                    collide = True
                elif times == 2 and newSpeedY != speedY:
                    times -= 1
                    bomb = True
                speedY = newSpeedY
                blockDirection = currentBlockerDirection
                blockPosX = currentBlockerPos
                t = True
            if y < 260 and not t: # < or <=
            # check ball hits the blocker edge
                bx = x
                by = y
                lx, currentBlockerDirection = blockPosX, blockDirection
                if speedX > 0:
                    k = (bx <= lx) # < or <=
                else:
                    k = (bx >= lx)  # > or >=
                while k: # < or <=
                    bx += speedX
                    by += speedY
                    if lx + 3 >= 170 and currentBlockerDirection:
                        lx = 170
                        currentBlockerDirection = False
                    elif lx - 3 <= 0 and not currentBlockerDirection:
                        lx = 0
                        currentBlockerDirection = True
                    else:
                        lx = lx + (3 if currentBlockerDirection else -3)
                    lastX = bx - speedX
                    lastY = by - speedY
                    lastRect = Rect(lastX, lastY, 5, 5)
                    xRect = Rect(bx, by, 5, 5)
                    blockRect = Rect(lx, 240, 30, 20)
                    if moving_collide_or_contact(lastRect, xRect, blockRect):
                        x, y, speedX, newSpeedY = bounce_off_ip(bx, by, speedX, speedY, currentBlockerDirection, lx)
                        if times == 1 and newSpeedY != speedY:
                            times += 1
                            collide = True
                        elif times == 2 and newSpeedY != speedY:
                            times -= 1
                            bomb = True
                        speedY = newSpeedY
                        blockDirection = currentBlockerDirection
                        blockPosX = lx
                        t = True
                        break
                    if speedX > 0:
                        k = (bx <= lx)
                    else:
                        k = (bx >= lx)
            if not t:
            # check ball hits the boundary or platform
                if speedX > 0:
                    e_length = math.floor((195 - x) / float(abs(speedX)))
                    p_length = math.floor((415 - y) / float(abs(speedY)))
                    if e_length < p_length:
                        ceilLength = (math.ceil((195 - x) / float(abs(speedX))))
                        y = y + ceilLength * speedY
                        x = 195
                        speedX *= -1
                        blockPosX, blockDirection = predict_blocker(blockDirection, blockPosX, ceilLength)
                    else:
                        ceilLength = math.ceil((415 - y) / float(abs(speedY)))
                        newX = x + ceilLength * speedX
                        newY = 415
                        blockPosX, blockDirection = predict_blocker(blockDirection, blockPosX, ceilLength)
                        if times != 1:
                            s = (True if abs(speedX) != abs(speedY) else False)
                            if speedX > 0:
                                sliceSpeed = speedX if s else speedX + 3
                                normalSpeed = speedX if not s else speedX - 3
                            else:
                                sliceSpeed = speedX if s else speedX - 3
                                normalSpeed = speedX if not s else speedX + 3
                            if not collide:
                                record = []
                                record.append(predict(newX, newY, sliceSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                record.append(predict(newX, newY, normalSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                record.append(predict(newX, newY, -normalSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                #pred = (record[0][0], record[1][0], record[2][0]) / 3.0
                                pred = (min(record[0][0], record[1][0], record[2][0]) + max(record[0][0], record[1][0], record[2][0])) / 2.0
                                Rpred = pred
                                blockDirection, blockPosX, speedX, bomb, num = record[0][2:]
                            else:
                                #prevent recirsive overflow
                                pred, Rpred, blockDirection, blockPosX, speedX, bomb, num = predict(newX, newY, speedX, -speedY, blockDirection, blockPosX, 1, num)
                            times = 0
                        else:
                            remainder = 415 - (y + p_length * speedY)
                            pred = x + p_length * speedX + remainder
                            Rpred = newX
                            times = 0
                        speedY *= -1
                else:
                    e_length = math.floor((x - 0) / float(abs(speedX)))
                    p_length = math.floor((415 - y) / float(abs(speedY)))
                    if e_length < p_length:
                        ceilLength = (math.ceil((x - 0) / float(abs(speedX))))
                        y = y + ceilLength * speedY
                        x = 0
                        speedX *= -1
                        blockPosX, blockDirection = predict_blocker(blockDirection, blockPosX, ceilLength)
                    else:
                        ceilLength = (math.ceil((415 - y) / float(abs(speedY))))
                        newX = x + ceilLength * speedX
                        newY = 415
                        blockPosX, blockDirection = predict_blocker(blockDirection, blockPosX, ceilLength)
                        if times != 1:
                            s = (True if abs(speedX) != abs(speedY) else False)
                            if speedX > 0:
                                sliceSpeed = speedX if s else speedX + 3
                                normalSpeed = speedX if not s else speedX - 3
                            else:
                                sliceSpeed = speedX if s else speedX - 3
                                normalSpeed = speedX if not s else speedX + 3
                            if not collide:
                                record = [] 
                                record.append(predict(newX, newY, sliceSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                record.append(predict(newX, newY, normalSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                record.append(predict(newX, newY, -normalSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                #pred = (record[0][0], record[1][0], record[2][0]) / 3.0
                                pred = (min(record[0][0], record[1][0], record[2][0]) + max(record[0][0], record[1][0], record[2][0])) / 2.0
                                Rpred = pred
                                blockDirection, blockPosX, speedX, bomb, num = record[0][2:]
                            else:
                                #prevent recirsive overflow
                                pred, Rpred, blockDirection, blockPosX, speedX, bomb, num = predict(newX, newY, speedX, -speedY, blockDirection, blockPosX, 1, num)
                            times = 0
                        else:
                            remainder = 415 - (y + p_length * speedY)
                            pred = x + p_length * speedX - remainder
                            Rpred = newX
                            times = 0
                        speedY *= -1
        else: # move up
            # check ball hits the blocker
            length = math.floor((y - 260) / abs(speedY))
            ceilLength = math.ceil((y - 260) / abs(speedY))
            currentBlockerPos, currentBlockerDirection = predict_blocker(blockDirection, blockPosX, ceilLength)
            lastX = x + length * speedX
            lastY = y + length * speedY
            currentX = lastX + speedX
            currentY = lastY + speedY
            lastRect = Rect(lastX, lastY, 5, 5)
            xRect = Rect(currentX, currentY, 5, 5)
            blockRect = Rect(currentBlockerPos, 240, 30, 20)
            if length >= 0 and moving_collide_or_contact(lastRect, xRect, blockRect):
                x, y, speedX, newSpeedY = bounce_off_ip(currentX, currentY, speedX, speedY, currentBlockerDirection, currentBlockerPos)
                if times == 1 and newSpeedY != speedY:
                    times += 1
                    collide = True
                elif times == 2 and newSpeedY != speedY:
                    times -= 1
                    bomb = True
                speedY = newSpeedY
                blockDirection = currentBlockerDirection
                blockPosX = currentBlockerPos
                t = True
            if y > 235 and not t:
            # check ball hits the blocker edge
                bx = x
                by = y
                lx, currentBlockerDirection = blockPosX, blockDirection
                if speedX > 0:
                    k = (bx <= lx) # < or <=
                else:
                    k = (bx >= lx)  # > or >=
                while k and by > 235: # < or <=
                    bx += speedX
                    by += speedY
                    if lx + 3 >= 170 and currentBlockerDirection:
                        lx = 170
                        currentBlockerDirection = False
                    elif lx - 3 <= 0 and not currentBlockerDirection:
                        lx = 0
                        currentBlockerDirection = True
                    else:
                        lx = lx + (3 if currentBlockerDirection else -3)
                    lastX = bx - speedX
                    lastY = by - speedY
                    lastRect = Rect(lastX, lastY, 5, 5)
                    xRect = Rect(bx, by, 5, 5)
                    blockRect = Rect(lx, 240, 30, 20)
                    if moving_collide_or_contact(lastRect, xRect, blockRect):
                        x, y, speedX, newSpeedY = bounce_off_ip(bx, by, speedX, speedY, currentBlockerDirection, lx)
                        if times == 1 and newSpeedY != speedY:
                            times += 1
                            collide = True
                        elif times == 2 and newSpeedY != speedY:
                            times -= 1
                            bomb = True
                        speedY = newSpeedY
                        blockDirection = currentBlockerDirection
                        blockPosX = lx
                        t = True
                        break
                    if speedX > 0:
                        k = (bx <= lx)
                    else:
                        k = (bx >= lx)
            if not t:
            # check ball hits the boundary or platform
                if speedX > 0:
                    e_length = math.floor((195 - x) / float(abs(speedX)))
                    p_length = math.floor((y - 80) / float(abs(speedY)))
                    if e_length < p_length:
                        ceilLength = (math.ceil((195 - x) / float(abs(speedX))))
                        y = y + ceilLength * speedY
                        x = 195
                        speedX *= -1
                        blockPosX, blockDirection = predict_blocker(blockDirection, blockPosX, ceilLength)
                    else:
                        ceilLength = (math.ceil((y - 80) / float(abs(speedY))))
                        newX = x + ceilLength * speedX
                        newY = 80
                        blockPosX, blockDirection = predict_blocker(blockDirection, blockPosX, ceilLength)
                        if times != 1:
                            s = (True if abs(speedX) != abs(speedY) else False)
                            if speedX > 0:
                                sliceSpeed = speedX if s else speedX + 3
                                normalSpeed = speedX if not s else speedX - 3
                            else:
                                sliceSpeed = speedX if s else speedX - 3
                                normalSpeed = speedX if not s else speedX + 3
                            if not collide:
                                record = [] 
                                record.append(predict(newX, newY, sliceSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                record.append(predict(newX, newY, normalSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                record.append(predict(newX, newY, -normalSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                #pred = (record[0][0], record[1][0], record[2][0]) / 3.0
                                pred = (min(record[0][0], record[1][0], record[2][0]) + max(record[0][0], record[1][0], record[2][0])) / 2.0
                                Rpred = pred
                                blockDirection, blockPosX, speedX, bomb, num = record[0][2:]
                            else:
                                #prevent recirsive overflow
                                pred, Rpred, blockDirection, blockPosX, speedX, bomb, num = predict(newX, newY, speedX, -speedY, blockDirection, blockPosX, 1, num)
                            times = 0
                        else:
                            remainder = (y + p_length * speedY) - 80
                            pred = x + p_length * speedX + remainder
                            Rpred = newX
                            times = 0
                        speedY *= -1
                else:
                    e_length = math.floor((x - 0) / float(abs(speedX)))
                    p_length = math.floor((y - 80) / float(abs(speedY)))
                    if e_length < p_length:
                        ceilLength = (math.ceil((x - 0) / float(abs(speedX))))
                        y = y + ceilLength * speedY
                        x = 0
                        speedX *= -1
                        blockPosX, blockDirection = predict_blocker(blockDirection, blockPosX, ceilLength)
                    else:
                        ceilLength = (math.ceil((y - 80) / float(abs(speedY))))
                        newX = x + ceilLength * speedX
                        newY = 80
                        blockPosX, blockDirection = predict_blocker(blockDirection, blockPosX, ceilLength)
                        if times != 1:
                            s = (True if abs(speedX) != abs(speedY) else False)
                            if speedX > 0:
                                sliceSpeed = speedX if s else speedX + 3
                                normalSpeed = speedX if not s else speedX - 3
                            else:
                                sliceSpeed = speedX if s else speedX - 3
                                normalSpeed = speedX if not s else speedX + 3
                            if not collide:
                                record = [] 
                                record.append(predict(newX, newY, sliceSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                record.append(predict(newX, newY, normalSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                record.append(predict(newX, newY, -normalSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                #pred = (record[0][0], record[1][0], record[2][0]) / 3.0
                                pred = (min(record[0][0], record[1][0], record[2][0]) + max(record[0][0], record[1][0], record[2][0])) / 2.0
                                Rpred = pred
                                blockDirection, blockPosX, speedX, bomb, num = record[0][2:]
                            else:
                                #prevent recirsive overflow
                                pred, Rpred, blockDirection, blockPosX, speedX, bomb, num = predict(newX, newY, speedX, -speedY, blockDirection, blockPosX, 1, num)
                            times = 0
                        else:
                            remainder = (y + p_length * speedY) - 80
                            pred = x + p_length * speedX - remainder
                            Rpred = newX
                            times = 0
                        speedY *= -1
    if pred < 0:
        pred = 0
    if pred > 195:
        pred = 195
    return pred, Rpred, blockDirection, blockPosX, speedX, bomb, num

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

def chooseCase(x, y, blockDirection, blockPosX, scene_info, speed, frames):
    s = (True if abs(scene_info['ball_speed'][0]) != abs(scene_info['ball_speed'][1]) else False)
    if speed > 0:
        sliceSpeed = speed if s else speed + 3
        normalSpeed = speed if not s else speed - 3
    else:
        sliceSpeed = speed if s else speed - 3
        normalSpeed = speed if not s else speed + 3
    _, _, _, _, _, bomb, _ = predict(x, y, sliceSpeed, -scene_info['ball_speed'][1], blockDirection, blockPosX, 2, frames)
    case = 1
    if bomb:
        _, _, _, _, _, bomb, _ = predict(x, y, normalSpeed, -scene_info['ball_speed'][1], blockDirection, blockPosX, 2, frames)
        case = 2
    if bomb:
        _, _, _, _, _, bomb, _= predict(x, y, -normalSpeed, -scene_info['ball_speed'][1], blockDirection, blockPosX, 2, frames)
        case = 3
    return case

def predict_blocker(blockDirection, blockPosX, length):
    while length > 0:
        if blockPosX + 3 >= 170 and blockDirection:
            blockPosX = 170
            blockDirection = not blockDirection
        elif blockPosX - 3 <= 0 and not blockDirection:
            blockPosX = 0
            blockDirection = not blockDirection
        else:
            blockPosX = blockPosX + (3 if blockDirection else -3)
        length -= 1
    return blockPosX, blockDirection

