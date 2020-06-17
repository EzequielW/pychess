import enum
import numpy as np
import pickle
import os

class Piece(enum.IntEnum):
    WHITE = 0
    BLACK = 1
    PAWN = 2
    KNIGHT = 3
    BISHOP = 4
    ROOK = 5
    QUEEN = 6
    KING = 7

class Square(enum.IntEnum):
    (A1, B1, C1, D1, E1, F1, G1, H1,
    A2, B2, C2, D2, E2, F2, G2, H2,
    A3, B3, C3, D3, E3, F3, G3, H3,
    A4, B4, C4, D4, E4, F4, G4, H4,
    A5, B5, C5, D5, E5, F5, G5, H5,
    A6, B6, C6, D6, E6, F6, G6, H6,
    A7, B7, C7, D7, E7, F7, G7, H7,
    A8, B8, C8, D8, E8, F8, G8, H8) = range(64)

class Direction(enum.IntEnum):
    NORTH = 0
    EAST = 1
    NORTH_EAST = 2
    NORTH_WEST = 3
    SOUTH = 4
    WEST = 5
    SOUTH_EAST = 6
    SOUTH_WEST = 7

class Move():
    def __init__(self, piece_color, piece_type, square_from, square_to, cpiece_color = None, cpiece_type = None, castle = False):
        self.piece_color = piece_color
        self.piece_type = piece_type
        self.square_from = square_from
        self.square_to = square_to
        self.cpiece_color = cpiece_color
        self.cpiece_type = cpiece_type
        self.castle = castle
    
    def is_capture(self):
        if self.cpiece_color is not None:
            return True
        else:
            return False

