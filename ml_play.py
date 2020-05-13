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
import random
from pygame import Rect
from pygame.math import Vector2
import math

def predict(x, y, speedX, speedY, blockDirection, blockPosX, times, side = '2P'):
    pred = 0
    bomb = False
    num = 0 #need delete
    collide = False
    mini, maxi = 100, 100
    if speedX == 0 or speedY == 0:
        return 100, 100, blockDirection, blockPosX, speedX, bomb, num, True, 100, 100
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
                                t = predict(newX, newY, sliceSpeed, -speedY, blockDirection, blockPosX, 1, num)
                                if t[-1] != False:
                                    record.append(t)
                                t = predict(newX, newY, normalSpeed, -speedY, blockDirection, blockPosX, 1, num)
                                if t[-1] != False:
                                    record.append(t)
                                t = predict(newX, newY, -normalSpeed, -speedY, blockDirection, blockPosX, 1, num)
                                if t[-1] != False:
                                    record.append(t)
                                mini = 1000
                                maxi = -1000
                                for i in record:
                                    if i[0] < mini:
                                        mini = i[0]
                                    if i[0] > maxi:
                                        maxi = i[0]
                                #pred = (mini + maxi) / 2.0
                                #record.append(predict(newX, newY, sliceSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                #record.append(predict(newX, newY, normalSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                #record.append(predict(newX, newY, -normalSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                #pred = (record[0][0], record[1][0], record[2][0]) / 3.0
                                #pred = (min(record[0][0], record[1][0], record[2][0]) + max(record[0][0], record[1][0], record[2][0])) / 2.0
                                #Rpred = pred
                                if len(record) == 0:
                                    return 100, 100, True, 0, 0, True, 0, False, 100, 100
                                else:
                                    pred, Rpred = (mini + maxi) / 2.0, (mini + maxi) / 2.0
                                    blockDirection, blockPosX, speedX, bomb, num = record[0][2:-3]
                            else:
                                #prevent recirsive overflow
                                #pred, Rpred, blockDirection, blockPosX, speedX, bomb, num = predict(newX, newY, speedX, -speedY, blockDirection, blockPosX, 1, num)
                                return 100, 100, True, 0, 0, True, 0, False, 100, 100
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
                                t = predict(newX, newY, sliceSpeed, -speedY, blockDirection, blockPosX, 1, num)
                                if t[-1] != False:
                                    record.append(t)
                                t = predict(newX, newY, normalSpeed, -speedY, blockDirection, blockPosX, 1, num)
                                if t[-1] != False:
                                    record.append(t)
                                t = predict(newX, newY, -normalSpeed, -speedY, blockDirection, blockPosX, 1, num)
                                if t[-1] != False:
                                    record.append(t)
                                mini = 1000
                                maxi = -1000
                                for i in record:
                                    if i[0] < mini:
                                        mini = i[0]
                                    if i[0] > maxi:
                                        maxi = i[0]
                                pred = (mini + maxi) / 2.0
                                #record.append(predict(newX, newY, sliceSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                #record.append(predict(newX, newY, normalSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                #record.append(predict(newX, newY, -normalSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                #pred = (record[0][0], record[1][0], record[2][0]) / 3.0
                                #pred = (min(record[0][0], record[1][0], record[2][0]) + max(record[0][0], record[1][0], record[2][0])) / 2.0
                                Rpred = pred
                                if len(record) == 0:
                                    return 100, 100, True, 0, 0, True, 0, False, 100, 100
                                else:
                                    pred, Rpred = (mini + maxi) / 2.0, (mini + maxi) / 2.0
                                    blockDirection, blockPosX, speedX, bomb, num = record[0][2:-3]
                            else:
                                #prevent recirsive overflow
                                #pred, Rpred, blockDirection, blockPosX, speedX, bomb, num = predict(newX, newY, speedX, -speedY, blockDirection, blockPosX, 1, num)
                                #_, _, _, _, _, _, _, False = predict(newX, newY, speedX, -speedY, blockDirection, blockPosX, 1, num)
                                return 100, 100, True, 0, 0, True, 0, False, 100, 100
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
                                #record.append(predict(newX, newY, sliceSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                t = predict(newX, newY, sliceSpeed, -speedY, blockDirection, blockPosX, 1, num)
                                if t[-1] != False:
                                    record.append(t)
                                t = predict(newX, newY, normalSpeed, -speedY, blockDirection, blockPosX, 1, num)
                                if t[-1] != False:
                                    record.append(t)
                                t = predict(newX, newY, -normalSpeed, -speedY, blockDirection, blockPosX, 1, num)
                                if t[-1] != False:
                                    record.append(t)
                                mini = 1000
                                maxi = -1000
                                for i in record:
                                    if i[0] < mini:
                                        mini = i[0]
                                    if i[0] > maxi:
                                        maxi = i[0]
                                #record.append(predict(newX, newY, normalSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                #record.append(predict(newX, newY, -normalSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                #pred = (record[0][0], record[1][0], record[2][0]) / 3.0
                                #pred = (min(record[0][0], record[1][0], record[2][0]) + max(record[0][0], record[1][0], record[2][0])) / 2.0
                                if len(record) == 0:
                                    return 100, 100, True, 0, 0, True, 0, False, 100, 100
                                else:
                                    pred, Rpred = (mini + maxi) / 2.0, (mini + maxi) / 2.0
                                    blockDirection, blockPosX, speedX, bomb, num = record[0][2:-3]
                                    #print(mini, maxi)
                            else:
                                #prevent recirsive overflow
                                #pred, Rpred, blockDirection, blockPosX, speedX, bomb, num = predict(newX, newY, speedX, -speedY, blockDirection, blockPosX, 1, num)
                                return 100, 100, True, 0, 0, True, 0, False, 100, 100
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
                                t = predict(newX, newY, sliceSpeed, -speedY, blockDirection, blockPosX, 1, num)
                                if t[-1] != False:
                                    record.append(t)
                                t = predict(newX, newY, normalSpeed, -speedY, blockDirection, blockPosX, 1, num)
                                if t[-1] != False:
                                    record.append(t)
                                t = predict(newX, newY, -normalSpeed, -speedY, blockDirection, blockPosX, 1, num)
                                if t[-1] != False:
                                    record.append(t)
                                mini = 1000
                                maxi = -1000
                                for i in record:
                                    if i[0] < mini:
                                        mini = i[0]
                                    if i[0] > maxi:
                                        maxi = i[0]
                                #record.append(predict(newX, newY, sliceSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                #record.append(predict(newX, newY, normalSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                #record.append(predict(newX, newY, -normalSpeed, -speedY, blockDirection, blockPosX, 1, num))
                                #pred = (record[0][0], record[1][0], record[2][0]) / 3.0
                                #pred = (min(record[0][0], record[1][0], record[2][0]) + max(record[0][0], record[1][0], record[2][0])) / 2.0
                                if len(record) == 0:
                                    return 100, 100, True, 0, 0, True, 0, False, 100, 100
                                else:
                                    pred, Rpred = (mini + maxi) / 2.0, (mini + maxi) / 2.0
                                    blockDirection, blockPosX, speedX, bomb, num = record[0][2:-3]
                                    #print(mini, maxi)
                            else:
                                #prevent recirsive overflow
                                #pred, Rpred, blockDirection, blockPosX, speedX, bomb, num = predict(newX, newY, speedX, -speedY, blockDirection, blockPosX, 1, num)
                                return 100, 100, True, 0, 0, True, 0, False, 100, 100
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
    return pred, Rpred, blockDirection, blockPosX, speedX, bomb, num, True, mini, maxi

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

