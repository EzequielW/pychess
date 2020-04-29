import enum
import numpy as np

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
    def __init__(self, piece_color, piece_type, square_from, square_to, cpiece_color = None, cpiece_type = None):
        self.piece_color = piece_color
        self.piece_type = piece_type
        self.square_from = square_from
        self.square_to = square_to
        self.cpiece_color = cpiece_color
        self.cpiece_type = cpiece_type
    
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
        self.king_moves = [None]*64
        self.pawn_attacks = [None]*64
        self.pawn_pushes = [None]*64
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
        ## Initialize moves for each piece ##
        for i in range(64):
            self.knight_moves[i] = self.get_knight_moves(i)
            self.ray_moves[i] = self.get_ray_moves(i)
            self.king_moves[i] = self.get_king_moves(i)
            self.pawn_attacks[i] = self.get_pawn_attacks(i)
            self.pawn_pushes[i] = self.get_pawn_pushes(i)
        
        ## Variables to avoid generating sets again ##
        self.white_pieces = None
        self.black_pieces = None
        self.all_pieces = None

    ## Get join set between any two sets ##
    def get_piece_set(self, first_set, second_set):
        return np.bitwise_and(self.pieceBB[first_set], self.pieceBB[second_set])

    ## Get all pieces sets ##
    def get_all_pieces(self):
        pieces = [[None]*64 for n in range(2)]

        white_pawn = self.get_piece_set(Piece.WHITE, Piece.PAWN)
        white_knight = self.get_piece_set(Piece.WHITE, Piece.KNIGHT)
        white_bishop = self.get_piece_set(Piece.WHITE, Piece.BISHOP)
        white_rook = self.get_piece_set(Piece.WHITE, Piece.ROOK)
        white_queen = self.get_piece_set(Piece.WHITE, Piece.QUEEN)
        white_king = self.get_piece_set(Piece.WHITE, Piece.KING)

        black_pawn = self.get_piece_set(Piece.BLACK, Piece.PAWN)
        black_knight = self.get_piece_set(Piece.BLACK, Piece.KNIGHT)
        black_bishop = self.get_piece_set(Piece.BLACK, Piece.BISHOP)
        black_rook = self.get_piece_set(Piece.BLACK, Piece.ROOK)
        black_queen = self.get_piece_set(Piece.BLACK, Piece.QUEEN)
        black_king = self.get_piece_set(Piece.BLACK, Piece.KING)
            
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

    ## Play a move ##
    def move(self, move):      
        fromBB = np.uint64(1) << np.uint64(move.square_from)
        toBB = np.uint64(1) << np.uint64(move.square_to)
        fromToBB = np.bitwise_xor(fromBB, toBB)

        if(move.is_capture()):
            self.pieceBB[move.cpiece_color] = np.bitwise_xor(toBB, self.pieceBB[move.cpiece_color])
            self.pieceBB[move.cpiece_type] = np.bitwise_xor(toBB, self.pieceBB[move.cpiece_type])

        self.pieceBB[move.piece_color] = np.bitwise_xor(fromToBB, self.pieceBB[move.piece_color])
        self.pieceBB[move.piece_type] = np.bitwise_xor(fromToBB, self.pieceBB[move.piece_type])

        

        if self.player_turn == Piece.WHITE:
            self.player_turn = Piece.BLACK
        else:
            self.player_turn = Piece.WHITE

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
    def get_legal_moves(self):
        moves = [None] * 64

        white_pawn = self.get_piece_set(Piece.WHITE, Piece.PAWN)
        white_knight = self.get_piece_set(Piece.WHITE, Piece.KNIGHT)
        white_bishop = self.get_piece_set(Piece.WHITE, Piece.BISHOP)
        white_rook = self.get_piece_set(Piece.WHITE, Piece.ROOK)
        white_queen = self.get_piece_set(Piece.WHITE, Piece.QUEEN)
        white_king = self.get_piece_set(Piece.WHITE, Piece.KING)

        self.white_pieces = np.bitwise_or.reduce([white_pawn, white_knight, white_bishop, white_rook, white_queen, white_king])

        black_pawn = self.get_piece_set(Piece.BLACK, Piece.PAWN)
        black_knight = self.get_piece_set(Piece.BLACK, Piece.KNIGHT)
        black_bishop = self.get_piece_set(Piece.BLACK, Piece.BISHOP)
        black_rook = self.get_piece_set(Piece.BLACK, Piece.ROOK)
        black_queen = self.get_piece_set(Piece.BLACK, Piece.QUEEN)
        black_king = self.get_piece_set(Piece.BLACK, Piece.KING)

        self.black_pieces = np.bitwise_or.reduce([black_pawn, black_knight, black_bishop, black_rook, black_queen, black_king])

        self.all_pieces = self.get_all_pieces()

        for i in range(len(moves)):
            square_moves = []
            if self.player_turn == Piece.WHITE:
                if (white_pawn >> np.uint64(i)) % 2 == 1:
                    square_moves = self.get_pawn_legal(Piece.WHITE, i)
                elif (white_knight >> np.uint64(i)) % 2 == 1:
                    square_moves = self.get_knight_legal(Piece.WHITE, i)
                elif (white_bishop >> np.uint64(i)) % 2 == 1:
                    avoid_directions = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]
                    square_moves = self.get_sliding_legal(Piece.WHITE, i, Piece.BISHOP, avoid_directions)
                elif (white_rook >> np.uint64(i)) % 2 == 1:
                    avoid_directions = [Direction.NORTH_EAST, Direction.NORTH_WEST, Direction.SOUTH_EAST, Direction.SOUTH_WEST]
                    square_moves = self.get_sliding_legal(Piece.WHITE, i, Piece.ROOK, avoid_directions)
                elif (white_queen >> np.uint64(i)) % 2 == 1:
                    square_moves = self.get_sliding_legal(Piece.WHITE, i, Piece.QUEEN, [])

            else:
                if (black_pawn >> np.uint64(i)) % 2 == 1:
                    square_moves = self.get_pawn_legal(Piece.BLACK, i)
                elif (black_knight >> np.uint64(i)) % 2 == 1:
                    square_moves = self.get_knight_legal(Piece.BLACK, i)
                elif (black_bishop >> np.uint64(i)) % 2 == 1:
                    avoid_directions = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]
                    square_moves = self.get_sliding_legal(Piece.BLACK, i, Piece.BISHOP, avoid_directions)
                elif (black_rook >> np.uint64(i)) % 2 == 1:
                    avoid_directions = [Direction.NORTH_EAST, Direction.NORTH_WEST, Direction.SOUTH_EAST, Direction.SOUTH_WEST]
                    square_moves = self.get_sliding_legal(Piece.BLACK, i, Piece.ROOK, avoid_directions)
                elif (black_queen >> np.uint64(i)) % 2 == 1:
                    square_moves = self.get_sliding_legal(Piece.BLACK, i, Piece.QUEEN, [])

            moves[i] = square_moves
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

        ## Check for push moves ##
        blocker_mask = np.bitwise_and(self.pawn_pushes[square_from][color], opp_pieces)
        push_moves = np.bitwise_xor(blocker_mask, self.pawn_pushes[square_from][color])
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

    ## Get sliding pieces legal moves from a square ##
    def get_sliding_legal(self, color, square_from, piece_type, avoid_directions = None):
        moves = []
        opp_pieces = None
        opp_color = None
        positive = True

        if color == Piece.WHITE:
            opp_pieces = self.black_pieces
            opp_color = Piece.BLACK
        else:
            opp_pieces = self.white_pieces
            opp_color = Piece.WHITE
        
        ## Skip lines ##
        for direction in Direction:
            if direction in avoid_directions:
                continue
            elif direction > Direction.NORTH_WEST:
                positive = False
            else: 
                positive = True
            
            ## Calculate including blocker ##
            attacks = self.ray_moves[square_from][direction]
            occupy_squares = np.bitwise_or(self.white_pieces, self.black_pieces)
            blockers = np.bitwise_and(attacks, occupy_squares)
            first_blocker = None
            blocker_mask = np.uint64(0)
            if blockers > 0:   
                if positive:
                    first_blocker = self.get_lsb(blockers)
                else: 
                    first_blocker = self.get_msb(blockers)
                blocker_mask = np.uint64(1) << np.uint64(first_blocker)
            
            if first_blocker != None:
                attacks = np.bitwise_xor(self.ray_moves[first_blocker][direction], attacks)

            ## Check for capture moves ##
            capture_moves = np.bitwise_and(attacks, opp_pieces)
            while capture_moves > 0:
                square_to = self.get_lsb(capture_moves)
                captured_piece = self.all_pieces[opp_color][square_to]
                move = Move(color, piece_type, square_from, square_to, opp_color, captured_piece)
                moves.append(move)
                square_to = np.uint64(1) << np.uint64(square_to)
                capture_moves = np.bitwise_xor(capture_moves, square_to)

            ## Remove blocker and check for push moves ##
            push_moves = np.bitwise_xor(attacks, blocker_mask) 
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

        moves[Direction.NORTH] = np.uint64(72340172838076672) << np.uint64(square)

        south = np.uint64(282578800148737) >> np.uint64((7 - piece_rank)*8)
        south = south << np.uint64(piece_file)
        moves[Direction.SOUTH] = south

        moves[Direction.EAST] = np.uint64(2**(7 - piece_file) - 1) << np.uint64(square + 1)
        
        moves[Direction.WEST] = np.uint64(2**(piece_file) - 1) << np.uint64(square - piece_file)

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
    
    def draw_bin(self, number):
        number = "{0:b}".format(number).zfill(64)
        for i in range(8):
            for j in range(8):
                print(number[(i*8 + 7-j)], end="")
            print("")
        print("")

if __name__ == "__main__":
    chess_game = Engine()

    new_move = Move(Piece.WHITE, Piece.PAWN, Square.A2, Square.A4)

    chess_game.move(new_move)

    new_move = Move(Piece.BLACK, Piece.PAWN, Square.B7, Square.B5)

    chess_game.move(new_move)

    current_board = np.binary_repr(chess_game.pawn_pushes[Square.H7][Piece.BLACK], width=64)

    print(chess_game.get_all_pieces())
    
    

