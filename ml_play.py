import math
import copy

class MLPlay:
    def __init__(self, player):
        self.player = player
        if self.player == "player1":
            self.player_no = 0
        elif self.player == "player2":
            self.player_no = 1
        elif self.player == "player3":
            self.player_no = 2
        elif self.player == "player4":
            self.player_no = 3
        self.car_vel = 0                            # speed initial
        self.car_pos = (0,0)                        # pos initial
        self.car_lane = self.car_pos[0] // 70       # lanes 0 ~ 8
        self.lanes = [35, 105, 175, 245, 315, 385, 455, 525, 595]  # lanes center
        self.target = None
        self.null = 0
        self.brake = 0
        self.speedUp = False
        self.maxVel = 0
        self.camera_vel = 1
        self.touch_ceiling = False
        self.counter = 100
        self.car_info = {}
        pass

    def update(self, scene_info):
        """
        9 grid relative position
        |     |     |     |
        |  1  |  2  |  3  |
        |     |  5  |     |
        |  4  |10c11|  6  | 
        |     |     |     |
        |  7  |  8  |  9  |
        |     |     |     |  
        """
        
        brakeCar = []
        '''computer_car = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[]}
        for car in scene_info['cars_info']:
            if car['id'] > 100:
                computer_car[car['pos'][0] // 70].append(car['pos'] + (car['id'], car['velocity']))
        for i in range(9):
            sorted(computer_car[i], key = lambda l:l[1])
        push = False
        for i in range(9):
            for j in range(len(computer_car[i]) - 1):
                if push:
                    brakeCar.append(computer_car[i][j + 1][2])
                if abs(computer_car[i][j + 1][1] - computer_car[i][j][1]) <= 165:
                    push = True
            if not push:
                if i != 0:
                    for j in range(len(computer_car[i - 1])):
                        for k in range(len(computer_car[i])):
                            if push:
                                brakeCar.append(computer_car[i][k][2])
                            if abs(computer_car[i][k][1] - computer_car[i - 1][j][1]) <= 165 and abs(computer_car[i][k][0] - computer_car[i - 1][j][0]) < 50:
                                push = True
                        if push:
                            break
                elif i != 8:
                    for j in range(len(computer_car[i + 1])):
                        for k in range(len(computer_car[i])):
                            if push:
                                brakeCar.append(computer_car[i][k][2])
                            if abs(computer_car[i][k][1] - computer_car[i + 1][j][1]) <= 165 and abs(computer_car[i][k][0] - computer_car[i + 1][j][0]) < 50:
                                push = True
                        if push:
                            break'''


        
        if len(self.car_info) != 0:
            for car in scene_info['cars_info']:
                if car['id'] in self.car_info:
                    if car['velocity'] != 0 and self.car_info.get(car['id']) - car['velocity'] > 0:
                        brakeCar.append(car['id'])
            self.car_info.clear()
        for car in scene_info['cars_info']:
            if car['id'] > 100:
                self.car_info[car['id']] = car['velocity']

        for car in scene_info['cars_info']:
            if car['id'] < 100:
                if self.maxVel < car['velocity']:
                    self.maxVel = car['velocity']
        if self.maxVel >= 13:
            if self.touch_ceiling:
                self.camera_vel = self.maxVel
            else:
                self.camera_vel = self.maxVel - 2
        elif self.maxVel == 0:
            self.camera_vel = 1
        else:
            if self.camera_vel < self.maxVel:
                self.camera_vel += 0.7
            elif self.camera_vel > self.maxVel + 1:
                self.camera_vel -= 0.7
            else:
                pass
        self.touch_ceiling = False # next frame camera speed

        def follow(car):
            if (self.car_pos[1] - 40) - (car["pos"][1] + 40) <= 5 + 8 * (self.car_vel - car["velocity"] + 1.7):
                if self.car_vel > car["velocity"] - 5:
                    return 'BRAKE'
                else:
                    return keepSpeed(car["velocity"] - 4.7)
            else:
                return keepSpeed(car["velocity"] + 1)

        def keepSpeed(speed):
            if self.car_vel >= speed:
                return None
            else:
                return 'SPEED'

        def check_grid():
            grid = set()
            speed_ahead = 100
            if self.car_pos[0] == 0:
                return
            if self.car_pos[0] < 35:
                grid.add(1)
                grid.add(4)
                grid.add(7)
            if self.car_pos[0] > 595: # right bound
                grid.add(3)
                grid.add(6)
                grid.add(9)
            for car in scene_info["cars_info"]:
                if car["id"] != self.player_no:
                    x = self.car_pos[0] - car["pos"][0] # x relative position
                    y = self.car_pos[1] - car["pos"][1] # y relative position
                    if self.car_pos[0] - 46 <= car['pos'][0] <= self.car_pos[0] + 46:
                        if self.car_pos[1] > 600:
                            if 80 <= y <= 500:
                                grid.add(2)
                                record[2].append(car)
                                if y < 200:
                                    if speed_ahead > car["velocity"]:
                                        speed_ahead = car["velocity"]
                                    grid.add(5)
                                    record[5].append(car)
                        else:
                            if 80 <= y <= 300:
                                grid.add(2)
                                record[2].append(car)
                                if y < 200:
                                    if speed_ahead > car["velocity"]:
                                        speed_ahead = car["velocity"]
                                    grid.add(5)
                                    record[5].append(car)
                        if -200 < y < 0:
                            grid.add(8)
                            record[8].append(car)
                    #if self.car_pos[0] <= car['pos'][0] <= self.car_pos[0] + 100 and self.lanes[car['pos'][0] // 70] != self.car_lane + 2:
                    if car['pos'][0] // 70 == self.car_lane + 1:
                        if self.car_pos[1] > 600:
                            if 80 < y < 500:
                                grid.add(3)
                                record[3].append(car)
                        else:
                            if 80 < y < 300:
                                grid.add(3)
                                record[3].append(car)
                        if -80 <= y <= 80:
                            grid.add(6)
                            record[6].append(car)
                        elif -300 < y < -80:
                            grid.add(9)
                            record[9].append(car)
                    #if self.car_pos[0] - 100 <= car['pos'][0] <= self.car_pos[0] and self.lanes[car['pos'][0] // 70] != self.car_lane - 2:
                    if car['pos'][0] // 70 == self.car_lane - 1:
                        if self.car_pos[1] > 600:
                            if 80 < y < 500:
                                grid.add(1)
                                record[1].append(car)
                        else:
                            if 80 < y < 300:
                                grid.add(1)
                                record[1].append(car)
                        if -80 <= y <= 80:
                            grid.add(4)
                            record[4].append(car)
                        elif -300 < y < -80:
                            grid.add(7)
                            record[7].append(car)
                    if -80 <= y <= 80:
                        if 40 < x <= 46:
                            grid.add(10)
                            record[10].append(car)
                        elif -40 > x >= -46:
                            grid.add(11)
                            record[11].append(car)

                    if 80 < y < 400: # y range need choose
                        topLine[car['pos'][0] // 70].append(car)
                    elif -80 <= y <= 80:
                        midLine[car['pos'][0] // 70].append(car)

            return move(grid = grid, speed_ahead = speed_ahead)
            
        def move(grid, speed_ahead):

            if (10 in grid):
                left = False
            else:
                for car in record[7]:
                    if (car['id'] < 101) and (car['pos'][1] - self.car_pos[1] < 100):
                        left = False
                        break
                else:
                    left = True
                for car in record[1]:
                    if (self.car_pos[1] - car['pos'][1] < 100 and car['velocity'] <= self.car_vel) or car['id'] in brakeCar:
                        left = False
                        break
                else:
                    left = True
            if (11 in grid):
                right = False
            else:
                for car in record[9]:
                    if (car['id'] < 101) and (car['pos'][1] - self.car_pos[1] < 100):
                        right = False
                        break
                else:
                    right = True
                for car in record[3]:
                    if (self.car_pos[1] - car['pos'][1] < 100 and car['velocity'] <= self.car_vel) or car['id'] in brakeCar:
                        right = False
                        break
                else:
                    right = True

            returnAns = []

            target = -1
            maxY = 0
            right_coin = []
            catchCoin = False

            if 10 in grid and 11 in grid:
                pass
            if 10 in grid:
                returnAns.append('MOVE_RIGHT')
            elif 11 in grid:
                returnAns.append('MOVE_LEFT')
            else:
                for coin in scene_info['coins']:
                    if 0 <= self.car_pos[1] - coin[1] <= 400:
                        frame = abs(coin[0] + 10 - self.car_pos[0]) / 3
                        target_y = predict_y(frame)
                        if target_y > coin[1] + 5 * frame: # can arrive
                            right_coin.append(coin)
                for coin in right_coin:
                    coin_lane = coin[0] // 70
                    for car in scene_info['cars_info']:
                        frame = (self.car_pos[1] - coin[1]) / 5
                        if car['pos'][0] // 70 == coin_lane and 0 < self.car_pos[1] - car['pos'][1] < 200 and car['pos'][1] > coin[1]:
                            if 0 < self.car_pos[1] - car['pos'][1] < 200:
                                break
                            if car['id'] in brakeCar:
                                break
                    else:
                        collide = False
                        for i in range(abs(coin_lane - self.car_lane)):
                            if coin_lane > self.car_lane or not right:
                                if len(topLine[self.car_lane + i + 1]) != 0:
                                    collide = True
                                    break
                            if coin_lane < self.car_lane or not left:
                                if len(topLine[self.car_lane - i - 1]) != 0:
                                    collide = True
                                    break
                        if not collide:
                            if maxY < coin[1]:
                                maxY = coin[1]
                                state = self.car_pos[0] % 3
                                remainder = (coin[0] + 10) % 3
                                if state == 0:
                                    if remainder == 1:
                                        target = coin[0] + 10 - 1
                                    elif remainder == 2:
                                        target = coin[0] + 10 + 1
                                    else:
                                        target = coin[0] + 10 
                                elif state == 1:
                                    if remainder == 1:
                                        target = coin[0] + 10
                                    elif remainder == 2:
                                        target = coin[0] + 10 - 1
                                    else:
                                        target = coin[0] + 10 + 1
                                else:
                                    if remainder == 1:
                                        target = coin[0] + 10 + 1
                                    elif remainder == 2:
                                        target = coin[0] + 10
                                    else:
                                        target = coin[0] + 10 - 1
                if target == -1 and self.car_pos[1] < 550:
                    for coin in right_coin:
                        coin_lane = coin[0] // 70
                        for car in scene_info['cars_info']:
                            frame = (self.car_pos[1] - coin[1]) / 5
                            if car['pos'][0] // 70 == coin_lane and 0 < self.car_pos[1] - car['pos'][1] < 200 and car['pos'][1] > coin[1]:
                                if 0 < self.car_pos[1] - car['pos'][1] < 200:
                                    break
                                if car['id'] in brakeCar:
                                    break
                        else:
                            if (coin[0] > self.car_pos[0] and not right) or (coin[0] < self.car_pos[0] and not left):
                                continue
                            if maxY < coin[1]:
                                maxY = coin[1]
                                state = self.car_pos[0] % 3
                                remainder = (coin[0] + 10) % 3
                                if state == 0:
                                    if remainder == 1:
                                        target = coin[0] + 10 - 1
                                    elif remainder == 2:
                                        target = coin[0] + 10 + 1
                                    else:
                                        target = coin[0] + 10 
                                elif state == 1:
                                    if remainder == 1:
                                        target = coin[0] + 10
                                    elif remainder == 2:
                                        target = coin[0] + 10 - 1
                                    else:
                                        target = coin[0] + 10 + 1
                                else:
                                    if remainder == 1:
                                        target = coin[0] + 10 + 1
                                    elif remainder == 2:
                                        target = coin[0] + 10
                                    else:
                                        target = coin[0] + 10 - 1
                            else:
                                pass
                            continue
                        '''if coin_lane > self.car_lane and right:
                            collide = False
                            for i in range(coin_lane - self.car_lane):
                                if collide:
                                    break
                                if i != coin_lane - self.car_lane - 1:
                                    f = (self.lanes[self.car_lane + i + 1] + 35) / self.car_pos[0]
                                else:
                                    f = (self.lanes[self.car_lane + i + 1] - 20) / self.car_pos[0]
                                for car in topLine[self.car_lane + i + 1]:
                                    if self.car_pos[1] - 40 <= car['pos'][1] + 3 * f + 40 and self.car_pos[1] > car['pos'][1]:
                                        collide = True
                                        break
                            if not collide:
                                if maxY < coin[1]:
                                    maxY = coin[1]
                                    state = self.car_pos[0] % 3
                                    remainder = (coin[0] + 10) % 3
                                    if state == 0:
                                        if remainder == 1:
                                            target = coin[0] + 10 - 1
                                        elif remainder == 2:
                                            target = coin[0] + 10 + 1
                                        else:
                                            target = coin[0] + 10 
                                    elif state == 1:
                                        if remainder == 1:
                                            target = coin[0] + 10
                                        elif remainder == 2:
                                            target = coin[0] + 10 - 1
                                        else:
                                            target = coin[0] + 10 + 1
                                    else:
                                        if remainder == 1:
                                            target = coin[0] + 10 + 1
                                        elif remainder == 2:
                                            target = coin[0] + 10
                                        else:
                                            target = coin[0] + 10 - 1
                        elif coin_lane < self.car_lane and left:
                            collide = False
                            for i in range(self.car_lane - coin_lane):
                                if collide:
                                    break
                                if i != self.car_lane - coin_lane - 1:
                                    f = (self.lanes[self.car_lane - i - 1] - 35) / self.car_pos[0]
                                else:
                                    f = (self.lanes[self.car_lane - i - 1] + 20) / self.car_pos[0]
                                for car in topLine[self.car_lane - i - 1]:
                                    if self.car_pos[1] - 40 <= car['pos'][1] + 3 * f + 40 and self.car_pos[1] > car['pos'][1]:
                                        collide = True
                                        break
                            if not collide:
                                if maxY < coin[1]:
                                    maxY = coin[1]
                                    state = self.car_pos[0] % 3
                                    remainder = (coin[0] + 10) % 3
                                    if state == 0:
                                        if remainder == 1:
                                            target = coin[0] + 10 - 1
                                        elif remainder == 2:
                                            target = coin[0] + 10 + 1
                                        else:
                                            target = coin[0] + 10 
                                    elif state == 1:
                                        if remainder == 1:
                                            target = coin[0] + 10
                                        elif remainder == 2:
                                            target = coin[0] + 10 - 1
                                        else:
                                            target = coin[0] + 10 + 1
                                    else:
                                        if remainder == 1:
                                            target = coin[0] + 10 + 1
                                        elif remainder == 2:
                                            target = coin[0] + 10
                                        else:
                                            target = coin[0] + 10 - 1
                        elif coin_lane == self.car_lane:
                            for car in scene_info['cars_info']:
                                if self.lanes[car['pos'][0] // 70] == self.car_lane and car['pos'][1] >= coin:
                                    break
                            else:
                                if maxY < coin[1]:
                                    maxY = coin[1]
                                    state = self.car_pos[0] % 3
                                    remainder = (coin[0] + 10) % 3
                                    if state == 0:
                                        if remainder == 1:
                                            target = coin[0] + 10 - 1
                                        elif remainder == 2:
                                            target = coin[0] + 10 + 1
                                        else:
                                            target = coin[0] + 10 
                                    elif state == 1:
                                        if remainder == 1:
                                            target = coin[0] + 10
                                        elif remainder == 2:
                                            target = coin[0] + 10 - 1
                                        else:
                                            target = coin[0] + 10 + 1
                                    else:
                                        if remainder == 1:
                                            target = coin[0] + 10 + 1
                                        elif remainder == 2:
                                            target = coin[0] + 10
                                        else:
                                            target = coin[0] + 10 - 1'''

                if target != -1:
                    if target > self.car_pos[0]:
                        returnAns.append('MOVE_RIGHT')
                    elif target < self.car_pos[0]:
                        returnAns.append('MOVE_LEFT')
                    else:
                        catchCoin = True
                        
            brake = False
            empty = False
            max_dis = 0
            for car in scene_info['cars_info']:
                '''if 80 < self.car_pos[1] - car['pos'][1] < 200 and car['pos'][0] - 46 <= self.car_pos[0] <= car['pos'][0] + 46: #change
                    if car['velocity'] < self.car_vel:
                        brake = True
                elif 80 < self.car_pos[1] - car['pos'][1] < 350 and car['pos'][0] - 46 <= self.car_pos[0] <= car['pos'][0] + 46:
                    if car['velocity'] < self.car_vel:
                        if car['id'] in brakeCar:
                            brake = True
                        else:
                            empty = True'''
                if 80 < self.car_pos[1] - car['pos'][1] < 200 and car['pos'][0] - 46 <= self.car_pos[0] <= car['pos'][0] + 46: #change
                    if car['velocity'] < self.car_vel:
                        elif follow(car) == 'BRAKE':
                            brake = True
                        elif follow(car) == None:
                            empty = True
                elif 80 < self.car_pos[1] - car['pos'][1] < 350 and car['pos'][0] - 46 <= self.car_pos[0] <= car['pos'][0] + 46:
                    if car['velocity'] < self.car_vel:
                        elif follow(car) == 'BRAKE':
                            brake = True
                        elif follow(car) == None:
                            empty = True
            if 'MOVE_LEFT' not in returnAns and 'MOVE_RIGHT' not in returnAns and not catchCoin: # no near coin 
                if 2 not in grid and 5 not in grid:
                    minVal = 1e9
                    idx = -1
                    for i in range(1, 5):
                        if len(scene_info['player' + str(i)]) != 0 and scene_info['player' + str(i)] != self.car_pos:
                            if -80 <= scene_info['player' + str(i)][1] - self.car_pos[1] <= 80 and abs(scene_info['player' + str(i)][0] - self.car_pos[0]) < minVal:
                               abs(scene_info['player' + str(i)][0] - self.car_pos[0])
                               idx = i
                    if idx != -1:
                        if self.car_pos[0] < scene_info['player' + str(idx)][0]:
                            returnAns.append('MOVE_RIGHT')
                        else:
                            returnAns.append('MOVE_LEFT')
                        #state = self.car_pos[0] % 3
                        #if state == 0:
                        #   target = 351
                        #elif state == 1:
                        #    target = 349
                        #else:
                        #    target = 350
                        #if self.car_pos[0] > target:
                        #    returnAns.append('MOVE_LEFT')
                        #elif self.car_pos[0] < target:
                        #    returnAns.append('MOVE_RIGHT')
                        #else:
                        #    pass
                    
                elif 2 in grid or 5 in grid:
                    for car in record[2]:
                        if car['pos'][0] // 70 == self.car_lane:
                            break
                    else:
                        if self.car_pos[0] > self.lanes[self.car_lane]:
                            returnAns.append('MOVE_LEFT')
                        else:
                            returnAns.append('MOVE_RIGHT')
                    if len(returnAns) == 0:
                        if left and 4 not in grid and right and 6 not in grid: 
                            if 1 not in grid and 3 not in grid:
                                if self.car_pos[0] < 350:
                                    returnAns.append('MOVE_RIGHT')
                                else:
                                    returnAns.append('MOVE_LEFT')
                            elif 1 not in grid:
                                returnAns.append('MOVE_LEFT')
                            elif 3 not in grid:
                                returnAns.append('MOVE_RIGHT')
                            else:

                                if len(record[1]) == 0: # in leftmost
                                    for car in scene_info['cars_info']:
                                        if car in brakeCar:
                                            if self.car_lane + 1 == car['pos'][0] // 70:
                                                break
                                    else:
                                        max_dis = [0, 0]
                                        max_dis[0] = max([car['pos'][1] for car in record[2]])
                                        max_dis[1] = max([car['pos'][1] for car in record[3]])

                                        max_speed = [0, 0]
                                        max_speed[0] = max([car['velocity'] for car in record[2]])
                                        max_speed[1] = max([car['velocity'] for car in record[3]])

                                        if max(max_speed) - min(max_speed) < 2:
                                            _, r = find_target(False, True)
                                            if r and self.car_pos[1] - max_dis[1] >= 100:
                                                returnAns.append('MOVE_RIGHT')
                                        if len(returnAns) == 0:
                                            if max_speed[0] <= max_speed[1] and self.car_pos[1] - max_dis[1] >= 100:
                                                returnAns.append('MOVE_RIGHT')
                                            elif max_dis[1] <= max_dis[0]:
                                                returnAns.append('MOVE_RIGHT')
                                elif len(record[3]) == 0:
                                    for car in scene_info['cars_info']:
                                        if car in brakeCar:
                                            if self.car_lane - 1 == car['pos'][0] // 70:
                                                break
                                    else:
                                        max_dis = [0, 0]
                                        max_dis[0] = max([car['pos'][1] for car in record[1]])
                                        max_dis[1] = max([car['pos'][1] for car in record[2]])

                                        max_speed = [0, 0]
                                        max_speed[0] = max([car['velocity'] for car in record[1]])
                                        max_speed[1] = max([car['velocity'] for car in record[2]])

                                        if max(max_speed) - min(max_speed) < 2:
                                            l, _ = find_target(True, False)
                                            if l and self.car_pos[1] - max_dis[0] >= 100:
                                                returnAns.append('MOVE_LEFT')
                                        if len(returnAns) == 0:
                                            if max_speed[0] >= max_speed[1] and self.car_pos[1] - max_dis[0] >= 100:
                                                returnAns.append('MOVE_LEFT')
                                            elif max_dis[0] <= max_dis[1]:
                                                returnAns.append('MOVE_LEFT')
                                else:
                                    left, right = False, False
                                    for car in scene_info['cars_info']:
                                        if car in brakeCar:
                                            if self.car_lane + 1 == car['pos'][0] // 70:
                                                right = True
                                            if self.car_lane - 1 == car['pos'][0] // 70:
                                                left = True

                                    max_dis = [0, 0, 0]
                                    max_dis[0] = max([car['pos'][1] for car in record[1]])
                                    max_dis[1] = max([car['pos'][1] for car in record[2]])
                                    max_dis[2] = max([car['pos'][1] for car in record[3]])

                                    max_speed = [0, 0, 0]
                                    max_speed[0] = max([car['velocity'] for car in record[1]])
                                    max_speed[1] = max([car['velocity'] for car in record[2]])
                                    max_speed[2] = max([car['velocity'] for car in record[3]])

                                    if max(max_speed) - min(max_speed) < 2:
                                        l, r = find_target(True, True)
                                        if l and self.car_pos[1] - max_dis[0] >= 100 and left:
                                            returnAns.append('MOVE_LEFT')
                                        elif r and self.car_pos[1] - max_dis[2] >= 100 and right:
                                            returnAns.append('MOVE_RIGHT')
                                    if len(returnAns) == 0:
                                        if max_speed[0] >= max_speed[1] and max_speed[0] >= max_speed[2] and self.car_pos[1] - max_dis[0] >= 100 and left:
                                            returnAns.append('MOVE_LEFT')
                                        elif max_speed[2] >= max_speed[1] and max_speed[2] >= max_speed[0] and self.car_pos[1] - max_dis[2] >= 100 and right:
                                            returnAns.append('MOVE_RIGHT')
                                        elif max_dis[0] <= max_dis[1] and max_dis[0] <= max_dis[2] and left:
                                            returnAns.append('MOVE_LEFT')
                                        elif max_dis[2] >= max_dis[1] and max_dis[2] >= max_dis[0] and right:
                                            returnAns.append('MOVE_RIGHT')
                        elif left and 4 not in grid:
                            if 1 not in grid:
                                returnAns.append('MOVE_LEFT')
                            else:
                                if len(record[1]) == 0:
                                    pass
                                else:
                                    for car in scene_info['cars_info']:
                                        if car in brakeCar:
                                            if self.car_lane - 1 == car['pos'][0] // 70:
                                                break
                                    else:
                                        max_dis = [0, 0]
                                        max_dis[0] = max([car['pos'][1] for car in record[1]])
                                        max_dis[1] = max([car['pos'][1] for car in record[2]])

                                        max_speed = [0, 0]
                                        max_speed[0] = max([car['velocity'] for car in record[1]])
                                        max_speed[1] = max([car['velocity'] for car in record[2]])

                                        if max(max_speed) - min(max_speed) < 2:
                                            l, _ = find_target(True, False)
                                            if l and self.car_pos[1] - max_dis[0] >= 100:
                                                returnAns.append('MOVE_LEFT')
                                        if len(returnAns) == 0:
                                            if max_speed[0] >= max_speed[1] and self.car_pos[1] - max_dis[0] >= 100:
                                                returnAns.append('MOVE_LEFT')
                                            elif max_dis[0] <= max_dis[1]:
                                                returnAns.append('MOVE_LEFT')
                        elif right and 6 not in grid:
                            if 3 not in grid:
                                returnAns.append('MOVE_RIGHT')
                            else:
                                if len(record[3]) == 0:
                                    pass
                                else:
                                    for car in scene_info['cars_info']:
                                        if car in brakeCar:
                                            if self.car_lane + 1 == car['pos'][0] // 70:
                                                break
                                    else:
                                        max_dis = [0, 0]
                                        max_dis[0] = max([car['pos'][1] for car in record[2]])
                                        max_dis[1] = max([car['pos'][1] for car in record[3]])

                                        max_speed = [0, 0]
                                        max_speed[0] = max([car['velocity'] for car in record[2]])
                                        max_speed[1] = max([car['velocity'] for car in record[3]])

                                        if max(max_speed) - min(max_speed) < 2:
                                            _, r = find_target(False, True)
                                            if r and self.car_pos[1] - max_dis[1] >= 100:
                                                returnAns.append('MOVE_RIGHT')
                                        if len(returnAns) == 0:
                                            if max_speed[0] <= max_speed[1] and self.car_pos[1] - max_dis[1] >= 100:
                                                returnAns.append('MOVE_RIGHT')
                                            elif max_dis[1] <= max_dis[0]:
                                                returnAns.append('MOVE_RIGHT')
                        else:
                            pass
                            
            if brake:
                returnAns.append('BRAKE')
            elif empty:
                pass
            else:
                returnAns.append('SPEED')

            return returnAns

        def find_target(left, right):
            target = self.car_pos[0]
            tmp = target // 70
            l = r = hasLeft = hasRight = False
            if right:
                imRight = False
                for i in range(tmp + 1, 9): 
                    if len(midLine[i]) != 0:
                        imRight = True
                    if len(midLine[i]) == 0 and len(topLine[i]) == 0 and not imRight:
                        r = True
                        break
                if tmp + 2 < 9 and len(midLine[tmp + 2]) == 0:
                    hasRight = True
            else:
                r = False
            if left:
                imLeft = False
                for i in range(tmp - 1, -1, -1):
                    if len(midLine[i]) != 0:
                        imLeft = True
                    if len(midLine[i]) == 0 and len(topLine[i]) == 0 and not imLeft:
                        l = True
                        break
                if tmp - 2 >= 0 and len(midLine[tmp - 2]) == 0:
                    hasLeft = True
            else:
                l = False

            if not l and not r:
                return [hasLeft, hasRight]

            return [l, r]

        def predict_y(frame, car = None):
            pos = self.car_pos[1]
            camera = self.camera_vel
            delay = False
            touch_ceiling = self.touch_ceiling
            maxVel = self.maxVel
            if car == None:
                car_vel = self.car_vel
            else:
                car_vel = car['velocity']
            for i in range(int(frame)):

                if not delay:
                    car_vel += 0.3
                    if car_vel > 14.5:
                        car_vel = 14.5
                delay = not delay
                for car in scene_info['cars_info']:
                    if car['id'] < 100:
                        if car['pos'][1] <= 390:
                            touch_ceiling = True
                        if car['velocity'] > maxVel:
                            maxVel = car['velocity']
                if car_vel > maxVel:
                    maxVel = car_vel

                if pos - 40 <= 350:
                    touch_ceiling = True

                pos = int(pos + camera - car_vel)

                #maxVel = car_vel # every user_car

                if maxVel >= 13:
                    if touch_ceiling:
                        camera = maxVel
                    else:
                        camera = maxVel - 2
                elif maxVel == 0:
                    camera = 1
                else:
                    if camera < maxVel:
                        camera += 0.7
                    elif camera > maxVel + 1:
                        camera -= 0.7
                    else:
                        pass
                touch_ceiling = False
                
            return pos
        
        def collide(frame, stay_frame, direction):
            pos = list(self.car_pos)
            camera = self.camera_vel
            delay = False
            touch_ceiling = self.touch_ceiling
            maxVel = self.maxVel
            car_vel = self.car_vel
            info = copy.deepcopy(scene_info['cars_info'])
            for car in info:
                car['pos'] = list(car['pos'])
                if car['id'] != self.player_no:
                    print(car['pos'])
            for i in range(int(frame)):

                if not delay:
                    car_vel += 0.3
                    if car_vel > 14.5:
                        car_vel = 14.5
                delay = not delay
                
                if direction:
                    pos[0] += 3
                else:
                    pos[0] -= 3
                
                #print(pos)
                for car in info:
                    if car["id"] != self.player_no:
                        car['pos'][1] = int(car['pos'][1] + camera - car['velocity'])
                        print(car['pos'], i)
                        if not((pos[0] - 20 > car['pos'][0] + 20 or car['pos'][0] - 20 > pos[0] + 20) or (pos[1] - 40 < car['pos'][1] + 40 or car['pos'][1] - 40 < pos[1] - 40)):
                            #print(pos, car['pos'])
                            return True
                    if car['id'] < 100:
                        if car['pos'][1] <= 390:
                            touch_ceiling = True
                        if car['velocity'] > maxVel:
                            maxVel = car['velocity']
                if car_vel > maxVel:
                    maxVel = car_vel

                if pos[1] - 40 <= 350:
                    touch_ceiling = True

                pos[1] = int(pos[1] + camera - car_vel)

                #maxVel = car_vel # every user_car

                if maxVel >= 13:
                    if touch_ceiling:
                        camera = maxVel
                    else:
                        camera = maxVel - 2
                elif maxVel == 0:
                    camera = 1
                else:
                    if camera < maxVel:
                        camera += 0.7
                    elif camera > maxVel + 1:
                        camera -= 0.7
                    else:
                        pass
                touch_ceiling = False
            
            for i in range(int(stay_frame)):
                if not delay:
                    car_vel += 0.3
                    if car_vel > 14.5:
                        car_vel = 14.5
                delay = not delay
                for car in info:
                    if car["id"] != self.player_no:
                        car['pos'][1] = int(car['pos'][1] + camera - car['velocity'])
                        if not((pos[0] - 20 > car['pos'][0] + 20 or car['pos'][0] - 20 > pos[0] + 20) or (pos[1] - 40 < car['pos'][1] + 40 or car['pos'][1] - 40 < pos[1] - 40)):
                            #print(pos, car['pos'])
                            return True
                    if car['id'] < 100:
                        if car['pos'][1] <= 390:
                            touch_ceiling = True
                        if car['velocity'] > maxVel:
                            maxVel = car['velocity']
                if car_vel > maxVel:
                    maxVel = car_vel

                if pos[1] - 40 <= 350:
                    touch_ceiling = True

                pos[1] = int(pos[1] + camera - car_vel)

                #maxVel = car_vel # every user_car

                if maxVel >= 13:
                    if touch_ceiling:
                        camera = maxVel
                    else:
                        camera = maxVel - 2
                elif maxVel == 0:
                    camera = 1
                else:
                    if camera < maxVel:
                        camera += 0.7
                    elif camera > maxVel + 1:
                        camera -= 0.7
                    else:
                        pass
                touch_ceiling = False
            return False


        topLine = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[]}
        midLine = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[]}
        record = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[], 11:[]}
        
        if len(scene_info[self.player]) != 0:
            self.car_pos = scene_info[self.player]
        for car in scene_info["cars_info"]:
            if car["id"] == self.player_no:
                self.car_vel = car["velocity"]
        self.car_lane = self.car_pos[0] // 70

        if scene_info["status"] != "ALIVE":
            return "RESET"

        return check_grid()

        
    def reset(self):
        self.maxVel = 0
        self.camera_vel = 1
        self.touch_ceiling = False
        pass
