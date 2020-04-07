import enum

class PlayerColor(enum.Enum):
    WHITE = 0
    BLACK = 1

class PieceType(enum.Enum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

class Square(enum.IntEnum):
    (A1, A2, A3, A4, A5, A6, A7, A8,
    B1, B2, B3, B4, B5, B6, B7, B8,
    C1, C2, C3, C4, C5, C6, C7, C8,
    D1, D2, D3, D4, D5, D6, D7, D8,
    E1, E2, E3, E4, E5, E6, E7, E8,
    F1, F2, F3, F4, F5, F6, F7, F8,
    G1, G2, G3, G4, G5, G6, G7, G8,
    H1, H2, H3, H4, H5, H6, H7, H8) = range(64)

class Piece():
    def __init__(self, piece_type, piece_color):
        self.piece_type = piece_type
        self.piece_color = piece_color

class Chess():
    def __init__(self):
        self.board = [None]*64
        self.player_turn = PlayerColor.WHITE
        
        ## Initial state of the board ##

        self.board[Square.A1] = Piece(PieceType.ROOK, PlayerColor.WHITE)
        self.board[Square.A2] = Piece(PieceType.KNIGHT, PlayerColor.WHITE)
        self.board[Square.A3] = Piece(PieceType.BISHOP, PlayerColor.WHITE)
        self.board[Square.A4] = Piece(PieceType.KING, PlayerColor.WHITE)
        self.board[Square.A5] = Piece(PieceType.QUEEN, PlayerColor.WHITE)
        self.board[Square.A6] = Piece(PieceType.BISHOP, PlayerColor.WHITE)
        self.board[Square.A7] = Piece(PieceType.KNIGHT, PlayerColor.WHITE)
        self.board[Square.A8] = Piece(PieceType.ROOK, PlayerColor.WHITE)
        self.board[Square.B1] = Piece(PieceType.PAWN, PlayerColor.WHITE)
        self.board[Square.B2] = Piece(PieceType.PAWN, PlayerColor.WHITE)
        self.board[Square.B3] = Piece(PieceType.PAWN, PlayerColor.WHITE)
        self.board[Square.B4] = Piece(PieceType.PAWN, PlayerColor.WHITE)
        self.board[Square.B5] = Piece(PieceType.PAWN, PlayerColor.WHITE)
        self.board[Square.B6] = Piece(PieceType.PAWN, PlayerColor.WHITE)
        self.board[Square.B7] = Piece(PieceType.PAWN, PlayerColor.WHITE)
        self.board[Square.B8] = Piece(PieceType.PAWN, PlayerColor.WHITE)

        self.board[Square.H1] = Piece(PieceType.ROOK, PlayerColor.BLACK)
        self.board[Square.H2] = Piece(PieceType.KNIGHT, PlayerColor.BLACK)
        self.board[Square.H3] = Piece(PieceType.BISHOP, PlayerColor.BLACK)
        self.board[Square.H4] = Piece(PieceType.KING, PlayerColor.BLACK)
        self.board[Square.H5] = Piece(PieceType.QUEEN, PlayerColor.BLACK)
        self.board[Square.H6] = Piece(PieceType.BISHOP, PlayerColor.BLACK)
        self.board[Square.H7] = Piece(PieceType.KNIGHT, PlayerColor.BLACK)
        self.board[Square.H8] = Piece(PieceType.ROOK, PlayerColor.BLACK)
        self.board[Square.G1] = Piece(PieceType.PAWN, PlayerColor.BLACK)
        self.board[Square.G2] = Piece(PieceType.PAWN, PlayerColor.BLACK)
        self.board[Square.G3] = Piece(PieceType.PAWN, PlayerColor.BLACK)
        self.board[Square.G4] = Piece(PieceType.PAWN, PlayerColor.BLACK)
        self.board[Square.G5] = Piece(PieceType.PAWN, PlayerColor.BLACK)
        self.board[Square.G6] = Piece(PieceType.PAWN, PlayerColor.BLACK)
        self.board[Square.G7] = Piece(PieceType.PAWN, PlayerColor.BLACK)
        self.board[Square.G8] = Piece(PieceType.PAWN, PlayerColor.BLACK)

    def move(self, square_from, square_to):
        self.board[square_to] = self.board[square_from]
        self.board[square_from] = None
        
        if self.player_turn == PlayerColor.WHITE:
            self.player_turn = PlayerColor.BLACK
        else:
            self.player_turn = PlayerColor.WHITE

    ## Returns all the legal moves on the current board given the players_turn ##
    def get_legal_moves(self):
        moves = {}

        for i in range(len(self.board)):
            if self.board[i] != None:
                if self.board[i].piece_color == self.player_turn:
                    if self.board[i].piece_type == PieceType.PAWN:
                        moves[self.board[i]] = self.get_pawn_moves(i)
                    elif self.board[i].piece_type == PieceType.KNIGHT:
                        moves[self.board[i]] = self.get_knight_moves(i)
                    elif self.board[i].piece_type == PieceType.BISHOP:
                        moves[self.board[i]] = self.get_bishop_moves(i)
                    elif self.board[i].piece_type == PieceType.ROOK:
                        moves[self.board[i]] = self.get_rook_moves(i)
                    elif self.board[i].piece_type == PieceType.QUEEN:
                        moves[self.board[i]] = self.get_queen_moves(i)
                    else: 
                        moves[self.board[i]] = self.get_king_moves(i)

        return moves

    def get_pawn_moves(self, square):
        moves = []

        if self.player_turn == PlayerColor.WHITE:
            ## check if pawn can capture ##
            if square % 8 != 0 and self.board[square + 7] != None:
                if self.board[square + 7].piece_color != self.player_turn:
                    moves.append(square + 7)
            if (square + 1) % 8 != 0 and self.board[square + 9] != None:
                if self.board[square + 9].piece_color != self.player_turn:
                    moves.append(square + 9)
            ## check if pawn can advance ##
            if self.board[square + 8] == None:
                moves.append(square + 8)
                if self.board[square + 16] == None and square < Square.C1:
                    moves.append(square + 16)
        else:
            ## check if pawn can capture ##
            if square % 8 != 0 and self.board[square - 9] != None:
                if self.board[square - 9].piece_color != self.player_turn:
                    moves.append(square - 9)
            if (square + 1) % 8 != 0 and self.board[square - 7] != None:
                if self.board[square - 7].piece_color != self.player_turn:
                    moves.append(square - 7)
            ## check if pawn can advance ##
            if self.board[square - 8] == None:
                moves.append(square - 8)
                if self.board[square - 16] == None and square > Square.F8:
                    moves.append(square - 16)
        
        return moves

    def get_knight_moves(self, square):
        moves = []

        if square % 8 != 0:
            if square < Square.G1:
                if self.board[square + 15] != None:
                    if self.board[square + 15].piece_color != self.player_turn:
                        moves.append(square + 15)
                else:
                    moves.append(square + 15)
            if square > Square.B8:
                if self.board[square - 17] != None:
                    if self.board[square - 17].piece_color != self.player_turn:
                        moves.append(square - 17)
                else:
                    moves.append(square - 17)
            if (square - 1) % 8 != 0:
                if square > Square.A8:
                    if self.board[square - 10] != None:
                        if self.board[square - 10].piece_color != self.player_turn:
                            moves.append(square - 10)
                    else:
                        moves.append(square - 10)
                if square < Square.H1:
                    if self.board[square + 6] != None:
                        if self.board[square + 6].piece_color != self.player_turn:
                            moves.append(square + 6)
                    else:
                        moves.append(square + 6)
        
        if (square + 1) % 8 != 0:
            if square < Square.G1:
                if self.board[square + 17] != None:
                    if self.board[square + 17].piece_color != self.player_turn:
                        moves.append(square + 17)
                else:
                    moves.append(square + 17)
            if square > Square.B8:
                if self.board[square - 15] != None:
                    if self.board[square - 15].piece_color != self.player_turn:
                        moves.append(square - 15)
                else:
                    moves.append(square - 15)
            if (square + 2) % 8 != 0:
                if square < Square.H1:
                    if self.board[square + 10] != None:
                        if self.board[square + 10].piece_color != self.player_turn:
                            moves.append(square + 10)
                    else:
                        moves.append(square + 10)
                if square > Square.A8:
                    if self.board[square - 6] != None:
                        if self.board[square - 6].piece_color != self.player_turn:
                            moves.append(square - 6)
                    else:
                        moves.append(square - 6)

        return moves
    
    def get_bishop_moves(self, square):
        moves = []
        
        next_move = square - 7
        while next_move >= 0 and next_move % 8 != 0:
            if self.board[next_move] != None:
                if self.board[next_move].piece_color != self.player_turn:
                    moves.append(next_move)
                break
            moves.append(next_move)
            next_move -= 7

        next_move = square - 9
        while next_move >= 0 and (next_move + 9) % 8 != 0:
            if self.board[next_move] != None:
                if self.board[next_move].piece_color != self.player_turn:
                    moves.append(next_move)
                break
            moves.append(next_move)
            next_move -= 9

        next_move = square + 7
        while next_move < 64 and (next_move - 7) % 8 != 0:
            if self.board[next_move] != None:
                if self.board[next_move].piece_color != self.player_turn:
                    moves.append(next_move)
                break
            moves.append(next_move)
            next_move += 7

        next_move = square + 9
        while next_move < 64 and next_move % 8 != 0:
            if self.board[next_move] != None:
                if self.board[next_move].piece_color != self.player_turn:
                    moves.append(next_move)
                break
            moves.append(next_move)
            next_move += 9

        return moves
    
    def get_rook_moves(self, square):
        moves = []

        next_move = square - 1
        while (next_move + 1) % 8 != 0:
            if self.board[next_move] != None:
                if self.board[next_move].piece_color != self.player_turn:
                    moves.append(next_move)
                break
            moves.append(next_move)
            next_move -= 1
        
        next_move = square + 1
        while next_move % 8 != 0:
            if self.board[next_move] != None:
                if self.board[next_move].piece_color != self.player_turn:
                    moves.append(next_move)
                break
            moves.append(next_move)
            next_move += 1
        
        next_move = square - 8
        while next_move >= 0:
            if self.board[next_move] != None:
                if self.board[next_move].piece_color != self.player_turn:
                    moves.append(next_move)
                break
            moves.append(next_move)
            next_move -= 8

        next_move = square + 8
        while next_move < 64:
            if self.board[next_move] != None:
                if self.board[next_move].piece_color != self.player_turn:
                    moves.append(next_move)
                break
            moves.append(next_move)
            next_move += 8

        return moves
    
    def get_queen_moves(self, square):
        straight = self.get_rook_moves(square)
        diagonal = self.get_bishop_moves(square)
        moves = straight + diagonal

        return moves

    def get_king_moves(self, square):
        moves = []

        ## straights ##
        if square % 8 != 0:
            if self.board[square - 1] != None:
                if self.board[square - 1].piece_color != self.player_turn:
                    moves.append(square - 1)
            else:
                moves.append(square - 1)
            ## diagonals ##
            if square > Square.A8:
                if self.board[square - 9] != None:
                    if self.board[square - 9].piece_color != self.player_turn:
                        moves.append(square - 9)
                else:
                    moves.append(square - 9)
            if square < Square.H1:
                if self.board[square + 7] != None:
                    if self.board[square + 7].piece_color != self.player_turn:
                        moves.append(square + 7)
                else:
                    moves.append(square + 7)

        if (square + 1) % 8 != 0:
            if self.board[square + 1] != None:
                if self.board[square + 1].piece_color != self.player_turn:
                    moves.append(square + 1)
            else:
                moves.append(square + 1)
            ## diagonals ##
            if square > Square.A8:
                if self.board[square - 7] != None:
                    if self.board[square - 7].piece_color != self.player_turn:
                        moves.append(square - 7)
                else:
                    moves.append(square - 7)
            if square < Square.H1:
                if self.board[square + 9] != None:
                    if self.board[square + 9].piece_color != self.player_turn:
                        moves.append(square + 9)
                else:
                    moves.append(square + 9)

        if square > Square.A8:
            if self.board[square - 8] != None:
                if self.board[square - 8].piece_color != self.player_turn:
                    moves.append(square - 8)
            else:
                moves.append(square - 8)
        if square < Square.H1:
            if self.board[square + 8] != None:
                if self.board[square + 8].piece_color != self.player_turn:
                    moves.append(square + 8)
            else:
                moves.append(square + 8)

        return moves

            