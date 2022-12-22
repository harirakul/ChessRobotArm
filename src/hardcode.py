import serial
import json
from time import sleep

# Create JSON file with square names dict
# d = {}
# for L in 'abcdefgh':
#     for i in range(1, 9):
#         d[L + str(i)] = {'b': 0, 's': 0, 'e': 0}

# with open('angles.json', 'w') as fp:
#     json.dump(d, fp)

class Controller:
    def __init__(self, port='COM4', datafile='angles.json') -> None:
        self.port = port
        self.ser = serial.Serial(port)
        print(f"Connected to Robot on port {port}")

        self.shoulder = 0
        self.elbow = 0
        self.base = 0
        self.datafile = datafile

    def wait_until_msg(self, msg: str) -> None:
        while True:
            rec = self.ser.readline().decode().strip()
            if (msg in rec):
                break
            else:
                print("Received message:", rec)
                if int(rec) <= 180:
                    self.shoulder = int(rec)
                elif 200 <= int(rec) and int(rec) <= 380:
                    self.elbow = int(rec) - 200
                    sq = input('Square: ')
                    self.write_to_file(sq, self.base, self.shoulder, self.elbow, self.datafile)
                elif 400 <= int(rec) and int(rec) <= 480:
                    self.base = int(rec) - 400
        print("Received message:", rec)

    def command(self, num: int) -> None:
        self.ser.write(bytes(str(num), 'utf-8'))
        print(f"Sent command: {num}")
        sleep(0.05)
        self.wait_until_msg("done")
    
    def write_to_file(self, sq: str, b: int, s: int, e: int, f: str):
        with open(f, 'r') as fp:
            d = json.load(fp)
            d[sq]['b'] = b
            d[sq]['s'] = s
            d[sq]['e'] = e
        with open(f, 'w') as fp:
            json.dump(d, fp)


c = Controller(port='COM4')
c.wait_until_msg('done')

# while True:
#     square = input()
#     x = filemap[square[0]]
#     y = int(square[1]) + 0.5
#     b = robot.base_angle(x, y)
#     robot.base_to(b[1])
#     print(robot.shoulder)
#     print(robot.elbow)
#     robot.rest()