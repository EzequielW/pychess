from engine.chess_logic import Chess, Piece
import copy
import numpy as np

class Minimax():
    infinite = 20000
    node_number = 0
    pawn_value = np.array([
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ])
    knight_value = np.array([
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    ])
    bishop_value = np.array([
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20
    ])
    rook_value = np.array([
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        0,  0,  0,  5,  5,  0,  0,  0
    ])
    queen_value = np.array([
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -5,  0,  5,  5,  5,  5,  0, -5,
        0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ])
    king_value_middlegame = np.array([
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20,  0,  0,  0,  0, 20, 20,
        20, 30, 10,  0,  0, 10, 30, 20
    ])

    def evaluate(cb):
        w_moves_size = len(cb.get_legal_moves(Piece.WHITE))
        b_moves_size = len(cb.get_legal_moves(Piece.BLACK))

        w_queens = "{0:b}".format(np.bitwise_and(cb.pieceBB[Piece.WHITE], cb.pieceBB[Piece.QUEEN])).zfill(64)
        b_queens = "{0:b}".format(np.bitwise_and(cb.pieceBB[Piece.BLACK], cb.pieceBB[Piece.QUEEN])).zfill(64)

        w_rooks = "{0:b}".format(np.bitwise_and(cb.pieceBB[Piece.WHITE], cb.pieceBB[Piece.ROOK])).zfill(64)
        b_rooks = "{0:b}".format(np.bitwise_and(cb.pieceBB[Piece.BLACK], cb.pieceBB[Piece.ROOK])).zfill(64)
        
        w_bishops = "{0:b}".format(np.bitwise_and(cb.pieceBB[Piece.WHITE], cb.pieceBB[Piece.BISHOP])).zfill(64)
        b_bishops = "{0:b}".format(np.bitwise_and(cb.pieceBB[Piece.BLACK], cb.pieceBB[Piece.BISHOP])).zfill(64)

        w_knights = "{0:b}".format(np.bitwise_and(cb.pieceBB[Piece.WHITE], cb.pieceBB[Piece.KNIGHT])).zfill(64)
        b_knights = "{0:b}".format(np.bitwise_and(cb.pieceBB[Piece.BLACK], cb.pieceBB[Piece.KNIGHT])).zfill(64)

        w_pawns = "{0:b}".format(np.bitwise_and(cb.pieceBB[Piece.WHITE], cb.pieceBB[Piece.PAWN])).zfill(64)
        b_pawns = "{0:b}".format(np.bitwise_and(cb.pieceBB[Piece.BLACK], cb.pieceBB[Piece.PAWN])).zfill(64)

        w_pawn_score = Minimax.pawn_value * np.array([int(x) for x in w_pawns])
        b_pawn_score = list(reversed(Minimax.pawn_value)) * np.array([int(x) for x in b_pawns])

        w_knight_score = Minimax.knight_value * np.array([int(x) for x in w_knights])
        b_knight_score = list(reversed(Minimax.knight_value)) * np.array([int(x) for x in b_knights])

        w_bishop_score = Minimax.bishop_value * np.array([int(x) for x in w_bishops])
        b_bishop_score = list(reversed(Minimax.bishop_value)) * np.array([int(x) for x in b_bishops])

        w_rook_score = Minimax.rook_value * np.array([int(x) for x in w_rooks])
        b_rook_score = list(reversed(Minimax.rook_value)) * np.array([int(x) for x in b_rooks])

        w_queen_score = Minimax.queen_value * np.array([int(x) for x in w_queens])
        b_queen_score = list(reversed(Minimax.queen_value)) * np.array([int(x) for x in b_queens])

        evaluation = 1000*(w_queens.count("1")-b_queens.count("1")) + 525*(w_rooks.count("1")-b_rooks.count("1")) + 350*(w_bishops.count("1")-b_bishops.count("1")) + 350*(w_knights.count("1")-b_knights.count("1")) + (w_pawns.count("1")-b_pawns.count("1"))
        evaluation = evaluation + 10*(w_moves_size - b_moves_size)
        evaluation = evaluation + (np.sum(w_pawn_score) - np.sum(b_pawn_score))
        evaluation = evaluation + (np.sum(w_knight_score) - np.sum(b_knight_score))
        evaluation = evaluation + (np.sum(w_bishop_score) - np.sum(b_bishop_score))
        evaluation = evaluation + (np.sum(w_rook_score) - np.sum(b_rook_score))
        evaluation = evaluation + (np.sum(w_queen_score) - np.sum(b_queen_score))

        if cb.game_over: 
            evaluation = Minimax.infinite if cb.player_turn == Piece.BLACK else -Minimax.infinite

        evaluation = evaluation / 100

        return evaluation

    def searchABPruning(cb, depth, alpha=-infinite, beta=infinite):
        Minimax.node_number = Minimax.node_number + 1
        print("Alpha Beta Pruning number of nodes: %d\r"%Minimax.node_number, end="")
        if depth == 0 or cb.game_over: return Minimax.evaluate(cb)

        if cb.player_turn == Piece.WHITE:
            maxEval = -Minimax.infinite
            move_list = cb.get_legal_moves(cb.player_turn)
            og_position = cb.get_fen_position()
            for move in move_list:
                cb.move(move)
                maxEval = max(maxEval, Minimax.searchABPruning(cb, depth - 1, alpha, beta))
                alpha = max(alpha, maxEval)
                cb.load_fen_position(og_position)
                if alpha >= beta:
                    break
            return maxEval 
        else:
            minEval = Minimax.infinite
            move_list = cb.get_legal_moves(cb.player_turn)
            og_position = cb.get_fen_position()
            for move in move_list:
                cb.move(move)
                minEval = min(minEval, Minimax.searchABPruning(cb, depth - 1, alpha, beta))
                beta = min(beta, minEval)
                cb.load_fen_position(og_position)
                if beta <= alpha:
                    break
            return minEval
