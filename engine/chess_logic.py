import numpy as np
import pickle
import os
from engine.move_constants import Move, Piece, Square, Direction
import engine.move_generator as mgenerator

class Chess():
    def __init__(self):
        self.player_turn = Piece.WHITE
        self.game_over = False
        self.castleA1 = True
        self.castleH1 = True
        self.castleA8 = True
        self.castleH8 = True
        self.pinned_pieces = {}
        self.move_history = []
        self.generator = mgenerator.MoveGenerator()

        ## Initial Bitboard for piece and color ##
        ## Order by white, black, pawn, knight, bishop, rook, queen and king ##
        self.pieceBB = np.array((65535,
                                18446462598732840960,
                                71776119061282560,
                                4755801206503243842,
                                2594073385365405732,
                                9295429630892703873,
                                576460752303423496,
                                1152921504606846992), dtype=np.uint64)

        self.current_board = None
        self.update_current_board()

    def get_fen_position(self):
        fen = ""
        square = Square.A8
        fen_notation = {
            (Piece.BLACK, Piece.ROOK): "r", 
            (Piece.BLACK, Piece.KNIGHT): "n",
            (Piece.BLACK, Piece.BISHOP): "b",
            (Piece.BLACK, Piece.QUEEN): "q",
            (Piece.BLACK, Piece.KING): "k",
            (Piece.BLACK, Piece.PAWN): "p",
            (Piece.WHITE, Piece.ROOK): "R", 
            (Piece.WHITE, Piece.KNIGHT): "N",
            (Piece.WHITE, Piece.BISHOP): "B",
            (Piece.WHITE, Piece.QUEEN): "Q",
            (Piece.WHITE, Piece.KING): "K",
            (Piece.WHITE, Piece.PAWN): "P"
        }
        empty_square = 0

        while square >= 0:
            if self.current_board[square] is None:
                empty_square = empty_square + 1
            elif empty_square > 0:
                fen = fen + str(empty_square)
                empty_square = 0

            if self.current_board[square]:
                fen = fen + fen_notation[self.current_board[square]]

            if (square + 1) % 8 == 0:
                if empty_square > 0:
                    fen = fen + str(empty_square)
                    empty_square = 0

                if Square(square) is not Square.H1:
                    fen = fen + "/"
                square = square - 16
            
            square = square + 1

        fen = fen + " "

        fen = fen + "w" if self.player_turn == Piece.WHITE else fen + "b"

        fen = fen + " "

        if self.castleH1 or self.castleA1 or self.castleH8 or self.castleA8:
            if self.castleH1: fen = fen + "K"
            if self.castleA1: fen = fen + "Q"
            if self.castleH8: fen = fen + "k"
            if self.castleA8: fen = fen + "q"
        else:
            fen = fen + "-"

        fen = fen + " - 0 0"

        return fen

    #Load position in fen notation
    def load_fen_position(self, fen):
        square = Square.A8

        #Initialize an empty board
        self.move_history = []
        self.game_over = False
        self.castleH1 = False
        self.castleA1 = False
        self.castleH8 = False
        self.castleA8 = False
        self.pieceBB = np.array((0, 0, 0, 0, 0, 0, 0, 0), dtype=np.uint64)

        split_fen = fen.split()

        fen_notation = {
            "r": (Piece.BLACK, Piece.ROOK), 
            "n": (Piece.BLACK, Piece.KNIGHT),
            "b": (Piece.BLACK, Piece.BISHOP),
            "q": (Piece.BLACK, Piece.QUEEN),
            "k": (Piece.BLACK, Piece.KING),
            "p": (Piece.BLACK, Piece.PAWN),
            "R": (Piece.WHITE, Piece.ROOK), 
            "N": (Piece.WHITE, Piece.KNIGHT),
            "B": (Piece.WHITE, Piece.BISHOP),
            "Q": (Piece.WHITE, Piece.QUEEN),
            "K": (Piece.WHITE, Piece.KING),
            "P": (Piece.WHITE, Piece.PAWN)
        }

        #Set board
        for i in split_fen[0]:
            if square < 0: break
            square_bb = np.uint64(1) << np.uint64(square)
            
            if i in fen_notation:
                self.pieceBB[fen_notation[i][1]] = np.bitwise_or(self.pieceBB[fen_notation[i][1]], square_bb)
                self.pieceBB[fen_notation[i][0]] = np.bitwise_or(self.pieceBB[fen_notation[i][0]], square_bb)

            #Empty squares
            if i.isdigit():    
                square = square + int(i)
            #Jump to next line
            elif i == "/":
                square = square - 16
                continue
            #Else go to adjacent square
            else:
                square = square + 1

        #Set which color plays next move
        if split_fen[1] == "w":
            self.player_turn = Piece.WHITE
        elif split_fen[1] == "b":
            self.player_turn = Piece.BLACK
        
        #Set castling rights
        for i in split_fen[2]:
            if i == "-":
                break
            elif i == "K":
                self.castleH1 = True
            elif i == "Q":
                self.castleA1 = True
            elif i == "k":
                self.castleH8 = True
            elif i == "q":
                self.castleA8 = True

        self.update_current_board()

    ## Get all pieces sets ##
    def update_current_board(self):
        pieces = [None]*64

        white_pawn = np.bitwise_and(self.pieceBB[Piece.WHITE], self.pieceBB[Piece.PAWN])
        white_knight = np.bitwise_and(self.pieceBB[Piece.WHITE], self.pieceBB[Piece.KNIGHT])
        white_bishop = np.bitwise_and(self.pieceBB[Piece.WHITE], self.pieceBB[Piece.BISHOP])
        white_rook = np.bitwise_and(self.pieceBB[Piece.WHITE], self.pieceBB[Piece.ROOK])
        white_queen = np.bitwise_and(self.pieceBB[Piece.WHITE], self.pieceBB[Piece.QUEEN])
        white_king = np.bitwise_and(self.pieceBB[Piece.WHITE], self.pieceBB[Piece.KING])

        black_pawn = np.bitwise_and(self.pieceBB[Piece.BLACK], self.pieceBB[Piece.PAWN])
        black_knight = np.bitwise_and(self.pieceBB[Piece.BLACK], self.pieceBB[Piece.KNIGHT])
        black_bishop = np.bitwise_and(self.pieceBB[Piece.BLACK], self.pieceBB[Piece.BISHOP])
        black_rook = np.bitwise_and(self.pieceBB[Piece.BLACK], self.pieceBB[Piece.ROOK])
        black_queen = np.bitwise_and(self.pieceBB[Piece.BLACK], self.pieceBB[Piece.QUEEN])
        black_king = np.bitwise_and(self.pieceBB[Piece.BLACK], self.pieceBB[Piece.KING])

        for i in range(64):
            square = np.uint64(1) << np.uint64(i)
            if np.bitwise_and(square, white_pawn) > 0:
                pieces[i] = (Piece.WHITE, Piece.PAWN) 
            elif np.bitwise_and(square, white_knight) > 0:
                pieces[i] = (Piece.WHITE, Piece.KNIGHT) 
            elif np.bitwise_and(square, white_bishop) > 0:
                pieces[i] = (Piece.WHITE, Piece.BISHOP) 
            elif np.bitwise_and(square, white_rook) > 0:
                pieces[i] = (Piece.WHITE, Piece.ROOK) 
            elif np.bitwise_and(square, white_queen) > 0:
                pieces[i] = (Piece.WHITE, Piece.QUEEN) 
            elif np.bitwise_and(square, white_king) > 0:
                pieces[i] = (Piece.WHITE, Piece.KING)
            elif np.bitwise_and(square, black_pawn) > 0:
                pieces[i] = (Piece.BLACK, Piece.PAWN)  
            elif np.bitwise_and(square, black_knight) > 0:
                pieces[i] = (Piece.BLACK, Piece.KNIGHT)  
            elif np.bitwise_and(square, black_bishop) > 0:
                pieces[i] = (Piece.BLACK, Piece.BISHOP)  
            elif np.bitwise_and(square, black_rook) > 0:
                pieces[i] = (Piece.BLACK, Piece.ROOK)  
            elif np.bitwise_and(square, black_queen) > 0:
                pieces[i] = (Piece.BLACK, Piece.QUEEN)  
            elif np.bitwise_and(square, black_king) > 0:
                pieces[i] = (Piece.BLACK, Piece.KING)  
                
        self.current_board = pieces 

    # Called to move the rook when the move is castling
    def castle_rook(self, move):
        rook_square_from = 0
        rook_square_to = 0
        if move.square_to == Square.G1:
            rook_square_from = Square.H1
            rook_square_to = Square.F1
        elif move.square_to == Square.C1:
            rook_square_from = Square.A1
            rook_square_to = Square.D1
        elif move.square_to == Square.G8:
            rook_square_from = Square.H8
            rook_square_to = Square.F8
        else:
            rook_square_from = Square.A8
            rook_square_to = Square.D8

        fromBB = np.uint64(1) << np.uint64(rook_square_from)
        toBB = np.uint64(1) << np.uint64(rook_square_to)
        fromToBB = np.bitwise_xor(fromBB, toBB)
        self.pieceBB[move.piece_color] = np.bitwise_xor(fromToBB, self.pieceBB[move.piece_color])
        self.pieceBB[Piece.ROOK] = np.bitwise_xor(fromToBB, self.pieceBB[Piece.ROOK])

        if move.piece_color == Piece.WHITE:
            self.castleA1 = False
            self.castleH1 = False
        else:
            self.castleA8 = False
            self.castleH8 = False

    #Play a move
    def move(self, move):
        #Check if move is castling and move the rook   
        if move.castle:
            self.castle_rook(move)
        #Check if the king move and disable castling
        elif move.piece_type == Piece.KING:
            if move.piece_color == Piece.WHITE:
                self.castleA1 = False
                self.castleH1 = False
            else:
                self.castleA8 = False
                self.castleH8 = False
        #Check which rook move and disable castling
        elif move.piece_type == Piece.ROOK:  
            if move.square_from == Square.A1:
                self.castleA1 = False
            elif move.square_from == Square.H1:
                self.castleH1 = False
            elif move.square_from == Square.A8:
                self.castleA8 = False
            elif move.square_from == Square.H8:
                self.castleH8 = False

        fromBB = np.uint64(1) << np.uint64(move.square_from)
        toBB = np.uint64(1) << np.uint64(move.square_to)
        fromToBB = np.bitwise_xor(fromBB, toBB)

        if(move.is_capture()):
            self.pieceBB[move.cpiece_color] = np.bitwise_xor(toBB, self.pieceBB[move.cpiece_color])
            self.pieceBB[move.cpiece_type] = np.bitwise_xor(toBB, self.pieceBB[move.cpiece_type])

        self.pieceBB[move.piece_color] = np.bitwise_xor(fromToBB, self.pieceBB[move.piece_color])
        self.pieceBB[move.piece_type] = np.bitwise_xor(fromToBB, self.pieceBB[move.piece_type])

        self.move_history.append(move)

        #Switch player turn
        if self.player_turn == Piece.WHITE:
            self.player_turn = Piece.BLACK
        else:
            self.player_turn = Piece.WHITE

        # Update current board using the bitboards
        self.update_current_board()

    ## Returns all the legal moves on the current board given the player_color ##
    def get_legal_moves(self, player_color):
        moves = []
        self.pinned_pieces = {}
        opp_color = None
        opp_color = Piece.BLACK if player_color == Piece.WHITE else Piece.WHITE

        king_square = np.bitwise_and(self.pieceBB[player_color], self.pieceBB[Piece.KING])
        king_square = self.generator.get_lsb(king_square)

        attacks_to_king = self.attacks_to_square(king_square, player_color)
        occupied_squares = np.bitwise_or(self.pieceBB[Piece.WHITE], self.pieceBB[Piece.BLACK])

        # Calculate opponent attacks so the king doesnt walk to check
        opp_attacks = np.uint64(0)
        for i in range(len(self.current_board)):
            if self.current_board[i] == (opp_color, Piece.PAWN):
                opp_attacks = np.bitwise_or(self.generator.pawn_attacks[i][opp_color], opp_attacks)
            elif self.current_board[i] == (opp_color, Piece.KNIGHT):
                opp_attacks = np.bitwise_or(self.generator.knight_moves[i], opp_attacks)
            elif self.current_board[i] == (opp_color, Piece.BISHOP):
                blockerboard = np.bitwise_and(self.generator.bishop_masks[i], occupied_squares)
                opp_attacks = np.bitwise_or(self.generator.bishop_moveboard[i][blockerboard], opp_attacks)
            elif self.current_board[i] == (opp_color, Piece.ROOK):
                blockerboard = np.bitwise_and(self.generator.rook_masks[i], occupied_squares)
                opp_attacks = np.bitwise_or(self.generator.rook_moveboard[i][blockerboard], opp_attacks)
            elif self.current_board[i] == (opp_color, Piece.QUEEN):
                bishop_blockerboard = np.bitwise_and(self.generator.bishop_masks[i], occupied_squares)
                rook_blockerboard = np.bitwise_and(self.generator.rook_masks[i], occupied_squares)
                moveboard = np.bitwise_or(self.generator.bishop_moveboard[i][bishop_blockerboard], self.generator.rook_moveboard[i][rook_blockerboard])
                opp_attacks = np.bitwise_or(moveboard, opp_attacks)
        
        # Map pinned pieces to allowed moves
        rook_blockerboard = np.bitwise_and(occupied_squares, self.generator.rook_masks[king_square])
        rook_and_queen = np.bitwise_or(self.pieceBB[Piece.QUEEN], self.pieceBB[Piece.ROOK])
        opp_rook_queen = np.bitwise_and(rook_and_queen, self.pieceBB[opp_color])
        pinners = np.bitwise_and(self.generator.rook_xrays[king_square][rook_blockerboard], opp_rook_queen)
        while pinners > 0:
            pinner_square = self.generator.get_lsb(pinners)
            blocker_moves = np.bitwise_or(self.generator.rook_moveboard[king_square][rook_blockerboard], self.generator.rook_xrays[king_square][rook_blockerboard])
            blocker_moves = np.bitwise_and(blocker_moves, self.generator.rook_masks[pinner_square])
            blocker = np.bitwise_and(self.generator.rook_masks[pinner_square], self.generator.rook_moveboard[king_square][rook_blockerboard])
            blocker = np.bitwise_and(blocker, self.pieceBB[player_color])
            pinner_square = np.uint64(1) << np.uint64(pinner_square)
            blocker_moves = np.bitwise_or(blocker_moves, pinner_square)
            if blocker > 0:
                blocker_square = self.generator.get_lsb(blocker)
                self.pinned_pieces[blocker_square] = blocker_moves
            pinners = np.bitwise_xor(pinners, pinner_square)

        bishop_blockerboard = np.bitwise_and(occupied_squares, self.generator.bishop_masks[king_square])
        bishop_and_queen = np.bitwise_or(self.pieceBB[Piece.QUEEN], self.pieceBB[Piece.BISHOP])
        opp_bishop_queen = np.bitwise_and(bishop_and_queen, self.pieceBB[opp_color])
        pinners = np.bitwise_and(self.generator.bishop_xrays[king_square][bishop_blockerboard], opp_bishop_queen)
        while pinners > 0:
            pinner_square = self.generator.get_lsb(pinners)
            blocker_moves = np.bitwise_or(self.generator.bishop_moveboard[king_square][bishop_blockerboard], self.generator.bishop_xrays[king_square][bishop_blockerboard])
            blocker_moves = np.bitwise_and(blocker_moves, self.generator.bishop_masks[pinner_square])
            blocker = np.bitwise_and(self.generator.bishop_masks[pinner_square], self.generator.bishop_moveboard[king_square][bishop_blockerboard])
            blocker = np.bitwise_and(blocker, self.pieceBB[player_color])
            pinner_square = np.uint64(1) << np.uint64(pinner_square)
            blocker_moves = np.bitwise_or(blocker_moves, pinner_square)
            if blocker > 0:
                blocker_square = self.generator.get_lsb(blocker)
                self.pinned_pieces[blocker_square] = blocker_moves
            pinners = np.bitwise_xor(pinners, pinner_square)

        # There is no check
        if bin(attacks_to_king).count("1") == 0:
            for i in range(len(self.current_board)):
                if self.current_board[i] == (player_color, Piece.PAWN):
                    moves = moves + self.get_pawn_legal(player_color, i)
                elif self.current_board[i] == (player_color, Piece.KNIGHT):
                    moves = moves + self.get_knight_legal(player_color, i)
                elif self.current_board[i] == (player_color, Piece.BISHOP):
                    moves = moves + self.get_sliding_legal(player_color, i, Piece.BISHOP)
                elif self.current_board[i] == (player_color, Piece.ROOK):
                    moves = moves + self.get_sliding_legal(player_color, i, Piece.ROOK)
                elif self.current_board[i] == (player_color, Piece.QUEEN):
                    moves = moves + self.get_sliding_legal(player_color, i, Piece.QUEEN)
                elif self.current_board[i] == (player_color, Piece.KING):
                    moves = moves + self.get_king_legal(player_color, i, opp_attacks)
        # There is a single check            
        elif bin(attacks_to_king).count("1") == 1:
            # Get squares that can block the check
            attacker_square = self.generator.get_lsb(attacks_to_king)
            blocking_moves = None
            if self.current_board[attacker_square] == (opp_color, Piece.PAWN):
                blocking_moves = np.uint64(1 << attacker_square)
            elif self.current_board[attacker_square] == (opp_color, Piece.KNIGHT):
                blocking_moves = np.uint64(1 << attacker_square)
            elif self.current_board[attacker_square] == (opp_color, Piece.BISHOP):
                attacker_moves = np.bitwise_and(self.generator.bishop_masks[attacker_square], occupied_squares)
                king_moves = np.bitwise_and(self.generator.bishop_masks[king_square], occupied_squares)
                blocking_moves = np.bitwise_and(self.generator.bishop_moveboard[attacker_square][attacker_moves], self.generator.bishop_moveboard[king_square][king_moves])
                blocking_moves = np.bitwise_or(np.uint64(1 << attacker_square), blocking_moves)
            elif self.current_board[attacker_square] == (opp_color, Piece.ROOK):
                attacker_moves = np.bitwise_and(self.generator.rook_masks[attacker_square], occupied_squares)
                king_moves = np.bitwise_and(self.generator.rook_masks[king_square], occupied_squares)
                blocking_moves = np.bitwise_and(self.generator.rook_moveboard[attacker_square][attacker_moves], self.generator.rook_moveboard[king_square][king_moves])
                blocking_moves = np.bitwise_or(np.uint64(1 << attacker_square), blocking_moves)
            elif self.current_board[attacker_square] == (opp_color, Piece.QUEEN):
                # Check if its line check or diagonal check
                attacker_moves = None
                king_moves = None
                if abs(king_square - attacker_square) % 8 == 0 or (king_square//8) == (attacker_square//8):
                    attacker_moves = np.bitwise_and(self.generator.rook_masks[attacker_square], occupied_squares)
                    attacker_moves = self.generator.rook_moveboard[attacker_square][attacker_moves]
                    king_moves = np.bitwise_and(self.generator.rook_masks[king_square], occupied_squares)
                    king_moves = self.generator.rook_moveboard[king_square][king_moves]
                else:
                    attacker_moves = np.bitwise_and(self.generator.bishop_masks[attacker_square], occupied_squares)
                    attacker_moves = self.generator.bishop_moveboard[attacker_square][attacker_moves]
                    king_moves = np.bitwise_and(self.generator.bishop_masks[king_square], occupied_squares)
                    king_moves = self.generator.bishop_moveboard[king_square][king_moves]

                blocking_moves = np.bitwise_and(attacker_moves, king_moves)
                blocking_moves = np.bitwise_or(np.uint64(1 << attacker_square), blocking_moves)
            # Add moves that block the check or king moves
            for i in range(len(self.current_board)):
                if self.current_board[i] == (player_color, Piece.PAWN):
                    moves = moves + self.get_pawn_legal(player_color, i, blocking_moves)
                elif self.current_board[i] == (player_color, Piece.KNIGHT):
                    moves = moves + self.get_knight_legal(player_color, i, blocking_moves)
                elif self.current_board[i] == (player_color, Piece.BISHOP):
                    moves = moves + self.get_sliding_legal(player_color, i, Piece.BISHOP, blocking_moves)
                elif self.current_board[i] == (player_color, Piece.ROOK):
                    moves = moves + self.get_sliding_legal(player_color, i, Piece.ROOK, blocking_moves)
                elif self.current_board[i] == (player_color, Piece.QUEEN):
                    moves = moves + self.get_sliding_legal(player_color, i, Piece.QUEEN, blocking_moves)
                elif self.current_board[i] == (player_color, Piece.KING):
                    moves = moves + self.get_king_legal(player_color, i, opp_attacks)
        # Double check            
        else: 
            moves = moves + self.get_king_legal(player_color, king_square, opp_attacks)

        if not moves:
            self.game_over = True
        else:
            moves.sort(key=lambda x: x.is_capture(), reverse=True)

        return moves

    # Returns attacks to a square
    def attacks_to_square(self, square, piece_color):
        opp_color = None
        opp_color = Piece.BLACK if piece_color == Piece.WHITE else Piece.WHITE

        occupiedBB = np.bitwise_or(self.pieceBB[Piece.WHITE], self.pieceBB[Piece.BLACK])
        bishop_blockerboard = np.bitwise_and(self.generator.bishop_masks[square], occupiedBB)
        rook_blockerboard = np.bitwise_and(self.generator.rook_masks[square], occupiedBB)

        pawns = np.bitwise_and(self.pieceBB[opp_color], self.pieceBB[Piece.PAWN])
        knight = np.bitwise_and(self.pieceBB[opp_color], self.pieceBB[Piece.KNIGHT])
        bishop = np.bitwise_and(self.pieceBB[opp_color], self.pieceBB[Piece.BISHOP])
        rook = np.bitwise_and(self.pieceBB[opp_color], self.pieceBB[Piece.ROOK])
        queen = np.bitwise_and(self.pieceBB[opp_color], self.pieceBB[Piece.QUEEN])

        pawn_attack = np.bitwise_and(self.generator.pawn_attacks[square][piece_color], pawns)
        knight_attack = np.bitwise_and(self.generator.knight_moves[square], knight)
        bishop_attack = np.bitwise_and(self.generator.bishop_moveboard[square][bishop_blockerboard], bishop)
        rook_attack = np.bitwise_and(self.generator.rook_moveboard[square][rook_blockerboard], rook)
        queen_attack = np.bitwise_or(self.generator.bishop_moveboard[square][bishop_blockerboard], self.generator.rook_moveboard[square][rook_blockerboard])
        queen_attack = np.bitwise_and(queen_attack, queen)

        pawn_knight = np.bitwise_or(pawn_attack, knight_attack) 
        bishop_rook = np.bitwise_or(bishop_attack, rook_attack)

        return np.bitwise_or(np.bitwise_or(pawn_knight, bishop_rook), queen_attack)

    # Get a list of moves from a 64 bit moveboard
    def get_moves_from_moveboard(self, moveboard, square_from, piece_color, piece_type, capture=False):
        moves = []

        # If its pinned to king only allow moves in the pin line
        if square_from in self.pinned_pieces:
            moveboard = np.bitwise_and(moveboard, self.pinned_pieces[square_from])

        if capture:
            opp_color = None
            opp_color = Piece.BLACK if piece_color == Piece.WHITE else Piece.WHITE
            while moveboard > 0:
                square_to = self.generator.get_lsb(moveboard)
                captured_piece = self.current_board[square_to][1]
                move = Move(piece_color, piece_type, square_from, square_to, opp_color, captured_piece)
                moves.append(move)
                square_to = np.uint64(1) << np.uint64(square_to)
                moveboard = np.bitwise_xor(moveboard, square_to)
        else:
            while moveboard > 0:
                square_to = self.generator.get_lsb(moveboard)
                move = Move(piece_color, piece_type, square_from, square_to)
                moves.append(move)
                square_to = np.uint64(1) << np.uint64(square_to)
                moveboard = np.bitwise_xor(moveboard, square_to)

        return moves

    # Get king legal moves
    def get_king_legal(self, piece_color, square_from, opp_attacks):
        moves = []
        opp_pieces = None
        occupied_squares = np.bitwise_or(self.pieceBB[Piece.WHITE], self.pieceBB[Piece.BLACK])

        #Set opposite color and check if it can castle either side
        if piece_color == Piece.WHITE:
            opp_pieces = self.pieceBB[Piece.BLACK]
            if self.castleA1:
                castle_path = self.generator.ray_moves[square_from][Direction.WEST]
                castle_path = np.bitwise_and(castle_path, occupied_squares)
                if castle_path == np.uint64(1):
                    move = Move(piece_color, Piece.KING, square_from, Square.C1, castle = True)
                    moves.append(move)
            if self.castleH1:
                castle_path = self.generator.ray_moves[square_from][Direction.EAST]
                castle_path = np.bitwise_and(castle_path, occupied_squares)
                if castle_path == np.uint64(128):
                    move = Move(piece_color, Piece.KING, square_from, Square.G1, castle = True)
                    moves.append(move)
        else:
            opp_pieces = self.pieceBB[Piece.WHITE]
            if self.castleA8:
                castle_path = self.generator.ray_moves[square_from][Direction.WEST]
                castle_path = np.bitwise_and(castle_path, occupied_squares)
                if castle_path == np.uint64(72057594037927936):
                    move = Move(piece_color, Piece.KING, square_from, Square.C8, castle = True)
                    moves.append(move)
            if self.castleH8:
                castle_path = self.generator.ray_moves[square_from][Direction.EAST]
                castle_path = np.bitwise_and(castle_path, occupied_squares)
                if castle_path == np.uint64(9223372036854775808):
                    move = Move(piece_color, Piece.KING, square_from, Square.G8, castle = True)
                    moves.append(move)

        #Check for capture moves
        legal_moves = np.bitwise_and(self.generator.king_moves[square_from], np.bitwise_not(opp_attacks))
        capture_moves = np.bitwise_and(legal_moves, opp_pieces)
        moves.extend(self.get_moves_from_moveboard(capture_moves, square_from, piece_color, Piece.KING, True))

        #Check for push moves
        push_moves = np.bitwise_and(legal_moves, np.bitwise_not(occupied_squares))
        moves.extend(self.get_moves_from_moveboard(push_moves, square_from, piece_color, Piece.KING))

        return moves

    # Get pawn legal moves
    def get_pawn_legal(self, piece_color, square_from, blocking_moves=np.uint64(18446744073709551615)):
        moves = []
        opp_pieces = None

        if piece_color == Piece.WHITE:
            opp_pieces = self.pieceBB[Piece.BLACK]
        else:
            opp_pieces = self.pieceBB[Piece.WHITE]

        # Check for capture moves
        capture_moves = np.bitwise_and(self.generator.pawn_attacks[square_from][piece_color], opp_pieces)
        capture_moves = np.bitwise_and(capture_moves, blocking_moves)
        moves.extend(self.get_moves_from_moveboard(capture_moves, square_from, piece_color, Piece.PAWN, True))

        # Check pawn blockers
        occupied_squares = np.bitwise_or(self.pieceBB[Piece.WHITE], self.pieceBB[Piece.BLACK])
        blocker_mask = np.bitwise_and(self.generator.pawn_pushes[square_from][piece_color], occupied_squares)
        blocker_square = None
        if blocker_mask > 0:
            if piece_color == Piece.WHITE:
                blocker_square = self.generator.get_msb(blocker_mask)
            else:
                blocker_square = self.generator.get_lsb(blocker_mask)
            blocker_mask = np.bitwise_or(self.generator.pawn_pushes[blocker_square][piece_color], blocker_mask)

        # Check for push moves
        push_moves = np.bitwise_and(blocker_mask, self.generator.pawn_pushes[square_from][piece_color])
        push_moves = np.bitwise_xor(push_moves, self.generator.pawn_pushes[square_from][piece_color])
        push_moves = np.bitwise_and(push_moves, blocking_moves)
        moves.extend(self.get_moves_from_moveboard(push_moves, square_from, piece_color, Piece.PAWN))

        return moves

    # Get knight legal moves from a square
    def get_knight_legal(self, piece_color, square_from, blocking_moves=np.uint64(18446744073709551615)):
        moves = []
        opp_pieces = None

        if piece_color == Piece.WHITE:
            opp_pieces = self.pieceBB[Piece.BLACK]
        else:
            opp_pieces = self.pieceBB[Piece.WHITE]

        ## Check for capture moves ##
        capture_moves = np.bitwise_and(self.generator.knight_moves[square_from], opp_pieces)
        capture_moves = np.bitwise_and(capture_moves, blocking_moves)
        moves.extend(self.get_moves_from_moveboard(capture_moves, square_from, piece_color, Piece.KNIGHT, True))

        ## Check for push moves ##
        occupied_squares = np.bitwise_not(np.bitwise_or(self.pieceBB[Piece.WHITE], self.pieceBB[Piece.BLACK]))
        push_moves = np.bitwise_and(occupied_squares, self.generator.knight_moves[square_from]) 
        push_moves = np.bitwise_and(push_moves, blocking_moves)
        moves.extend(self.get_moves_from_moveboard(push_moves, square_from, piece_color, Piece.KNIGHT))
        
        return moves

    # Get bishop legal moves from a square
    def get_sliding_legal(self, piece_color, square_from, piece_type, blocking_moves=np.uint64(18446744073709551615)):
        moves = []
        opp_pieces = None

        if piece_color == Piece.WHITE:
            opp_pieces = self.pieceBB[Piece.BLACK]
            own_pieces = self.pieceBB[Piece.WHITE]
        else:
            opp_pieces = self.pieceBB[Piece.WHITE]
            own_pieces = self.pieceBB[Piece.BLACK]

        occupied_squares = np.bitwise_or(opp_pieces, own_pieces)
        moveboard = None

        if piece_type == Piece.BISHOP:
            blockerboard = np.bitwise_and(occupied_squares, self.generator.bishop_masks[square_from])
            moveboard = self.generator.bishop_moveboard[square_from][blockerboard]
        elif piece_type == Piece.ROOK:
            blockerboard = np.bitwise_and(occupied_squares, self.generator.rook_masks[square_from])
            moveboard = self.generator.rook_moveboard[square_from][blockerboard]
        else:
            blockerboard_bishop = np.bitwise_and(occupied_squares, self.generator.bishop_masks[square_from])
            moveboard_bishop = self.generator.bishop_moveboard[square_from][blockerboard_bishop]
            blockerboard_rook = np.bitwise_and(occupied_squares, self.generator.rook_masks[square_from])
            moveboard_rook = self.generator.rook_moveboard[square_from][blockerboard_rook]
            moveboard = np.bitwise_or(moveboard_bishop, moveboard_rook)

        moveboard = np.bitwise_and(moveboard, np.bitwise_not(own_pieces))

        # Check for capture moves ##
        ignore_captures = np.bitwise_and(moveboard, opp_pieces)
        capture_moves = np.bitwise_and(ignore_captures, blocking_moves)
        moves.extend(self.get_moves_from_moveboard(capture_moves, square_from, piece_color, piece_type, True))

        # Remove blocker and check for push moves ##
        push_moves = np.bitwise_xor(moveboard, ignore_captures) 
        push_moves = np.bitwise_and(push_moves, blocking_moves)
        moves.extend(self.get_moves_from_moveboard(push_moves, square_from, piece_color, piece_type))

        return moves
    
    #Utility function to print uin64 number like board
    def draw_bitboard(self, bitboard):
        bitboard = "{0:b}".format(bitboard).zfill(64)
        for i in range(8):
            for j in range(8):
                print(bitboard[(i*8 + 7-j)], end="")
            print("")
        print("")

