#Play a chess game without using Computer Vision

import chess
import chess.engine
from arm import ChessRobotArm
import random

engine = chess.engine.SimpleEngine.popen_uci(r"stockfish\stockfish-windows-2022-x86-64-avx2.exe")

board = chess.Board()
robot = ChessRobotArm(22, 22.5, port = 'COM4') #Initialize a 3DOF Robotic Arm with L1=22, L2=21, at port COM4

while not board.is_game_over():
    result = engine.play(board, chess.engine.Limit(time=random.random()))
    comp_move = result.move.uci()
    (sq1, sq2) = (comp_move[:2], comp_move[2:4])

    #Check for castling
    if board.is_capture(result.move):
        robot.discard(sq2)

    robot.move(sq1, sq2)

    #Check for castling:
    if comp_move == 'e1g1' and board.piece_type_at(chess.E1) == chess.KING: #Kingside
        robot.move('h1', 'f1')
    elif comp_move == 'e1c1' and board.piece_type_at(chess.E1) == chess.KING: #Queenside
        robot.move('a1', 'c1')
    
    board.push(result.move)
    print('Robot plays', result.move.uci())
    print(board)

    user_move = input("Make your move:")
    board.push_uci(user_move)
    print(board)

engine.quit()