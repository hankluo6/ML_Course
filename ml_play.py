import math
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
        self.camera_vel = 0
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
        def check_grid():
            grid = set()
            speed_ahead = 100
            if self.car_pos[0] == 0:
                return
            if self.car_pos[0] <= 35:
                grid.add(1)
                grid.add(4)
                grid.add(7)
            if self.car_pos[0] >= 595: # right bound
                grid.add(3)
                grid.add(6)
                grid.add(9)
            for car in scene_info["cars_info"]:
                if car["id"] != self.player_no:
                    x = self.car_pos[0] - car["pos"][0] # x relative position
                    y = self.car_pos[1] - car["pos"][1] # y relative position
                    if self.lanes[self.car_lane] - 35 <= car['pos'][0] <= self.lanes[self.car_lane] + 35:
                        if self.car_pos[1] > 600:
                            if 0 <= y <= 500:
                                grid.add(2)
                                record[2].append(car)
                                if y < 200:
                                    if speed_ahead > car["velocity"]:
                                        speed_ahead = car["velocity"]
                                    grid.add(5)
                                    record[5].append(car)
                        else:
                            if 0 <= y <= 300:
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
                    if self.car_lane == 8 or self.lanes[self.car_lane + 1] - 35 <= car['pos'][0] <= self.lanes[self.car_lane + 1] + 35:
                        if self.car_pos[1] > 600:
                            if 80 < y < 500:
                                grid.add(3)
                                record[3].append(car)
                        else:
                            if 80 < y < 300:
                                grid.add(3)
                                record[3].append(car)
                        elif -80 <= y <= 80:
                            grid.add(6)
                            record[6].append(car)
                        elif -300 < y < -80:
                            grid.add(9)
                            record[9].append(car)
                    if self.car_lane == 0 or self.lanes[self.car_lane - 1] - 35 <= car['pos'][0] <= self.lanes[self.car_lane - 1] + 35:
                        if self.car_pos[1] > 600:
                            if 80 < y < 500:
                                grid.add(1)
                                record[1].append(car)
                        else:
                            if 80 < y < 300:
                                grid.add(1)
                                record[1].append(car)
                        elif -80 <= y <= 80:
                            grid.add(4)
                            record[4].append(car)
                        elif -300 < y < -80:
                            grid.add(7)
                            record[7].append(car)
                    if -80 <= y <= 80 and car['id'] < 101:
                        if 40 < x < 70:
                            grid.add(10)
                            record[10].append(car)
                        elif -40 > x > -70:
                            grid.add(11)
                            record[11].append(car)

                    if 80 < y < 400:
                        if car["id"] < 101:
                            topLine[car['pos'][0] // 70] = 1
                        else:
                            topLine[car['pos'][0]] = 1
                    elif -80 <= y <= 80:
                        if car["id"] < 101:
                            midLine[car['pos'][0] // 70] = 1
                        else:
                            midLine[car['pos'][0]] = 1
            return move(grid = grid, speed_ahead = speed_ahead)
            
        def move(grid, speed_ahead):
            if len(grid) == 0:
                if self.car_lane > 4:
                    self.target = 'LEFT'
                    return ['SPEED', 'MOVE_LEFT']
                elif self.car_lane < 4:
                    self.target = 'RIGHT'
                    return ['SPEED', 'MOVE_RIGHT']
                if self.car_pos[0] != self.lanes[self.car_lane]:
                    if self.target == 'LEFT':
                        return ["SPEED", "MOVE_LEFT"]
                    elif self.target == 'RIGHT':
                        return ["SPEED", "MOVE_RIGHT"]
                self.target = 'FRONT'
                return ["SPEED"]
            else:
                if self.target == 'LEFT' and self.car_pos[0] > self.lanes[self.car_lane] and (10 not in grid):
                    left = True
                else:
                    if (4 in grid):
                        left = False
                    else:
                        for car in record[7]:
                            if (car['velocity'] >= self.car_vel and car['id'] < 101) or (car['pos'][1] - self.car_pos[1] < 100):
                                left = False
                                break
                        else:
                            left = True
                        for car in record[1]:
                            if self.car_pos[1] - car['pos'][1] < 100 and car['velocity'] <= self.car_vel:
                                left = False
                                break
                        else:
                            left = True
    
                if self.target == 'RIGHT' and self.car_pos[0] < self.lanes[self.car_lane] and (11 not in grid):
                    right = True
                else:
                    if (6 in grid):
                        right = False
                    else:
                        for car in record[9]:
                            if (car['velocity'] > self.car_vel and car['id'] < 101) or (car['pos'][1] - self.car_pos[1] < 100):
                                right = False
                                break
                        else:
                            right = True
                        for car in record[3]:
                            if self.car_pos[1] - car['pos'][1] < 100 and car['velocity'] <= self.car_vel:
                                right = False
                                break
                        else:
                            right = True

                if (10 in grid) and (11 in grid): # car in left or right
                    if self.null != 0:
                        self.null -= 1
                        return [None]
                    elif self.brake != 0:
                        self.brake -= 1
                        return ['BRAKE']
                    elif self.speedUp:
                        return ['SPEED']
                    self.target = 'FRONT'
                    offset = record[11][0]['pos'][1] - self.car_pos[1]
                    if offset > record[10][0]['pos'][1] - self.car_pos[1]:
                        offset = record[10][0]['pos'][1] - self.car_pos[1]
                    if offset <= 0:
                        if self.car_vel >= 10:
                            self.null = 35
                        else:
                            self.null = 17
                    if offset > 0:
                        if record[10][0]['velocity'] >= self.car_vel:
                            if self.car_vel >= 10:
                                self.brake = 20
                            else:
                                self.brake = 15
                    self.speedUp = True
                    return [None]
                elif (10 in grid):
                    if right: # find top right speed
                        self.target = 'RIGHT'
                        return ['MOVE_RIGHT']
                    else:
                        if self.null != 0:
                            self.null -= 1
                            return [None]
                        elif self.brake != 0:
                            self.brake -= 1
                            return ['BRAKE']
                        elif self.speedUp: #maybe brake
                            return ['SPEED']
                        self.target = 'FRONT'
                        offset = record[10][0]['pos'][1] - self.car_pos[1]
                        if offset <= 0:
                            if self.car_vel >= 10:
                                self.null = 35
                            else:
                                self.null = 17
                        if offset > 0:
                            if record[10][0]['velocity'] >= self.car_vel:
                                if self.car_vel >= 10:
                                    self.brake = 20
                                else:
                                    self.brake = 15
                        self.speedUp = True
                        return [None]
                elif (11 in grid):
                    if left: # find top left speed
                        self.target = 'LEFT'
                        return ['MOVE_LEFT']
                    else:
                        if self.null != 0:
                            self.null -= 1
                            return [None]
                        elif self.brake != 0:
                            self.brake -= 1
                            return ['BRAKE']
                        elif self.speedUp:
                            return ['SPEED']
                        self.target = 'FRONT'
                        offset = record[11][0]['pos'][1] - self.car_pos[1]
                        if offset <= 0:
                            if self.car_vel >= 10:
                                self.null = 35
                            else:
                                self.null = 17
                        if offset > 0:
                            if record[11][0]['velocity'] >= self.car_vel:
                                if self.car_vel >= 10:
                                    self.brake = 20
                                else:
                                    self.brake = 15
                        self.speedUp = True
                        return [None]
                self.speedUp = False
                self.null = 0
                self.brake = 0
                if (2 not in grid): # Check forward 
                    if self.car_lane > 4 and (1 not in grid) and left:
                        self.target = 'LEFT'
                        return ['SPEED', 'MOVE_LEFT']
                    elif self.car_lane < 4 and (3 not in grid) and right:
                        self.target = 'RIGHT'
                        return ['SPEED', 'MOVE_RIGHT']
                    
                    # Back to lane center
                    if self.car_pos[0] != self.lanes[self.car_lane]:
                        if self.target == 'LEFT':
                            return ["SPEED", "MOVE_LEFT"]
                        elif self.target == 'RIGHT':
                            return ["SPEED", "MOVE_RIGHT"]
                    self.target = 'FRONT'
                    return ["SPEED"]
                else:
                    if (5 in grid):
                        if self.target == 'LEFT' and self.car_pos[0] > self.lanes[self.car_lane]: # moving to center
                            if (3 not in grid) and right:
                                self.target = 'RIGHT'
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_RIGHT"]
                                else:
                                    return ["BRAKE", "MOVE_RIGHT"]
                            else:
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_LEFT"]
                                else:
                                    return ["BRAKE", "MOVE_LEFT"]
                        if self.target == 'LEFT' and self.car_pos[0] < self.lanes[self.car_lane]: # moving away from center
                            maxSpeed = 100
                            for car in record[1]:
                                if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                    maxSpeed = car['velocity']
                            if self.car_vel < speed_ahead and self.car_vel < maxSpeed:
                                return ["SPEED", "MOVE_LEFT"]
                            else:
                                return ["BRAKE", "MOVE_LEFT"]
                        if self.target == 'RIGHT' and self.car_pos[0] < self.lanes[self.car_lane]: # moving to center
                            if (1 not in grid) and left:
                                self.target = 'LEFT'
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_LEFT"]
                                else:
                                    return ["BRAKE", "MOVE_LEFT"]
                            else:
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_RIGHT"]
                                else:
                                    return ["BRAKE", "MOVE_RIGHT"]
                        if self.target == 'RIGHT' and self.car_pos[0] > self.lanes[self.car_lane]: # moving away from center
                            maxSpeed = 100
                            for car in record[1]:
                                if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                    maxSpeed = car['velocity']
                            if self.car_vel < speed_ahead and self.car_vel < maxSpeed:
                                return ["SPEED", "MOVE_RIGHT"]
                            else:
                                return ["BRAKE", "MOVE_RIGHT"]

                        if left and right:
                            if (1 not in grid) and (3 not in grid):
                                if self.car_lane >= 4:
                                    self.target = 'LEFT'
                                    if self.car_vel < speed_ahead:
                                        return ["SPEED", "MOVE_LEFT"]
                                    else:
                                        return ["BRAKE", "MOVE_LEFT"]
                                else:
                                    self.target = 'RIGHT'
                                    if self.car_vel < speed_ahead:
                                        return ["SPEED", "MOVE_RIGHT"]
                                    else:
                                        return ["BRAKE", "MOVE_RIGHT"]
                            elif (1 not in grid):
                                self.target = 'LEFT'
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_LEFT"]
                                else:
                                    return ["BRAKE", "MOVE_LEFT"]
                            elif (3 not in grid):
                                self.target = 'RIGHT'
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_RIGHT"]
                                else:
                                    return ["BRAKE", "MOVE_RIGHT"]
                            else:
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
                                    if l and self.car_pos[1] - max_dis[0] >= 100:
                                        self.target = 'LEFT'
                                        maxSpeed = 100
                                        for car in record[1]:
                                            if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                                maxSpeed = car['velocity']
                                        if self.car_vel < speed_ahead and self.car_vel < maxSpeed:
                                            return ["SPEED", "MOVE_LEFT"]
                                        else:
                                            return ["BRAKE", "MOVE_LEFT"]
                                    elif r and self.car_pos[1] - max_dis[2] >= 100:
                                        self.target = 'RIGHT'
                                        maxSpeed = 100
                                        for car in record[3]:
                                            if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                                maxSpeed = car['velocity']
                                        if self.car_vel < speed_ahead and self.car_vel < maxSpeed:
                                            return ["SPEED", "MOVE_RIGHT"]
                                        else:
                                            return ["BRAKE", "MOVE_RIGHT"]

                                if max_speed[0] >= max_speed[1] and max_speed[0] >= max_speed[2] and self.car_pos[1] - max_dis[0] >= 100:
                                    self.target = 'LEFT'
                                    maxSpeed = 100
                                    for car in record[1]:
                                        if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                            maxSpeed = car['velocity']
                                    if self.car_vel < speed_ahead and self.car_vel < maxSpeed:
                                        return ["SPEED", "MOVE_LEFT"]
                                    else:
                                        return ["BRAKE", "MOVE_LEFT"]
                                if max_speed[1] >= max_speed[0] and max_speed[1] >= max_speed[2] and self.car_pos[1] - max_dis[1] >= 100:
                                    self.target = 'FRONT'
                                    if self.car_vel < speed_ahead:
                                        return ["SPEED"]
                                    else:
                                        return ["BRAKE"]
                                if max_speed[2] >= max_speed[1] and max_speed[2] >= max_speed[0] and self.car_pos[1] - max_dis[2] >= 100:
                                    self.target = 'RIGHT'
                                    maxSpeed = 100
                                    for car in record[3]:
                                        if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                            maxSpeed = car['velocity']
                                    if self.car_vel < speed_ahead and self.car_vel < maxSpeed:
                                        return ["SPEED", "MOVE_RIGHT"]
                                    else:
                                        return ["BRAKE", "MOVE_RIGHT"]

                                
                                if max_dis[0] <= max_dis[1] and max_dis[0] <= max_dis[2]:
                                    self.target = 'LEFT'
                                    maxSpeed = 100
                                    for car in record[1]:
                                        if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                            maxSpeed = car['velocity']
                                    if self.car_vel < speed_ahead and self.car_vel < maxSpeed:
                                        return ["SPEED", "MOVE_LEFT"]
                                    else:
                                        return ["BRAKE", "MOVE_LEFT"]
                                if max_dis[1] <= max_dis[0] and max_dis[1] <= max_dis[2]:
                                    self.target = 'FRONT'
                                    if self.car_vel < speed_ahead:
                                        return ["SPEED"]
                                    else:
                                        return ["BRAKE"]
                                else:
                                    self.target = 'RIGHT'
                                    maxSpeed = 100
                                    for car in record[3]:
                                        if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                            maxSpeed = car['velocity']
                                    if self.car_vel < speed_ahead and self.car_vel < maxSpeed:
                                        return ["SPEED", "MOVE_RIGHT"]
                                    else:
                                        return ["BRAKE", "MOVE_RIGHT"]
                        if left:
                            if (1 not in grid):
                                self.target = 'LEFT'
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_LEFT"]
                                else:
                                    return ["BRAKE", "MOVE_LEFT"]
                            elif self.car_lane == 8:
                                maxSpeed = 100
                                for car in record[1]:
                                    if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                        maxSpeed = car['velocity']
                                if self.car_vel < speed_ahead and self.car_vel < maxSpeed:
                                    return ["SPEED", "MOVE_LEFT"]
                                else:
                                    return ["BRAKE", "MOVE_LEFT"]
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
                                        self.target = 'LEFT'
                                        maxSpeed = 100
                                        for car in record[1]:
                                            if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                                maxSpeed = car['velocity']
                                        if self.car_vel < speed_ahead and self.car_vel < maxSpeed:
                                            return ["SPEED", "MOVE_LEFT"]
                                        else:
                                            return ["BRAKE", "MOVE_LEFT"]

                                if max_speed[0] >= max_speed[1] and self.car_pos[1] - max_dis[0] >= 100:
                                    self.target = 'LEFT'
                                    maxSpeed = 100
                                    for car in record[1]:
                                        if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                            maxSpeed = car['velocity']
                                    if self.car_vel < speed_ahead and self.car_vel < maxSpeed:
                                        return ["SPEED", "MOVE_LEFT"]
                                    else:
                                        return ["BRAKE", "MOVE_LEFT"]
                                elif max_speed[1] >= max_speed[0] and self.car_pos[1] - max_dis[1] >= 100:
                                    self.target = 'FRONT'
                                    if self.car_vel < speed_ahead:
                                        return ["SPEED"]
                                    else:
                                        return ["BRAKE"]

                                if max_dis[0] <= max_dis[1]:
                                    self.target = 'LEFT'
                                    maxSpeed = 100
                                    for car in record[1]:
                                        if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                            maxSpeed = car['velocity']
                                    if self.car_vel < speed_ahead and self.car_vel < maxSpeed:
                                        return ["SPEED", "MOVE_LEFT"]
                                    else:
                                        return ["BRAKE", "MOVE_LEFT"]
                                else:
                                    self.target = 'FRONT'
                                    if self.car_vel < speed_ahead:
                                        return ["SPEED"]
                                    else:
                                        return ["BRAKE"]
                        if right:
                            if (3 not in grid):
                                self.target = 'RIGHT'
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_RIGHT"]
                                else:
                                    return ["BRAKE", "MOVE_RIGHT"]
                            elif self.car_lane == 0:
                                maxSpeed = 100
                                for car in record[3]:
                                    if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                        maxSpeed = car['velocity']
                                if self.car_vel < speed_ahead and self.car_vel < maxSpeed:
                                    return ["SPEED", "MOVE_RIGHT"]
                                else:
                                    return ["BRAKE", "MOVE_RIGHT"]
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
                                        self.target = 'RIGHT'
                                        maxSpeed = 100
                                        for car in record[3]:
                                            if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                                maxSpeed = car['velocity']
                                        if self.car_vel < speed_ahead and self.car_vel < maxSpeed:
                                            return ["SPEED", "MOVE_RIGHT"]
                                        else:
                                            return ["BRAKE", "MOVE_RIGHT"]

                                if max_speed[0] <= max_speed[1] and self.car_pos[1] - max_dis[1] >= 100:
                                    self.target = 'RIGHT'
                                    maxSpeed = 100
                                    for car in record[3]:
                                        if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                            maxSpeed = car['velocity']
                                    if self.car_vel < speed_ahead and self.car_vel < maxSpeed:
                                        return ["SPEED", "MOVE_RIGHT"]
                                    else:
                                        return ["BRAKE", "MOVE_RIGHT"]
                                elif max_speed[1] < max_speed[0] and self.car_pos[1] - max_dis[0] >= 100:
                                    self.target = 'FRONT'
                                    if self.car_vel < speed_ahead:
                                        return ["SPEED"]
                                    else:
                                        return ["BRAKE"]

                                if max_dis[1] <= max_dis[0]:
                                    self.target = 'RIGHT'
                                    maxSpeed = 100
                                    for car in record[3]:
                                        if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                            maxSpeed = car['velocity']
                                    if self.car_vel < speed_ahead and self.car_vel < maxSpeed:
                                        return ["SPEED", "MOVE_RIGHT"]
                                    else:
                                        return ["BRAKE", "MOVE_RIGHT"]
                                else:
                                    self.target = 'FRONT'
                                    if self.car_vel < speed_ahead:
                                        return ["SPEED"]
                                    else:
                                        return ["BRAKE"]
                        else:
                            self.target = 'FRONT'
                            if self.car_vel < speed_ahead:
                                return ["SPEED"]
                            else:
                                return ["BRAKE"]

                    if self.target == 'LEFT' and self.car_pos[0] > self.lanes[self.car_lane]: # moving to center
                        if (3 not in grid) and right:
                            self.target = 'RIGHT'
                            return ["SPEED", "MOVE_RIGHT"]
                        else:
                            return ["SPEED", "MOVE_LEFT"]
                    if self.target == 'LEFT' and self.car_pos[0] < self.lanes[self.car_lane]: # moving away from center
                        maxSpeed = 100
                        for car in record[1]:
                            if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                maxSpeed = car['velocity']
                        if self.car_vel < maxSpeed:
                            return ["SPEED", "MOVE_LEFT"]
                        else:
                            return ["BRAKE", "MOVE_LEFT"]
                    if self.target == 'RIGHT' and self.car_pos[0] < self.lanes[self.car_lane]: # moving to center
                        if (1 not in grid) and left:
                            self.target = 'LEFT'
                            return ["SPEED", "MOVE_LEFT"]
                        else:
                            return ["SPEED", "MOVE_RIGHT"]
                    if self.target == 'RIGHT' and self.car_pos[0] > self.lanes[self.car_lane]: # moving away from center
                        maxSpeed = 100
                        for car in record[3]:
                            if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                maxSpeed = car['velocity']
                        if self.car_vel < maxSpeed:
                            return ["SPEED", "MOVE_RIGHT"]
                        else:
                            return ["BRAKE", "MOVE_RIGHT"]

                    if left and right:
                        if (1 not in grid) and (3 not in grid):
                            if self.car_lane >= 4:
                                self.target = 'LEFT'
                                return ["SPEED", "MOVE_LEFT"]
                            else:
                                self.target = 'RIGHT'
                                return ["SPEED", "MOVE_RIGHT"]
                        if (1 not in grid):
                            self.target = 'LEFT'
                            return ["SPEED", "MOVE_LEFT"]
                        elif (3 not in grid):
                            self.target = 'RIGHT'
                            return ["SPEED", "MOVE_RIGHT"]
                        else:

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
                                if l and self.car_pos[1] - max_dis[0] >= 100:
                                    self.target = 'LEFT'
                                    maxSpeed = 100
                                    for car in record[1]:
                                        if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                            maxSpeed = car['velocity']
                                    if self.car_vel < maxSpeed:
                                        return ["SPEED", "MOVE_LEFT"]
                                    else:
                                        return ["BRAKE", "MOVE_LEFT"]
                                elif r and self.car_pos[1] - max_dis[2] >= 100:
                                    self.target = 'RIGHT'
                                    maxSpeed = 100
                                    for car in record[3]:
                                        if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                            maxSpeed = car['velocity']
                                    if self.car_vel < maxSpeed:
                                        return ["SPEED", "MOVE_RIGHT"]
                                    else:
                                        return ["BRAKE", "MOVE_RIGHT"]

                            if max_speed[0] >= max_speed[1] and max_speed[0] >= max_speed[2] and self.car_pos[1] - max_dis[0] >= 100:
                                self.target = 'LEFT'
                                maxSpeed = 100
                                for car in record[1]:
                                    if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                        maxSpeed = car['velocity']
                                if self.car_vel < maxSpeed:
                                    return ["SPEED", "MOVE_LEFT"]
                                else:
                                    return ["BRAKE", "MOVE_LEFT"]
                            if max_speed[1] >= max_speed[0] and max_speed[1] >= max_speed[2] and self.car_pos[1] - max_dis[1] >= 100:
                                self.target = 'FRONT'
                                return ["SPEED"]
                            if max_speed[2] >= max_speed[1] and max_speed[2] >= max_speed[0] and self.car_pos[1] - max_dis[2] >= 100:
                                self.target = 'RIGHT'
                                maxSpeed = 100
                                for car in record[3]:
                                    if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                        maxSpeed = car['velocity']
                                if self.car_vel < maxSpeed:
                                    return ["SPEED", "MOVE_RIGHT"]
                                else:
                                    return ["BRAKE", "MOVE_RIGHT"]

                            if max_dis[0] <= max_dis[1] and max_dis[0] <= max_dis[2]:
                                self.target = 'LEFT'
                                maxSpeed = 100
                                for car in record[1]:
                                    if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                        maxSpeed = car['velocity']
                                if self.car_vel < maxSpeed:
                                    return ["SPEED", "MOVE_LEFT"]
                                else:
                                    return ["BRAKE", "MOVE_LEFT"]
                            elif max_dis[1] <= max_dis[0] and max_dis[1] <= max_dis[2]:
                                self.target = 'FRONT'
                                if self.car_vel < speed_ahead:
                                    return ["SPEED"]
                                else:
                                    return ["BRAKE"]
                            else:
                                self.target = 'RIGHT'
                                maxSpeed = 100
                                for car in record[3]:
                                    if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                        maxSpeed = car['velocity']
                                if self.car_vel < maxSpeed:
                                    return ["SPEED", "MOVE_RIGHT"]
                                else:
                                    return ["BRAKE", "MOVE_RIGHT"]
                    if left:
                        if self.car_lane == 1: # prevent to the leftmost
                            return ["SPEED"]
                        elif (1 not in grid):
                            self.target = 'LEFT'
                            return ["SPEED", "MOVE_LEFT"]
                        else:
                            if (3 not in grid):
                                return ["SPEED"]
                            max_dis = [0, 0]
                            max_dis[0] = max([car['pos'][1] for car in record[1]])
                            max_dis[1] = max([car['pos'][1] for car in record[2]])
                            
                            max_speed = [0, 0]
                            max_speed[0] = max([car['velocity'] for car in record[1]])
                            max_speed[1] = max([car['velocity'] for car in record[2]])

                            if max(max_speed) - min(max_speed) < 2:
                                l, _ = find_target(True, False)
                                if l and self.car_pos[1] - max_dis[0] >= 100:
                                    self.target = 'LEFT'
                                    maxSpeed = 100
                                    for car in record[1]:
                                        if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                            maxSpeed = car['velocity']
                                    if self.car_vel < maxSpeed:
                                        return ["SPEED", "MOVE_LEFT"]
                                    else:
                                        return ["BRAKE", "MOVE_LEFT"] 

                            if max_speed[0] >= max_speed[1] and self.car_pos[1] - max_dis[0] >= 100:
                                self.target = 'LEFT'
                                maxSpeed = 100
                                for car in record[1]:
                                    if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                        maxSpeed = car['velocity']
                                if self.car_vel < maxSpeed:
                                    return ["SPEED", "MOVE_LEFT"]
                                else:
                                    return ["BRAKE", "MOVE_LEFT"]
                            elif max_speed[1] >= max_speed[0] and self.car_pos[1] - max_dis[1] >= 100:
                                self.target = 'FRONT'
                                return ["SPEED"]

                            if max_dis[0] <= max_dis[1]:
                                self.target = 'LEFT'
                                maxSpeed = 100
                                for car in record[1]:
                                    if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                        maxSpeed = car['velocity']
                                if self.car_vel < maxSpeed:
                                    return ["SPEED", "MOVE_LEFT"]
                                else:
                                    return ["BRAKE", "MOVE_LEFT"]
                            else:
                                self.target = 'FRONT'
                                return ["SPEED"]
                    if right:
                        if self.car_lane == 7: # prevent to the rightmost
                            return ["SPEED"]
                        elif (3 not in grid):
                            self.target = 'RIGHT'
                            return ["SPEED", "MOVE_RIGHT"]
                        else:
                            if (1 not in grid):
                                return ["SPEED"]
                            max_dis = [0, 0]
                            max_dis[0] = max([car['pos'][1] for car in record[2]])
                            max_dis[1] = max([car['pos'][1] for car in record[3]])

                            max_speed = [0, 0]
                            max_speed[0] = max([car['velocity'] for car in record[2]])
                            max_speed[1] = max([car['velocity'] for car in record[3]])

                            if max(max_speed) - min(max_speed) < 2:
                                _, r = find_target(False, True)
                                if r and self.car_pos[1] - max_dis[1] >= 100:
                                    self.target = 'RIGHT'
                                    maxSpeed = 100
                                    for car in record[3]:
                                        if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                            maxSpeed = car['velocity']
                                    if self.car_vel < maxSpeed:
                                        return ["SPEED", "MOVE_RIGHT"]
                                    else:
                                        return ["BRAKE", "MOVE_RIGHT"]

                            if max_speed[0] <= max_speed[1] and self.car_pos[1] - max_dis[1] >= 100:
                                self.target = 'RIGHT'
                                maxSpeed = 100
                                for car in record[3]:
                                    if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                        maxSpeed = car['velocity']
                                if self.car_vel < maxSpeed:
                                    return ["SPEED", "MOVE_RIGHT"]
                                else:
                                    return ["BRAKE", "MOVE_RIGHT"]
                            elif max_speed[1] < max_speed[0] and self.car_pos[1] - max_dis[0] >= 100:
                                self.target = 'FRONT'
                                return ["SPEED"]
                            
                            if max_dis[1] <= max_dis[0]:
                                self.target = 'RIGHT'
                                maxSpeed = 100
                                for car in record[3]:
                                    if self.car_pos[1] - car["pos"][1] < 200 and maxSpeed > car['velocity']:
                                        maxSpeed = car['velocity']
                                if self.car_vel < maxSpeed:
                                    return ["SPEED", "MOVE_RIGHT"]
                                else:
                                    return ["BRAKE", "MOVE_RIGHT"]
                            else:
                                self.target = 'FRONT'
                                return ["SPEED"]
                    else:
                        self.target = 'FRONT'
                        return ["SPEED"]

                    

        
        def find_target(left, right):
            target = self.car_pos[0]
            tmp = target // 70
            l = r = hasLeft = hasRight = False
            if right:
                imRight = False
                for i in range(tmp + 1, 9): 
                    if midLine[i * 70 + 35] == 1:
                        imRight = True
                    if midLine[i * 70 + 35] == 0 and topLine[i * 70 + 35] == 0 and not imRight:
                        r = True
                        break
                if tmp + 2 < 9 and midLine[(tmp + 2) * 70 + 35] == 0:
                    hasRight = True
            else:
                r = False
            if left:
                imLeft = False
                for i in range(tmp - 1, -1, -1):
                    if midLine[i * 70 + 35] == 1:
                        imLeft = True
                    if midLine[i * 70 + 35] == 0 and topLine[i * 70 + 35] == 0 and not imLeft:
                        l = True
                        break
                if tmp - 2 >= 0 and midLine[(tmp - 2) * 70 + 35] == 0:
                    hasLeft = True
            else:
                l = False

            if not l and not r:
                return [hasLeft, hasRight]

            return [l, r]


        topLine = {35:0, 105:0, 175:0, 245:0, 315:0, 385:0, 455:0, 525:0, 595:0}
        midLine = {35:0, 105:0, 175:0, 245:0, 315:0, 385:0, 455:0, 525:0, 595:0}

        record = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[], 11:[]}
        
        if len(scene_info[self.player]) != 0:
            self.car_pos = scene_info[self.player]
        for car in scene_info["cars_info"]:
            if car["id"] == self.player_no:
                self.car_vel = car["velocity"]
        if scene_info["status"] != "ALIVE":
            return "RESET"
        self.car_lane = self.car_pos[0] // 70
        
        return check_grid()

        


    def reset(self):
        
        pass