class Engine():
    def __init__(self):
        self.player_turn = Piece.WHITE
        self.castleA1 = True
        self.castleH1 = True
        self.castleA8 = True
        self.castleH8 = True
        self.knight_moves = [None]*64
        self.ray_moves = [None]*64
        self.bishop_masks = [None]*64
        self.rook_masks = [None]*64
        self.king_moves = [None]*64
        self.pawn_attacks = [None]*64
        self.pawn_pushes = [None]*64
        self.bishop_moveboard = [None]*64
        self.rook_moveboard = [None]*64
        self.move_history = []
        ## Initial Bitboard for piece and color ##
        ## Order by white, black, pawn, knight, bishop, rook, queen and king ##

        # Load rook and bishop blockerboard to moveboard dictionaries
        if os.path.isfile("piece_movement.json"):
            print("---- loading piece movement ----")
            with (open('piece_movement.json', 'rb')) as openfile:
                piece_moveboard = pickle.load(openfile)
                self.rook_moveboard = piece_moveboard['rook_moveboard']
                self.bishop_moveboard = piece_moveboard['bishop_moveboard']

        self.pieceBB = np.array((65535,
                                18446462598732840960,
                                71776119061282560,
                                4755801206503243842,
                                2594073385365405732,
                                9295429630892703873,
                                576460752303423496,
                                1152921504606846992), dtype=np.uint64)
        ## Initialize moves for each piece ##
        for i in range(64):
            self.knight_moves[i] = self.get_knight_moves(i)
            self.ray_moves[i] = self.get_ray_moves(i)
            self.rook_masks[i] = self.get_rook_mask(i)
            self.bishop_masks[i] = self.get_bishop_mask(i)
            self.king_moves[i] = self.get_king_moves(i)
            self.pawn_attacks[i] = self.get_pawn_attacks(i)
            self.pawn_pushes[i] = self.get_pawn_pushes(i)

        if not os.path.isfile("piece_movement.json"):
            print("---- dumping piece movement ----")

            # Genereta all dictionaries for rook and bishops
            for i in range(64):
                self.rook_moveboard[i] = self.get_rook_attacks(i)
                self.bishop_moveboard[i] = self.get_bishop_attacks(i)

            piece_movement = {}
            piece_movement['rook_moveboard'] = self.rook_moveboard
            piece_movement['bishop_moveboard'] = self.bishop_moveboard

            with open('piece_movement.json', 'wb') as outfile:
                pickle.dump(piece_movement, outfile)
        
        ## Variables to avoid generating sets again ##
        self.white_pieces = None
        self.black_pieces = None
        self.all_pieces = None

    ## Get all pieces sets ##
    def get_all_pieces(self):
        pieces = [[None]*64 for n in range(2)]

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

        self.white_pieces = np.bitwise_or.reduce([white_pawn, white_knight, white_bishop, white_rook, white_queen, white_king])
        self.black_pieces = np.bitwise_or.reduce([black_pawn, black_knight, black_bishop, black_rook, black_queen, black_king])
            
        for j in range(64):
            if (white_pawn >> np.uint64(j)) % 2 == 1:
                pieces[Piece.WHITE][j] = Piece.PAWN 
            elif (white_knight >> np.uint64(j)) % 2 == 1:
                pieces[Piece.WHITE][j] = Piece.KNIGHT 
            elif (white_bishop >> np.uint64(j)) % 2 == 1:
                pieces[Piece.WHITE][j] = Piece.BISHOP 
            elif (white_rook >> np.uint64(j)) % 2 == 1:
                pieces[Piece.WHITE][j] = Piece.ROOK 
            elif (white_queen >> np.uint64(j)) % 2 == 1:
                pieces[Piece.WHITE][j] = Piece.QUEEN 
            elif (white_king >> np.uint64(j)) % 2 == 1:
                pieces[Piece.WHITE][j] = Piece.KING
            elif (black_pawn >> np.uint64(j)) % 2 == 1:
                pieces[Piece.BLACK][j] = Piece.PAWN
            elif (black_knight >> np.uint64(j)) % 2 == 1:
                pieces[Piece.BLACK][j] = Piece.KNIGHT
            elif (black_bishop >> np.uint64(j)) % 2 == 1:
                pieces[Piece.BLACK][j] = Piece.BISHOP
            elif (black_rook >> np.uint64(j)) % 2 == 1:
                pieces[Piece.BLACK][j] = Piece.ROOK
            elif (black_queen >> np.uint64(j)) % 2 == 1:
                pieces[Piece.BLACK][j] = Piece.QUEEN
            elif (black_king >> np.uint64(j)) % 2 == 1:
                pieces[Piece.BLACK][j] = Piece.KING
                
        return pieces        
 
    ## Get least significant bit ##
    def get_lsb(self, n):
        i=0
        while((n>>np.uint64(i))%2==0):
            i+=1

        return i

    ## Get most significant bit ##
    def get_msb(self, n):
        i=63
        while((n>>np.uint64(i))%2==0 and i != 0):
            i-=1

        return i

    #Play a move
    def move(self, move):
        #Check if move is castling and move the rook   
        if move.castle:
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

    #Generate a unique blocker board, given an index (0..2^bits) and the blocker mask 
    #for the piece/square. Each index will give a unique blocker board. 
    def gen_blockerboard(self, index, blockermask):
        blockerboard = blockermask
        bitindex = 0

        for i in range(64):
            if np.bitwise_and(blockermask, np.uint64(1 << i)) != 0:
                if (np.bitwise_and(index, (1 << bitindex))) == 0:
                    blockerboard = np.bitwise_and(blockerboard, np.bitwise_not(np.uint64(1 << i)))
                bitindex = bitindex + 1

        return blockerboard

    #Get attacks to a square of a color
    def attacks_to_square(self, square, color):
        opp_color = None
        if color == Piece.WHITE:
            opp_color = Piece.BLACK
        else:
            opp_color = Piece.WHITE

        occupiedBB = np.bitwise_or(self.pieceBB[Piece.WHITE], self.pieceBB[Piece.BLACK])

        pawns = np.bitwise_and(self.pieceBB[opp_color], self.pieceBB[Piece.PAWN])
        knight = np.bitwise_and(self.pieceBB[opp_color], self.pieceBB[Piece.KNIGHT])
        bishop = np.bitwise_and(self.pieceBB[opp_color], self.pieceBB[Piece.BISHOP])
        rook = np.bitwise_and(self.pieceBB[opp_color], self.pieceBB[Piece.ROOK])
        queen = np.bitwise_or(self.pieceBB[opp_color], self.pieceBB[Piece.QUEEN])

        pawn_attack = np.bitwise_and(self.pawn_attacks[color][square], pawns)
        knight_attack = np.bitwise_and(self.knight_moves[square], knight)
        bishop_attack = np.bitwise_and(self.bishop_moveboard[square][occupiedBB], bishop)
        rook_attack = np.bitwise_and(self.rook_moveboard[square][occupiedBB], rook)
        queen_attack = np.bitwise_or(self.bishop_moveboard[square][occupiedBB], self.rook_moveboard[square][occupiedBB])
        queen_attack = np.bitwise_and(queen_attack, queen)

        pawn_knight = np.bitwise_or(pawn_attack, knight_attack) 
        bishop_rook = np.bitwise_or(bishop_attack, rook_attack)

        return np.bitwise_or(np.bitwise_or(pawn_knight, bishop_rook), queen_attack)

    ## Check ranks and files ##
    def is_afile(self, square):
        return square % 8 == 0
        
    def is_bfile(self, square):
        return (square - 1) % 8 == 0

    def is_gfile(self, square):
        return (square + 2) % 8 == 0

    def is_hfile(self, square):
        return (square + 1) % 8 == 0

    def is_first_rank(self, square):
        return  square >= Square.A1 and square <= Square.H1
    
    def is_second_rank(self, square):
        return  square >= Square.A2 and square <= Square.H2

    def is_seventh_rank(self, square):
        return  square >= Square.A7 and square <= Square.H7

    def is_eight_rank(self, square):
        return  square >= Square.A8 and square <= Square.H8

    ## Returns all the legal moves on the current board given the players_turn ##
    def get_legal_moves(self, player_color):
        moves = [None] * 64

        self.all_pieces = self.get_all_pieces()

        for i in range(len(moves)):
            square_moves = None

            if self.all_pieces[player_color][i] == Piece.PAWN:
                square_moves = self.get_pawn_legal(player_color, i)
            elif self.all_pieces[player_color][i] == Piece.KNIGHT:
                square_moves = self.get_knight_legal(player_color, i)
            elif self.all_pieces[player_color][i] == Piece.BISHOP:
                square_moves = self.get_sliding_legal(player_color, i, Piece.BISHOP)
            elif self.all_pieces[player_color][i] == Piece.ROOK:
                square_moves = self.get_sliding_legal(player_color, i, Piece.ROOK)
            elif self.all_pieces[player_color][i] == Piece.QUEEN:
                square_moves = self.get_sliding_legal(player_color, i, Piece.QUEEN)
            elif self.all_pieces[player_color][i] == Piece.KING:
                square_moves = self.get_king_legal(player_color, i)

            moves[i] = square_moves
        return moves

    ## Get king legal moves ##
    def get_king_legal(self, color, square_from):
        moves = []
        opp_pieces = None
        opp_color = None

        #Set opposite color and check if it can castle either side
        if color == Piece.WHITE:
            opp_pieces = self.black_pieces
            opp_color = Piece.BLACK
            if self.castleA1:
                castle_path = self.ray_moves[square_from][Direction.WEST]
                all_set = np.bitwise_or(self.white_pieces, self.black_pieces)
                castle_path = np.bitwise_and(castle_path, all_set)
                if castle_path == np.uint64(1):
                    move = Move(color, Piece.KING, square_from, Square.C1, castle = True)
                    moves.append(move)
            if self.castleH1:
                castle_path = self.ray_moves[square_from][Direction.EAST]
                all_set = np.bitwise_or(self.white_pieces, self.black_pieces)
                castle_path = np.bitwise_and(castle_path, all_set)
                if castle_path == np.uint64(128):
                    move = Move(color, Piece.KING, square_from, Square.G1, castle = True)
                    moves.append(move)
        else:
            opp_pieces = self.white_pieces
            opp_color = Piece.WHITE
            if self.castleA8:
                castle_path = self.ray_moves[square_from][Direction.WEST]
                all_set = np.bitwise_or(self.white_pieces, self.black_pieces)
                castle_path = np.bitwise_and(castle_path, all_set)
                if castle_path == np.uint64(72057594037927936):
                    move = Move(color, Piece.KING, square_from, Square.C8, castle = True)
                    moves.append(move)
            if self.castleH8:
                castle_path = self.ray_moves[square_from][Direction.EAST]
                all_set = np.bitwise_or(self.white_pieces, self.black_pieces)
                castle_path = np.bitwise_and(castle_path, all_set)
                if castle_path == np.uint64(9223372036854775808):
                    move = Move(color, Piece.KING, square_from, Square.G8, castle = True)
                    moves.append(move)

        #Check for capture moves
        capture_moves = np.bitwise_and(self.king_moves[square_from], opp_pieces)
        while capture_moves > 0:
            square_to = self.get_lsb(capture_moves)
            captured_piece = self.all_pieces[opp_color][square_to]
            move = Move(color, Piece.KING, square_from, square_to, opp_color, captured_piece)
            moves.append(move)
            square_to = np.uint64(1) << np.uint64(square_to)
            capture_moves = np.bitwise_xor(capture_moves, square_to)

        #Check for push moves
        all_set = np.bitwise_or(self.white_pieces, self.black_pieces)
        push_moves = np.bitwise_and(self.king_moves[square_from], np.bitwise_not(all_set))
        while push_moves > 0:
            square_to = self.get_lsb(push_moves)
            move = Move(color, Piece.KING, square_from, square_to)
            moves.append(move)
            square_to = np.uint64(1) << np.uint64(square_to)
            push_moves = np.bitwise_xor(push_moves, square_to)

        return moves

    ## Get pawn legal moves ##
    def get_pawn_legal(self, color, square_from):
        moves = []
        opp_pieces = None
        opp_color = None

        if color == Piece.WHITE:
            opp_pieces = self.black_pieces
            opp_color = Piece.BLACK
        else:
            opp_pieces = self.white_pieces
            opp_color = Piece.WHITE

        ## Check for capture moves ##
        capture_moves = np.bitwise_and(self.pawn_attacks[square_from][color], opp_pieces)
        while capture_moves > 0:
            square_to = self.get_lsb(capture_moves)
            captured_piece = self.all_pieces[opp_color][square_to]
            move = Move(color, Piece.PAWN, square_from, square_to, opp_color, captured_piece)
            moves.append(move)
            square_to = np.uint64(1) << np.uint64(square_to)
            capture_moves = np.bitwise_xor(capture_moves, square_to)

        ## Check pawn blockers ##
        all_set = np.bitwise_or(self.white_pieces, self.black_pieces)
        blocker_mask = np.bitwise_and(self.pawn_pushes[square_from][color], all_set)
        blocker_square = None
        if blocker_mask > 0:
            if color == Piece.WHITE:
                blocker_square = self.get_msb(blocker_mask)
            else:
                blocker_square = self.get_lsb(blocker_mask)
            blocker_mask = np.bitwise_or(self.pawn_pushes[blocker_square][color], blocker_mask)

        ## Check for push moves ##
        push_moves = np.bitwise_and(blocker_mask, self.pawn_pushes[square_from][color])
        push_moves = np.bitwise_xor(push_moves, self.pawn_pushes[square_from][color])
        while push_moves > 0:
            square_to = self.get_lsb(push_moves)
            move = Move(color, Piece.PAWN, square_from, square_to)
            moves.append(move)
            square_to = np.uint64(1) << np.uint64(square_to)
            push_moves = np.bitwise_xor(push_moves, square_to)

        return moves

    ## Get knight legal moves from a square ## 
    def get_knight_legal(self, color, square_from):
        moves = []
        opp_pieces = None
        opp_color = None

        if color == Piece.WHITE:
            opp_pieces = self.black_pieces
            opp_color = Piece.BLACK
        else:
            opp_pieces = self.white_pieces
            opp_color = Piece.WHITE

        ## Check for capture moves ##
        capture_moves = np.bitwise_and(self.knight_moves[square_from], opp_pieces)
        while capture_moves > 0:
            square_to = self.get_lsb(capture_moves)
            captured_piece = self.all_pieces[opp_color][square_to]
            move = Move(color, Piece.KNIGHT, square_from, square_to, opp_color, captured_piece)
            moves.append(move)
            square_to = np.uint64(1) << np.uint64(square_to)
            capture_moves = np.bitwise_xor(capture_moves, square_to)

        ## Check for push moves ##
        occupy_squares = np.bitwise_not(np.bitwise_or(self.white_pieces, self.black_pieces))
        push_moves = np.bitwise_and(occupy_squares, self.knight_moves[square_from]) 
        while push_moves > 0:
            square_to = self.get_lsb(push_moves)
            move = Move(color, Piece.KNIGHT, square_from, square_to)
            moves.append(move)
            square_to = np.uint64(1) << np.uint64(square_to)
            push_moves = np.bitwise_xor(push_moves, square_to)
        
        return moves

    # Get bishop legal moves from a square
    def get_sliding_legal(self, color, square_from, piece_type):
        moves = []
        opp_pieces = None
        opp_color = None

        if color == Piece.WHITE:
            opp_pieces = self.black_pieces
            own_pieces = self.white_pieces
            opp_color = Piece.BLACK
        else:
            opp_pieces = self.white_pieces
            own_pieces = self.black_pieces
            opp_color = Piece.WHITE

        all_set = np.bitwise_or(opp_pieces, own_pieces)
        moveboard = None

        if piece_type == Piece.BISHOP:
            blockerboard = np.bitwise_and(all_set, self.bishop_masks[square_from])
            moveboard = self.bishop_moveboard[square_from][blockerboard]
        elif piece_type == Piece.ROOK:
            blockerboard = np.bitwise_and(all_set, self.rook_masks[square_from])
            moveboard = self.rook_moveboard[square_from][blockerboard]
        else:
            blockerboard_bishop = np.bitwise_and(all_set, self.bishop_masks[square_from])
            moveboard_bishop = self.bishop_moveboard[square_from][blockerboard_bishop]
            blockerboard_rook = np.bitwise_and(all_set, self.rook_masks[square_from])
            moveboard_rook = self.rook_moveboard[square_from][blockerboard_rook]
            moveboard = np.bitwise_or(moveboard_bishop, moveboard_rook)

        moveboard = np.bitwise_and(moveboard, np.bitwise_not(own_pieces))

        # Check for capture moves ##
        ignore_captures = np.bitwise_and(moveboard, opp_pieces)
        capture_moves = ignore_captures
        while capture_moves > 0:
            square_to = self.get_lsb(capture_moves)
            captured_piece = self.all_pieces[opp_color][square_to]
            move = Move(color, piece_type, square_from, square_to, opp_color, captured_piece)
            moves.append(move)
            square_to = np.uint64(1) << np.uint64(square_to)
            capture_moves = np.bitwise_xor(capture_moves, square_to)

        # Remove blocker and check for push moves ##
        push_moves = np.bitwise_xor(moveboard, ignore_captures) 
        while push_moves > 0:
            square_to = self.get_lsb(push_moves)
            move = Move(color, piece_type, square_from, square_to)
            moves.append(move)
            square_to = np.uint64(1) << np.uint64(square_to)
            push_moves = np.bitwise_xor(push_moves, square_to)

        return moves

    ## Fill pawn attacks ##
    def get_pawn_attacks(self, square):
        moves = [None]*2

        if self.is_afile(square):
            moves[Piece.WHITE] = np.uint64(1024)
            moves[Piece.BLACK] = np.uint64(1024)
        elif self.is_hfile(square):
            moves[Piece.WHITE] = np.uint64(256)
            moves[Piece.BLACK] = np.uint64(256)
        else:
            moves[Piece.WHITE] = np.uint64(1280)
            moves[Piece.BLACK] = np.uint64(1280)

        white_shift = square - 1  
        black_shift = square - 17

        if white_shift >= 0: 
            moves[Piece.WHITE] = moves[Piece.WHITE] << np.uint64(white_shift)
        else:
            moves[Piece.WHITE] = moves[Piece.WHITE] >> np.uint64(white_shift*-1)
        
        if black_shift >= 0: 
            moves[Piece.BLACK] = moves[Piece.BLACK] << np.uint64(black_shift)
        else:
            moves[Piece.BLACK] = moves[Piece.BLACK] >> np.uint64(black_shift*-1)

        return moves

    ## Fill pawn pushes ##
    def get_pawn_pushes(self, square):
        moves = [None]*2

        if self.is_second_rank(square):
            moves[Piece.WHITE] = np.uint64(65792)
            moves[Piece.BLACK] = np.uint64(256)
        elif self.is_seventh_rank(square):
            moves[Piece.WHITE] = np.uint64(256)
            moves[Piece.BLACK] = np.uint64(257)
        else:
            moves[Piece.WHITE] = np.uint64(256)
            moves[Piece.BLACK] = np.uint64(256)
  
        black_shift = square - 16

        moves[Piece.WHITE] = moves[Piece.WHITE] << np.uint64(square)
        
        if black_shift >= 0: 
            moves[Piece.BLACK] = moves[Piece.BLACK] << np.uint64(black_shift)
        else:
            moves[Piece.BLACK] = moves[Piece.BLACK] >> np.uint64(black_shift*-1)

        return moves

    ## Fill knight moves ##
    def get_knight_moves(self, square):
        moves = None

        if self.is_afile(square):
            moves = np.uint64(34628177928)
        elif self.is_bfile(square):
            moves = np.uint64(43218112522)
        elif self.is_gfile(square):
            moves = np.uint64(42966450442)
        elif self.is_hfile(square):
            moves = np.uint64(8606712066)
        else:
            moves = np.uint64(43234889994)

        shift_size = square - 18  

        if shift_size >= 0: 
            moves = moves << np.uint64(shift_size)
        else:
            moves = moves >> np.uint64(shift_size*-1)

        return moves
    
    ## Fill rook and bishop (queen) moves ##
    def get_ray_moves(self, square):
        moves = [None]*8
        piece_rank = square//8
        piece_file = square%8

        ## Calculate lines ##

        north = np.uint64(72340172838076672) << np.uint64(square)
        moves[Direction.NORTH] = north

        south = np.uint64(282578800148737) >> np.uint64((7 - piece_rank)*8)
        south = south << np.uint64(piece_file)
        moves[Direction.SOUTH] = south

        east = np.uint64(2**(7 - piece_file) - 1) << np.uint64(square + 1)
        moves[Direction.EAST] = east
        
        west = np.uint64(2**(piece_file) - 1) << np.uint64(square - piece_file)
        moves[Direction.WEST] = west

        ## Calculate diagonals ##

        north_east = np.uint64(9241421688590303744) << np.uint64(square)
        wrap_size = piece_file - 1 - piece_rank
        for i in range(wrap_size):
            north_east = np.bitwise_xor(north_east, (np.uint64(1) << np.uint64(self.get_msb(north_east))))
        moves[Direction.NORTH_EAST] = north_east

        north_west = np.uint64(567382630219904) << np.uint64(square)
        wrap_size = 8 - piece_file - piece_rank if piece_rank != 0 else 7 - piece_file
        for i in range(wrap_size):
            north_west = np.bitwise_xor(north_west, (np.uint64(1) << np.uint64(self.get_msb(north_west))))
        moves[Direction.NORTH_WEST] = north_west

        south_east = np.uint64(72624976668147712) >> np.uint64(63 - square)
        wrap_size = piece_file + piece_rank - 6 if piece_rank != 7 else piece_file
        for i in range(wrap_size):
            south_east = np.bitwise_xor(south_east, (np.uint64(1) << np.uint64(self.get_lsb(south_east))))
        moves[Direction.SOUTH_EAST] = south_east

        south_west = np.uint64(18049651735527937) >> np.uint64(63 - square)
        wrap_size = piece_rank - piece_file - 1
        for i in range(wrap_size):
            south_west = np.bitwise_xor(south_west, (np.uint64(1) << np.uint64(self.get_lsb(south_west))))
        moves[Direction.SOUTH_WEST] = south_west

        return moves

    # Fill bishop moves
    def get_bishop_mask(self, square):
        mask = None

        north_west = np.bitwise_and(np.uint64(18374403900871474688), self.ray_moves[square][Direction.NORTH_WEST])
        south_west = np.bitwise_and(np.uint64(71775015237779198), self.ray_moves[square][Direction.SOUTH_WEST])
        north_east = np.bitwise_and(np.uint64(9187201950435737344), self.ray_moves[square][Direction.NORTH_EAST])
        south_east = np.bitwise_and(np.uint64(35887507618889599), self.ray_moves[square][Direction.SOUTH_EAST])

        west = np.bitwise_or(north_west, south_west)  
        east = np.bitwise_or(north_east, south_east)
        mask = np.bitwise_or(west, east)

        return mask

    # Get move board from a blocker board for bishop
    def get_bishop_moveboard(self, square, blocker_board):
        west = np.bitwise_or(self.ray_moves[square][Direction.NORTH_WEST], self.ray_moves[square][Direction.SOUTH_WEST])
        east = np.bitwise_or(self.ray_moves[square][Direction.NORTH_EAST], self.ray_moves[square][Direction.SOUTH_EAST])
        moveboard = np.bitwise_or(west, east)

        nwest_blocker = np.bitwise_and(self.ray_moves[square][Direction.NORTH_WEST], blocker_board)
        if nwest_blocker != 0:
            first_blocker = self.get_lsb(nwest_blocker)
            moveboard = np.bitwise_xor(self.ray_moves[first_blocker][Direction.NORTH_WEST], moveboard)
        
        neast_blocker = np.bitwise_and(self.ray_moves[square][Direction.NORTH_EAST], blocker_board)
        if neast_blocker != 0:
            first_blocker = self.get_lsb(neast_blocker)
            moveboard = np.bitwise_xor(self.ray_moves[first_blocker][Direction.NORTH_EAST], moveboard)
        
        swest_blocker = np.bitwise_and(self.ray_moves[square][Direction.SOUTH_WEST], blocker_board)
        if swest_blocker != 0:
            first_blocker = self.get_msb(swest_blocker)
            moveboard = np.bitwise_xor(self.ray_moves[first_blocker][Direction.SOUTH_WEST], moveboard)
        
        seast_blocker = np.bitwise_and(self.ray_moves[square][Direction.SOUTH_EAST], blocker_board)
        if seast_blocker != 0:
            first_blocker = self.get_msb(seast_blocker)
            moveboard = np.bitwise_xor(self.ray_moves[first_blocker][Direction.SOUTH_EAST], moveboard)

        return moveboard

    # Get dictionary of keys: blockerboard values: moveboard , from a square
    def get_bishop_attacks(self, square):
        blockermask = self.bishop_masks[square]
        bits = bin(blockermask).count("1")

        blockerboard_to_moveboard = {}

        for j in range((1<<bits)):
            blockerboard = self.gen_blockerboard(j, blockermask)
            blockerboard_to_moveboard[blockerboard] = self.get_bishop_moveboard(square, blockerboard)

        return blockerboard_to_moveboard

    # Fill rook moves 
    def get_rook_mask(self, square):
        mask = None 

        west = np.bitwise_and(np.uint64(18374403900871474942), self.ray_moves[square][Direction.WEST])
        east = np.bitwise_and(np.uint64(9187201950435737471), self.ray_moves[square][Direction.EAST])
        north = np.bitwise_and(np.uint64(72057594037927935), self.ray_moves[square][Direction.NORTH])
        south = np.bitwise_and(np.uint64(18446744073709551360), self.ray_moves[square][Direction.SOUTH])
        
        west_east = np.bitwise_or(west, east)
        north_south = np.bitwise_or(north, south)
        mask = np.bitwise_or(west_east, north_south)

        return mask

    # Get move board from a blocker board for rook
    def get_rook_moveboard(self, square, blocker_board):
        north_south = np.bitwise_or(self.ray_moves[square][Direction.NORTH], self.ray_moves[square][Direction.SOUTH])
        west_east = np.bitwise_or(self.ray_moves[square][Direction.WEST], self.ray_moves[square][Direction.EAST])
        moveboard = np.bitwise_or(north_south, west_east)

        north_blocker = np.bitwise_and(self.ray_moves[square][Direction.NORTH], blocker_board)
        if north_blocker != 0:
            first_blocker = self.get_lsb(north_blocker)
            moveboard = np.bitwise_xor(self.ray_moves[first_blocker][Direction.NORTH], moveboard)
        
        south_blocker = np.bitwise_and(self.ray_moves[square][Direction.SOUTH], blocker_board)
        if south_blocker != 0:
            first_blocker = self.get_msb(south_blocker)
            moveboard = np.bitwise_xor(self.ray_moves[first_blocker][Direction.SOUTH], moveboard)
        
        east_blocker = np.bitwise_and(self.ray_moves[square][Direction.EAST], blocker_board)
        if east_blocker != 0:
            first_blocker = self.get_lsb(east_blocker)
            moveboard = np.bitwise_xor(self.ray_moves[first_blocker][Direction.EAST], moveboard)
        
        west_blocker = np.bitwise_and(self.ray_moves[square][Direction.WEST], blocker_board)
        if west_blocker != 0:
            first_blocker = self.get_msb(west_blocker)
            moveboard = np.bitwise_xor(self.ray_moves[first_blocker][Direction.WEST], moveboard)

        return moveboard

    # Get dictionary of keys: blockerboard values: moveboard , from a square
    def get_rook_attacks(self, square):
        blockermask = self.rook_masks[square]
        bits = bin(blockermask).count("1")

        blockerboard_to_moveboard = {}

        for j in range((1<<bits)):
            blockerboard = self.gen_blockerboard(j, blockermask)
            blockerboard_to_moveboard[blockerboard] = self.get_rook_moveboard(square, blockerboard)

        return blockerboard_to_moveboard


    ## Fill king moves ##
    def get_king_moves(self, square):
        moves = None

        if self.is_afile(square):
            moves = np.uint64(394246)
        elif self.is_hfile(square):
            moves = np.uint64(196867)
        else:
            moves = np.uint64(460039)

        shift_size = square - 9  

        if shift_size >= 0: 
            moves = moves << np.uint64(shift_size)
        else:
            moves = moves >> np.uint64(shift_size*-1)

        return moves
    
    #Utility function to print bitboard
    def draw_bin(self, number):
        number = "{0:b}".format(number).zfill(64)
        for i in range(8):
            for j in range(8):
                print(number[(i*8 + 7-j)], end="")
            print("")
        print("")

