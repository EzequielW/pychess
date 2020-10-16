import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" 
import pygame
import math
from engine.chess_logic import Chess, Piece, Square
import engine.minimax as minimax

SIZE = MAX_WIDTH, MAX_HEIGHT = 1024, 576  
FPS = 200

if __name__ == "__main__":
    chess_game = Chess()
    
    pygame.init()
    win = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Chess")

    scale_offset = 12
    scale_image = (MAX_HEIGHT//8 - scale_offset*2, MAX_HEIGHT//8 - scale_offset*2)

    w_pawn_image = pygame.image.load("PNG/1x/w_pawn_1x.png")
    w_pawn_image = pygame.transform.scale(w_pawn_image, scale_image)
    w_knight_image = pygame.image.load("PNG/1x/w_knight_1x.png")
    w_knight_image = pygame.transform.scale(w_knight_image, scale_image)
    w_bishop_image = pygame.image.load("PNG/1x/w_bishop_1x.png")
    w_bishop_image = pygame.transform.scale(w_bishop_image, scale_image)
    w_rook_image = pygame.image.load("PNG/1x/w_rook_1x.png")
    w_rook_image = pygame.transform.scale(w_rook_image, scale_image)
    w_queen_image = pygame.image.load("PNG/1x/w_queen_1x.png")
    w_queen_image = pygame.transform.scale(w_queen_image, scale_image)
    w_king_image = pygame.image.load("PNG/1x/w_king_1x.png")
    w_king_image = pygame.transform.scale(w_king_image, scale_image) 

    b_pawn_image = pygame.image.load("PNG/1x/b_pawn_1x.png")
    b_pawn_image = pygame.transform.scale(b_pawn_image, scale_image) 
    b_knight_image = pygame.image.load("PNG/1x/b_knight_1x.png")
    b_knight_image = pygame.transform.scale(b_knight_image, scale_image)
    b_bishop_image = pygame.image.load("PNG/1x/b_bishop_1x.png")
    b_bishop_image = pygame.transform.scale(b_bishop_image, scale_image)
    b_rook_image = pygame.image.load("PNG/1x/b_rook_1x.png")
    b_rook_image = pygame.transform.scale(b_rook_image, scale_image)
    b_queen_image = pygame.image.load("PNG/1x/b_queen_1x.png")
    b_queen_image = pygame.transform.scale(b_queen_image, scale_image)
    b_king_image = pygame.image.load("PNG/1x/b_king_1x.png")
    b_king_image = pygame.transform.scale(b_king_image, scale_image)

    pieces_images = [[w_pawn_image, w_knight_image, w_bishop_image, w_rook_image, w_queen_image, w_king_image],
                         [b_pawn_image, b_knight_image, b_bishop_image, b_rook_image, b_queen_image, b_king_image]]

    chess_game.load_fen_position("r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1")
    moves = chess_game.get_legal_moves(chess_game.player_turn)
    board = chess_game.current_board
    piece_moves = []
    piece_square = None

    run = True
    while(run):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                square =  63 - 7 + (mouse_pos[0]//(MAX_HEIGHT//8) - 8*(mouse_pos[1]//(MAX_HEIGHT//8))) 
                
                if piece_square != square:
                    if piece_moves:
                        if not chess_game.current_board[square] or chess_game.current_board[square][0] != chess_game.player_turn:
                            for move in piece_moves:
                                if move.square_to == square:
                                    chess_game.move(move)
                                    moves = chess_game.get_legal_moves(chess_game.player_turn)
                                    board = chess_game.current_board
                                    minimax.Minimax.node_number = 0
                                    evaluation = minimax.Minimax.searchABPruning(chess_game, 2)
                                    print("\nEvaluation:", evaluation)
                            piece_moves = []
                            piece_square = None
                        else:
                            piece_moves = []
                            for move in moves:
                                if move.square_from == square:
                                    piece_moves.append(move)
                            piece_square = square
                    elif chess_game.current_board[square]:
                        if chess_game.current_board[square][0] == chess_game.player_turn:
                            piece_moves = []
                            for move in moves:
                                if move.square_from == square:
                                    piece_moves.append(move)
                            piece_square = square
                    
        #Board drawing
        square_color = ((115,0,0))
        for i in range(8):
            for j in range(8):
                square = i*8 + 7 - j
                ## draw squares ##
                pos_x = (MAX_HEIGHT//8) * ((63 - square) % 8)
                pos_y = (MAX_HEIGHT//8) * math.floor((square)/8)
    
                if (square // 8 % 2) == 0:
                    if square % 2 == 0:
                        square_color = ((222,184,135))
                    else:
                        square_color = ((255,235,205)) 
                else:
                    if square % 2 == 0:
                        square_color = ((255,235,205)) 
                    else:
                        square_color = ((222,184,135))
                
                if (63 - square) == piece_square:
                    square_color = ((0,225,120))
                    
                pygame.draw.rect(win,square_color,(pos_x, pos_y, MAX_HEIGHT//8, MAX_HEIGHT//8))

                ## draw pieces ##
                piece_x = pos_x + scale_offset
                piece_y = pos_y + scale_offset

                if board[63 - square] != None:
                    win.blit(pieces_images[board[63 - square][0]][board[63 - square][1]-2], (piece_x, piece_y))   

        if piece_moves:
            for move in piece_moves:
                radius = 4
                if move.castle == True:
                    radius = 3
                pos_x = (MAX_HEIGHT//8) * ((move.square_to % 8))
                pos_y = (MAX_HEIGHT//8) * math.floor((63 - move.square_to)/8)
                pos_x = (pos_x + MAX_HEIGHT//16)
                pos_y = (pos_y + MAX_HEIGHT//16)
                pygame.draw.circle(win, (0,255,120), (pos_x, pos_y), (MAX_HEIGHT//8 - scale_offset*radius)//2)

        pygame.display.update()

    pygame.quit()