#Play a full game using Computer Vision

import cv2
import numpy as np
import json
import chess
import chess.svg
from cairosvg import svg2png
import chess.engine
from arm import ChessRobotArm
import random

engine = chess.engine.SimpleEngine.popen_uci(r"stockfish\stockfish-windows-2022-x86-64-avx2.exe")

with open('sqdict.json', 'r') as fp:
    sq_points = json.load(fp)

#Returns the square given a point within the square
def find_square(x: float, y: float): 
    for square in sq_points:
        points = np.array(sq_points[square], np.int32)
        if cv2.pointPolygonTest(points, (x, y), False) > 0:
            return square
    return None

#Outline the squares
def draw_outlines(sq_points: dict, frame, show_text = False) -> None:
    for square in sq_points:
        points = sq_points[square]
        points = np.array(points, dtype=np.int32)
        cv2.polylines(frame, [points], True, (255, 255, 255), thickness=1)
        x, y, w, h = cv2.boundingRect(points)
        if show_text:
            cv2.putText(frame, square, (x, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

#Show board using python-chess SVGRendering
def show_board(board: chess.Board, size=900, move = None) -> None:
        if move is not None:
            sq1, sq2 = chess.parse_square(move[:2]), chess.parse_square(move[2:4])
            svgwrap = chess.svg.board(board, size=size, fill=dict.fromkeys([sq1, sq2], '#ced264'))
        else:
            svgwrap = chess.svg.board(board, size=size)
        svg2png(svgwrap, write_to='output.png')
        cv2.imshow('Game', cv2.imread('output.png')) 

cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

initial = []
final = []
bounding_boxes = []
centers = []
highlights = set()

board = chess.Board()
robot = ChessRobotArm(22, 22.5, port = 'COM4') #Initialize a 3DOF Robotic Arm with L1=22, L2=21, at port COM4
comp_move = True
show_board(board)
cv2.waitKey(2)

while not board.is_game_over():
    ret, frame = cap.read()
    draw_outlines(sq_points, frame)
    cv2.imshow('Frame', frame)

    if comp_move:
        result = engine.play(board, chess.engine.Limit(time=random.random()))
        comp_move = result.move.uci()
        (sq1, sq2) = (comp_move[:2], comp_move[2:4])

        #Check for castling
        if board.is_capture(result.move):
            robot.discard(sq2)

        #For straight pawn moves:
        robot.move(sq1, sq2, knight=(board.piece_type_at(chess.parse_square(sq1)) == chess.KNIGHT))

        if comp_move == 'e1g1' and board.piece_type_at(chess.E1) == chess.KING: #Kingside
            robot.move('h1', 'f1')
        elif comp_move == 'e1c1' and board.piece_type_at(chess.E1) == chess.KING: #Queenside
            robot.move('a1', 'd1')
        
        board.push(result.move)
        print('Robot plays', result.move.uci())
        show_board(board, move=str(result.move))
        comp_move = False

    for (x, y, w, h) in bounding_boxes:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    for (x, y) in centers:
        square = find_square(x, y)
        highlights.add(square)

    if cv2.waitKey(1) & 0xFF == ord('r'):
        if len(initial)==0:
            initial = frame
            print("Recording")
        elif len(final)==0:
            print('Move captured')
            final = frame

            #Get the absolute difference between the initial and final frames.
            gray1 = cv2.cvtColor(initial, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(final, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(gray1, gray2)
            _, diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

            #Remove noise from the difference frame
            diff = cv2.dilate(diff, None, iterations=4)
            kernel_size = 3
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
            diff = cv2.erode(diff, kernel, iterations=6)
            
            #Find relevant contours
            contours, _ = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            sorted_contours_and_areas = sorted(zip(contours, [cv2.contourArea(c) for c in contours]), key=lambda x: x[1], reverse=True)
            try:
                contours = [sorted_contours_and_areas[0][0], sorted_contours_and_areas[1][0]]
                cv2.drawContours(frame, contours, 1, (255, 0, 0), 4)

                #Find the bounding boxes of the contours
                bounding_boxes = [cv2.boundingRect(c) for c in contours]

                # Find the center point of the bounding boxes 
                centers = [(x + w//2, y + 0.7*h) for (x, y, w, h) in bounding_boxes]
                highlights = set()
                for p in centers:
                    highlights.add(find_square(*p))
                initial = []
                final = []
            except:
                highlights = set()
                highlights.add('rand')
                highlights.add('placeholder')
                initial = []
                final = []
            #cv2.imshow('Absolute Difference', diff)
            if len(highlights) == 2:
                try:
                    sq1, sq2 = highlights.pop(), highlights.pop()
                    if board.color_at(chess.parse_square(sq1)) == board.turn:
                        start, end = sq1, sq2
                    else:
                        start, end = sq2, sq1
                    uci = start+end
                    board.push_uci(uci)
                except:
                    uci = input("Couldn't record proper move. Override: ")
                    board.push_uci(uci)
                show_board(board, move=uci)
                highlights = set()
                centers = []
                comp_move = True
    #Black castles 0-0
    if cv2.waitKey(3) & 0xFF == ord('m'):
        move = 'e8g8'
        board.push_uci('e8g8')
        show_board(board, move=move)
        bounding_boxes = []
        comp_move = True

    #Black castles 0-0-0 
    if cv2.waitKey(4) & 0xFF == ord('n'):
        move = 'e8c8'
        board.push_uci('e8c8')
        show_board(board, move=move)
        bounding_boxes = []
        comp_move = True

    #Exit command
    if cv2.waitKey(2) & 0xFF == ord('q'):
        break

    cv2.imshow('Frame', frame)


show_board(board)

# Release the video capture object
cap.release()

# Close all windows
#cv2.destroyAllWindows()