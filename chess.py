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
    (A8, B8, C8, D8, E8, F8, G8, H8,
    A7, B7, C7, D7, E7, F7, G7, H7,
    A6, B6, C6, D6, E6, F6, G6, H6,
    A5, B5, C5, D5, E5, F5, G5, H5,
    A4, B4, C4, D4, E4, F4, G4, H4,
    A3, B3, C3, D3, E3, F3, G3, H3,
    A2, B2, C2, D2, E2, F2, G2, H2,
    A1, B1, C1, D1, E1, F1, G1, H1) = range(64)

class Piece():
    def __init__(self, piece_type, piece_color):
        self.piece_type = piece_type
        self.piece_color = piece_color

class Chess():
    def __init__(self):
        self.board = [None]*64
        self.player_turn = PlayerColor.WHITE
        self.castleA1 = True
        self.castleH1 = True
        self.castleA8 = True
        self.castleH8 = True
        ## Initial state of the board ##

        self.board[Square.A1] = Piece(PieceType.ROOK, PlayerColor.WHITE)
        self.board[Square.B1] = Piece(PieceType.KNIGHT, PlayerColor.WHITE)
        self.board[Square.C1] = Piece(PieceType.BISHOP, PlayerColor.WHITE)
        self.board[Square.D1] = Piece(PieceType.QUEEN, PlayerColor.WHITE)
        self.board[Square.E1] = Piece(PieceType.KING, PlayerColor.WHITE)
        self.board[Square.F1] = Piece(PieceType.BISHOP, PlayerColor.WHITE)
        self.board[Square.G1] = Piece(PieceType.KNIGHT, PlayerColor.WHITE)
        self.board[Square.H1] = Piece(PieceType.ROOK, PlayerColor.WHITE)
        self.board[Square.A2] = Piece(PieceType.PAWN, PlayerColor.WHITE)
        self.board[Square.B2] = Piece(PieceType.PAWN, PlayerColor.WHITE)
        self.board[Square.C2] = Piece(PieceType.PAWN, PlayerColor.WHITE)
        self.board[Square.D2] = Piece(PieceType.PAWN, PlayerColor.WHITE)
        self.board[Square.E2] = Piece(PieceType.PAWN, PlayerColor.WHITE)
        self.board[Square.F2] = Piece(PieceType.PAWN, PlayerColor.WHITE)
        self.board[Square.G2] = Piece(PieceType.PAWN, PlayerColor.WHITE)
        self.board[Square.H2] = Piece(PieceType.PAWN, PlayerColor.WHITE)

        self.board[Square.A8] = Piece(PieceType.ROOK, PlayerColor.BLACK)
        self.board[Square.B8] = Piece(PieceType.KNIGHT, PlayerColor.BLACK)
        self.board[Square.C8] = Piece(PieceType.BISHOP, PlayerColor.BLACK)
        self.board[Square.D8] = Piece(PieceType.QUEEN, PlayerColor.BLACK)
        self.board[Square.E8] = Piece(PieceType.KING, PlayerColor.BLACK)
        self.board[Square.F8] = Piece(PieceType.BISHOP, PlayerColor.BLACK)
        self.board[Square.G8] = Piece(PieceType.KNIGHT, PlayerColor.BLACK)
        self.board[Square.H8] = Piece(PieceType.ROOK, PlayerColor.BLACK)
        self.board[Square.A7] = Piece(PieceType.PAWN, PlayerColor.BLACK)
        self.board[Square.B7] = Piece(PieceType.PAWN, PlayerColor.BLACK)
        self.board[Square.C7] = Piece(PieceType.PAWN, PlayerColor.BLACK)
        self.board[Square.D7] = Piece(PieceType.PAWN, PlayerColor.BLACK)
        self.board[Square.E7] = Piece(PieceType.PAWN, PlayerColor.BLACK)
        self.board[Square.F7] = Piece(PieceType.PAWN, PlayerColor.BLACK)
        self.board[Square.G7] = Piece(PieceType.PAWN, PlayerColor.BLACK)
        self.board[Square.H7] = Piece(PieceType.PAWN, PlayerColor.BLACK)

    def move(self, square_from, square_to):
        ## check castling ##
        if self.board[square_from].piece_type == PieceType.KING:
            if self.player_turn == PlayerColor.WHITE:
                if self.castleA1 or self.castleH1:
                    self.castleA1 = False
                    self.castleH1 = False
            else:
                if self.castleA8 or self.castleH8:
                    self.castleA8 = False
                    self.castleH8 = False
        elif self.board[square_from].piece_type == PieceType.ROOK:
            if square_from == Square.A1 and self.castleA1:
                self.castleA1 = False
            elif square_from == Square.H1 and self.castleH1:
                self.castleH1 = False
            elif square_from == Square.A8 and self.castleA8:
                self.castleA8 = False
            elif square_from == Square.H8 and self.castleH8:
                self.castleH8 = False

        ## move and pass turn ##
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
            if square % 8 != 0 and self.board[square - 7] != None:
                if self.board[square - 7].piece_color != self.player_turn:
                    moves.append(square - 7)
            if (square + 1) % 8 != 0 and self.board[square - 9] != None:
                if self.board[square - 9].piece_color != self.player_turn:
                    moves.append(square - 9)
            ## check if pawn can advance ##
            if self.board[square - 8] == None:
                moves.append(square - 8)
                if self.board[square - 16] == None and square > Square.H3:
                    moves.append(square - 16)
        else:
            ## check if pawn can capture ##
            if square % 8 != 0 and self.board[square + 9] != None:
                if self.board[square + 9].piece_color != self.player_turn:
                    moves.append(square + 9)
            if (square + 1) % 8 != 0 and self.board[square + 7] != None:
                if self.board[square + 7].piece_color != self.player_turn:
                    moves.append(square + 7)
            ## check if pawn can advance ##
            if self.board[square + 8] == None:
                moves.append(square + 8)
                if self.board[square + 16] == None and square < Square.A6:
                    moves.append(square + 16)
        
        return moves

    def get_knight_moves(self, square):
        moves = []

        if square % 8 != 0:
            if square < Square.A2:
                if self.board[square + 15] != None:
                    if self.board[square + 15].piece_color != self.player_turn:
                        moves.append(square + 15)
                else:
                    moves.append(square + 15)
            if square > Square.H7:
                if self.board[square - 17] != None:
                    if self.board[square - 17].piece_color != self.player_turn:
                        moves.append(square - 17)
                else:
                    moves.append(square - 17)
            if (square - 1) % 8 != 0:
                if square > Square.H8:
                    if self.board[square - 10] != None:
                        if self.board[square - 10].piece_color != self.player_turn:
                            moves.append(square - 10)
                    else:
                        moves.append(square - 10)
                if square < Square.A1:
                    if self.board[square + 6] != None:
                        if self.board[square + 6].piece_color != self.player_turn:
                            moves.append(square + 6)
                    else:
                        moves.append(square + 6)
        
        if (square + 1) % 8 != 0:
            if square < Square.A2:
                if self.board[square + 17] != None:
                    if self.board[square + 17].piece_color != self.player_turn:
                        moves.append(square + 17)
                else:
                    moves.append(square + 17)
            if square > Square.H7:
                if self.board[square - 15] != None:
                    if self.board[square - 15].piece_color != self.player_turn:
                        moves.append(square - 15)
                else:
                    moves.append(square - 15)
            if (square + 2) % 8 != 0:
                if square < Square.A1:
                    if self.board[square + 10] != None:
                        if self.board[square + 10].piece_color != self.player_turn:
                            moves.append(square + 10)
                    else:
                        moves.append(square + 10)
                if square > Square.H8:
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
            if square > Square.H8:
                if self.board[square - 9] != None:
                    if self.board[square - 9].piece_color != self.player_turn:
                        moves.append(square - 9)
                else:
                    moves.append(square - 9)
            if square < Square.A1:
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
            if square > Square.H8:
                if self.board[square - 7] != None:
                    if self.board[square - 7].piece_color != self.player_turn:
                        moves.append(square - 7)
                else:
                    moves.append(square - 7)
            if square < Square.A1:
                if self.board[square + 9] != None:
                    if self.board[square + 9].piece_color != self.player_turn:
                        moves.append(square + 9)
                else:
                    moves.append(square + 9)

        if square > Square.H8:
            if self.board[square - 8] != None:
                if self.board[square - 8].piece_color != self.player_turn:
                    moves.append(square - 8)
            else:
                moves.append(square - 8)
        if square < Square.A1:
            if self.board[square + 8] != None:
                if self.board[square + 8].piece_color != self.player_turn:
                    moves.append(square + 8)
            else:
                moves.append(square + 8)

        ## check castling ##
        if self.player_turn == PlayerColor.WHITE:
            if self.board[Square.B1] is None and self.board[Square.C1] is None and self.board[Square.D1] is None and self.castleA1:
                moves.append(Square.C1)
            if self.board[Square.F1] is None and self.board[Square.G1] is None and self.castleH1:
                moves.append(Square.G1)
        else:
            if self.board[Square.B8] is None and self.board[Square.C8] is None and self.board[Square.D8] is None and self.castleA8:
                moves.append(Square.C8)
            if self.board[Square.F8] is None and self.board[Square.G8] is None and self.castleH8:
                moves.append(Square.G8)

        return moves

            