def chooseCase(x, y, blockDirection, blockPosX, scene_info, speed, speedY, fall_point, side = '2P'):
    if speed == 0 or speedY == 0:
        return [1]
    s = (True if abs(scene_info['ball_speed'][0]) != abs(scene_info['ball_speed'][1]) else False)
    if speed > 0:
        sliceSpeed = speed if s else speed + 3
        normalSpeed = speed if not s else speed - 3
    else:
        sliceSpeed = speed if s else speed - 3
        normalSpeed = speed if not s else speed + 3
    '''_, _, _, _, _, bomb, _, c= predict(x, y, sliceSpeed, -scene_info['ball_speed'][1], blockDirection, blockPosX, 2, frames)
    case = 1
    if bomb:
        _, _, _, _, _, bomb, _, c = predict(x, y, normalSpeed, -scene_info['ball_speed'][1], blockDirection, blockPosX, 2, frames)
        case = 2
    if bomb:
        _, _, _, _, _, bomb, _, c = predict(x, y, -normalSpeed, -scene_info['ball_speed'][1], blockDirection, blockPosX, 2, frames)
        case = 3'''
    ans = []
    length = math.ceil((415 - 80) / float(abs(speedY))) * 2
    length2 = math.ceil((415 - 260) / float(abs(speedY))) * 2
    pred, _, _, _, _, bomb1, _, c1, mini, maxi = predict(x, y, sliceSpeed, -scene_info['ball_speed'][1], blockDirection, blockPosX, 2)
    mid = (mini + maxi) / 2.0
    if c1:
        if bomb1 and abs(x - pred) < length2 * 3:
            ans.append(1)
        elif not bomb1 and max(abs(x - mini), abs(x - maxi)) < length * 3 and abs(x - mid) < length * 3 / 2 and abs(max(abs(x - mini), abs(x - maxi)) - mid) < length * 3 / 2:
            ans.append(1)
    pred, _, _, _, _, bomb2, _, c2, mini, maxi = predict(x, y, normalSpeed, -scene_info['ball_speed'][1], blockDirection, blockPosX, 2)
    mid = (mini + maxi) / 2.0
    if c2:
        if not bomb2 and bomb2 and abs(x - pred) < length2 * 3:
            ans.append(2)
        elif max(abs(x - mini), abs(x - maxi)) < length * 3 and abs(x - mid) < length * 3 / 2 and abs(max(abs(x - mini), abs(x - maxi)) - mid) < length * 3 / 2:
            ans.append(2)
    pred, _, _, _, _, bomb3, _, c3, mini, maxi = predict(x, y, -normalSpeed, -scene_info['ball_speed'][1], blockDirection, blockPosX, 2)
    mid = (mini + maxi) / 2.0
    if c3:
        if bomb3 and abs(x - pred) < length2 * 3:
            ans.append(3)
        elif not bomb3 and max(abs(x - mini), abs(x - maxi)) < length * 3 and abs(x - mid) < length * 3 / 2 and abs(max(abs(x - mini), abs(x - maxi)) - mid) < length * 3 / 2:
            ans.append(3)
    if len(ans) != 0:
        return ans
    if not c1:
        ans.append(1)
    if not c2:
        ans.append(2)
    if not c3:
        ans.append(3)
    if len(ans) != 0:
        return ans
    if not bomb1:
        ans.append(1)
    if not bomb2:
        ans.append(2)
    if not bomb3:
        ans.append(3)
    if len(ans) != 0:
        return ans
    return [2]
    #choose the distance smaller

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
            self.nn2 = nn.Linear(128, 256)
            self.nn3 = nn.Linear(256, 3)
        def forward(self, x):
            x = F.relu(self.nn1(x))
            x = F.relu(self.nn2(x))
            x = self.nn3(x)
            return x
    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here


    ball_served = False
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    filename = path.join(path.dirname(__file__), 'save', 'model4.ckpt')
    model = Model(6).to(device)
    model.load_state_dict(torch.load(filename))
    filename = path.join(path.dirname(__file__), 'save', 'nn_scaler4.pickle')
    scaler = joblib.load(filename) 
    filename = path.join(path.dirname(__file__), 'save', 'ActionModel5.ckpt')
    actionModel = ActionModel(5).to(device)
    actionModel.load_state_dict(torch.load(filename))
    filename = path.join(path.dirname(__file__), 'save', 'ActionNN_scaler5.pickle')
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
        if scene_info['ball'][1] + 5 >= 420 - scene_info['ball_speed'][1] and scene_info["platform_1P"][0] < y < scene_info["platform_1P"][0] + 40:
            a, b = predict_blocker(blockDirection, scene_info['blocker'][0], 1)
            case = chooseCase(scene_info['ball'][0] + scene_info['ball_speed'][0], 415, b, a, scene_info, scene_info['ball_speed'][0], scene_info['ball_speed'][1], 0, '1P')
            action = -1
            for i in case:
                if i == 1 and scene_info['platform_1P'][0] != 0:
                    action = 1 if scene_info["ball_speed"][0] > 0 else 2
                    break
                elif i == 3 and scene_info['platform_1P'][0] != 160:
                    action = 1 if scene_info["ball_speed"][0] < 0 else 2
                    break
                elif i == 2:
                    action = 0
                    break
            if action == -1:
                action = case[-1]
            '''if case == 1:
                action = 1 if scene_info["ball_speed"][0] > 0 else 2
            elif case == 2:
                action = 0
            else:
                action = 1 if scene_info["ball_speed"][0] < 0 else 2'''
        elif y > scene_info["platform_1P"][0] + 20:
            action = 1
        elif y < scene_info["platform_1P"][0] + 20:
            action = 2
        else:
            action = 0
        return action
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
                blockDirection = True
            else:
                blockDirection = False
        if (scene_info['frame'] > 1) and (scene_info['blocker'][0] == 170 or scene_info['blocker'][0] == 0):
            blockDirection = not blockDirection
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