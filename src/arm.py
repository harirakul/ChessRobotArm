#Code for Chess Robot Inverse Kinematics

import math
import serial
from time import sleep

SQUARE_SIZE = 3.5
offset = 6

filemap = {
    "h": 3.5+0.2, "g": 2.5+0.1, "f": 1.5, "e": 0.5-0.2, "d": -0.5-0.3, "c": -1.5, "b": -2.5, "a": -3.5
}

class ChessRobotArm:
    def __init__(self, a: int, b: int, port='COM4', verbose=False) -> None:
        self.port = port
        self.ser = serial.Serial(port)
        print(f"Connected to Robot on port {port}")

        self.a = a #Length of arm a (cm)
        self.b = b #Length of arm b (cm)

        self.verbose = verbose

    def wait_until_msg(self, msg: str) -> None:
        while True:
            rec = self.ser.readline().decode().strip()
            if (msg in rec):
                break
            else:
                print("Received message:", rec)
                # if float(rec) <= 180:
                #     self.shoulder = float(rec)
                # elif 200 <= float(rec) and float(rec) <= 380:
                #     self.elbow = float(rec)
        if self.verbose:
            print("Received message:", rec)

    def command(self, num: int, wait=True) -> None:
        self.ser.write(bytes(str(num), 'utf-8'))
        if self.verbose:
            print(f"Sent command: {num}")
        sleep(0.05)
        if wait:
            self.wait_until_msg("done")

    def shoulder_to(self, angle: int) -> None:
        self.command(angle)
    
    def elbow_to(self, angle: int) -> None:
        self.command(angle + 200, wait=False)
    
    def combo_move(self, sangle, eangle):
        self.command(eangle + 200)
        self.command(sangle)
    
    def base_to(self, angle: int) -> None:
        self.command(angle + 400)
    
    def rest(self) -> None:
        self.command(190)
    
    def grasp(self) -> None:
        self.command(191)
    
    def drop(self) -> None:
        self.command(192)
    
    def grasp_knight(self) -> None:
        print("Grabbing knight")
        self.command(193)
    
    def base_angle(self, x: float, y: float):
        y += offset/SQUARE_SIZE + 0.3
        
        d = math.sqrt((x*SQUARE_SIZE)**2 + (y*SQUARE_SIZE)**2)

        #x -=0.54 #For angle purposes only.

        angle = math.atan(y/x)*180/math.pi

        if angle < 0:
            angle+= 180
        if x < 0: # adjusting angle when square is to the left of base.
            angle -= x*3
        return(d, angle)
    
    def inverse_kinematics(self, x: float, y: float):
        elbow_theta = math.acos((x**2 + y**2 - self.a**2 - self.b**2)/(2*self.a*self.b))
        shoulder_theta = math.atan(y/x) - math.atan((self.b*math.sin(elbow_theta))/(self.a + self.b*math.cos(elbow_theta)))

        return (-shoulder_theta*180/math.pi, 180 - elbow_theta*180/math.pi)
    
    def go_to(self, square: str):
        x = filemap[square[0]]
        y = int(square[1]) + 0.5
        b = self.base_angle(x, y)
        d = b[0]
        rank = int(square[1])
        vertical_offset = -8 + rank/2.6
        b_offset = 1
        s, e = self.inverse_kinematics(vertical_offset, d+rank/10)
        e-=3
        #s+=2
        if self.verbose:
            print('Base', b)
            print('Shoulder', s-90)
            print('Elbow', e)

        #Square-specific Tuning
        if rank==2:
            e-=1
        if square in ('h2', 'g2', 'c4', 'g3', 'e5', 'c1', 'f4', 'h1', 'g1', 'd2', 'c2', 'e2', 'f3', 'e4'):
            s += 0
            e += 2
            if square in ('h2', 'g2'):
                e += 2
            if square in ('g3', 'c4'):
                b_offset += 1
        if square in ('a1', 'b1', 'f3', 'b3'):
            b_offset+=3
            if square in ('b1'):
                e-=4
        if square in ('d1', 'c1'):
            e -= 8
        if square in ('e1'):
            e -=3
        if square in ('f1', 'c2', 'e3', 'e4'):
            b_offset += 2
            if square in ('f1', 'e3'):
                e -=1
                b_offset += 1
                if square in ('f1'):
                    e-=3
        if square in ['a1', 'a3', 'b3', 'c4', 'c5', 'b5', 'a5', 'c6', 'b6', 'a6', 'a7']:
            e -=2
        if square in ('d5', 'c5', 'b5'):
            s-=1
            e -=0
        if square in ('e2', 'd4', 'c4', 'b4', 'a4', 'd3', 'd2', 'c2'):
            s-=2
            if square in ('b4'):
                s-=1
        if square in ('d4', 'e4', 'a2', 'a4'):
            b_offset -=2
        if square in ('b4', 'd4', 'e4', 'c4', 'c2', 'a4', 'd3', 'g1', 'b1') or (rank in (5, 6, 7) and square not in ('a5', 'a6')):
            b_offset += 3   
            if square in ('c4'):
                e += 1
        if square in ('c1'):
            b_offset += 6
        if square in ('h7', 'g7', 'f7', 'e7'):
            e += 2
            b_offset+=2
        if square in ('b7', 'a7'):
            b_offset -=2
        if square in ('d1'):
            b_offset -=3
        if square in ('d5'):
            b_offset -=2
        if rank==8:
            e+=4
            b_offset+=6
            s += 2
            if square in ('c8', 'b8', 'e8', 'd8', 'a8'):
                e-=3
            if square in ('a8'):
                b_offset -=4
        if square in ('f5'):
            e += 1

        self.base_to(b[1] + b_offset)
        # self.elbow_to(e)
        # self.shoulder_to(s-90)
        self.combo_move(s-90, e)
    
    def move(self, sq1: str, sq2: str, knight=False):
        self.drop()
        self.go_to(sq1)
        if knight:
            self.grasp_knight()
        else:
            self.grasp()
        self.rest()
        self.go_to(sq2)
        self.drop()
        self.rest()
    
    def discard(self, sq: str):
        self.drop()
        self.go_to(sq)
        self.grasp()
        self.rest()
        self.base_to(140)
        self.combo_move(50, 94)
        # self.elbow_to(94)
        # self.shoulder_to(50)
        self.drop()
        self.rest()

if __name__ == '__main__':  
    robot = ChessRobotArm(22, 22.5, port='COM4', verbose=True)

    while True:
        sq = input()
        robot.drop()
        robot.go_to(sq)
        robot.grasp()
        robot.rest()
        robot.drop()
        #robot.move(sq[:2], sq[2:4])
        #robot.rest()
        #robot.discard(sq)