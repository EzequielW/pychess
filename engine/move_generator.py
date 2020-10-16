import os
import numpy as np
import pickle
from engine.move_constants import Move, Piece, Square, Direction

class MoveGenerator():
    def __init__(self):
        self.knight_moves = [None]*64
        self.ray_moves = [None]*64
        self.bishop_masks = [None]*64
        self.rook_masks = [None]*64
        self.king_moves = [None]*64
        self.pawn_attacks = [None]*64
        self.pawn_pushes = [None]*64
        self.bishop_moveboard = [None]*64
        self.rook_moveboard = [None]*64
        self.bishop_xrays = [None]*64
        self.rook_xrays = [None]*64

        # Load previously created rook and bishop blockerboard to moveboard dictionaries
        if os.path.isfile("sliding_pieces_dict.json"):
            print("---- loading piece movement ----")
            with (open('sliding_pieces_dict.json', 'rb')) as openfile:
                sliding_pieces_dict = pickle.load(openfile)
                self.rook_moveboard = sliding_pieces_dict['rook_moveboard']
                self.bishop_moveboard = sliding_pieces_dict['bishop_moveboard']
                self.rook_xrays = sliding_pieces_dict['rook_xrays']
                self.bishop_xrays = sliding_pieces_dict['bishop_xrays']

        # Initialize moves for each piece ##
        for i in range(64):
            self.knight_moves[i] = self.get_knight_moves(i)
            self.ray_moves[i] = self.get_ray_moves(i)
            self.rook_masks[i] = self.get_rook_mask(i)
            self.bishop_masks[i] = self.get_bishop_mask(i)
            self.king_moves[i] = self.get_king_moves(i)
            self.pawn_attacks[i] = self.get_pawn_attacks(i)
            self.pawn_pushes[i] = self.get_pawn_pushes(i)

        # Create dictionaries for rook and bishop if file doesnt exist
        if not os.path.isfile("sliding_pieces_dict.json"):
            print("---- dumping piece movement ----")
            for i in range(64):
                self.rook_moveboard[i] = self.get_rook_attacks(i)
                self.bishop_moveboard[i] = self.get_bishop_attacks(i)
            print("---- moveboard dictionary loaded ----")
            # Xray moves need moveboards to be loaded first
            for i in range(64):
                self.rook_xrays[i] = self.get_rook_xrays(i)
                self.bishop_xrays[i] = self.get_bishop_xrays(i)
            print("---- xray attacks loaded ----")

            sliding_pieces_dict = {}
            sliding_pieces_dict['rook_moveboard'] = self.rook_moveboard
            sliding_pieces_dict['bishop_moveboard'] = self.bishop_moveboard
            sliding_pieces_dict['rook_xrays'] = self.rook_xrays
            sliding_pieces_dict['bishop_xrays'] = self.bishop_xrays

            with open('sliding_pieces_dict.json', 'wb') as outfile:
                pickle.dump(sliding_pieces_dict, outfile)

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
    
    #Fill sliding pieces moves (bishop, rook and queen)
    def get_ray_moves(self, square):
        moves = [None]*8
        piece_rank = square//8
        piece_file = square%8

        #Generate lines
        north = np.uint64(72340172838076672) << np.uint64(square)
        moves[Direction.NORTH] = north

        south = np.uint64(282578800148737) >> np.uint64((7 - piece_rank)*8)
        south = south << np.uint64(piece_file)
        moves[Direction.SOUTH] = south

        east = np.uint64(2**(7 - piece_file) - 1) << np.uint64(square + 1)
        moves[Direction.EAST] = east
        
        west = np.uint64(2**(piece_file) - 1) << np.uint64(square - piece_file)
        moves[Direction.WEST] = west

        #Generate diagonals
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

    # Get bishop xray attacks(the attacks behind the first blockers)
    def get_bishop_xrays(self, square):
        blockermask = self.bishop_masks[square]
        bits = bin(blockermask).count("1")

        blockerboard_to_moveboard = {}

        for j in range((1<<bits)):
            blockerboard = self.gen_blockerboard(j, blockermask)
            blockers = np.bitwise_and(blockerboard, self.bishop_moveboard[square][blockerboard])
            xray_moves = np.uint64(0)

            while blockers > 0:
                blocker_square = self.get_lsb(blockers)
                new_blockerboard = np.bitwise_and(self.bishop_masks[blocker_square], blockerboard)
                new_ray = np.bitwise_and(self.bishop_moveboard[square][0], np.bitwise_not(self.bishop_moveboard[square][blockerboard]))
                new_ray = np.bitwise_and(self.bishop_moveboard[blocker_square][new_blockerboard], new_ray)
                xray_moves = np.bitwise_or(xray_moves, new_ray)
                blocker_square = np.uint64(1) << np.uint64(blocker_square)
                blockers = np.bitwise_xor(blocker_square, blockers)

            blockerboard_to_moveboard[blockerboard] = xray_moves

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

    # Get rook xray attacks(the attacks behind the first blockers)
    def get_rook_xrays(self, square):
        blockermask = self.rook_masks[square]
        bits = bin(blockermask).count("1")

        blockerboard_to_moveboard = {}

        for j in range((1<<bits)):
            blockerboard = self.gen_blockerboard(j, blockermask)
            blockers = np.bitwise_and(blockerboard, self.rook_moveboard[square][blockerboard])
            xray_moves = np.uint64(0)

            while blockers > 0:
                blocker_square = self.get_lsb(blockers)
                new_blockerboard = np.bitwise_and(self.rook_masks[blocker_square], blockerboard)
                new_ray = np.bitwise_and(self.rook_moveboard[square][0], np.bitwise_not(self.rook_moveboard[square][blockerboard]))
                new_ray = np.bitwise_and(self.rook_moveboard[blocker_square][new_blockerboard], new_ray)
                xray_moves = np.bitwise_or(xray_moves, new_ray)
                blocker_square = np.uint64(1) << np.uint64(blocker_square)
                blockers = np.bitwise_xor(blocker_square, blockers)

            blockerboard_to_moveboard[blockerboard] = xray_moves

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

        