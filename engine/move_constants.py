import enum

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