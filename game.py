import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" 
import pygame
import math
import chess

SIZE = MAX_WIDTH, MAX_HEIGHT = 576, 576 
FPS = 200

## White pieces ##

if __name__ == "__main__":
    chess_game = chess.Chess()
    
    pygame.init()
    win = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Chess")

    scale_offset = 12
    scale_image = (MAX_WIDTH//8 - scale_offset*2, MAX_HEIGHT//8 - scale_offset*2)

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

    moves = chess_game.get_legal_moves()
    piece_moves = None
    piece_square = None

    run = True
    while(run):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                square = mouse_pos[0]//(MAX_WIDTH//8) + 8*(mouse_pos[1]//(MAX_HEIGHT//8))
                piece = chess_game.board[square]
                if piece != None:
                    if piece.piece_color == chess_game.player_turn:
                        piece_moves = moves[piece]
                        piece_square = square
                if piece_moves != None:
                    if square in piece_moves:
                        chess_game.move(piece_square, square)
                        piece_moves = None
                        piece_square = None
                        moves = chess_game.get_legal_moves()
                    

        square_color = ((115,0,0))
        for i in range(64):
            ## draw squares ##
            pos_x = (MAX_WIDTH//8) * (i % 8)
            pos_y = (MAX_HEIGHT//8) * math.floor(i/8)
  
            if (i // 8 % 2) == 0:
                if i % 2 == 0:
                    square_color = ((255,235,205)) 
                else:
                    square_color = ((222,184,135))
            else:
                if i % 2 == 0:
                    square_color = ((222,184,135))
                else:
                    square_color = ((255,235,205))
                
            pygame.draw.rect(win,square_color,(pos_x, pos_y, MAX_HEIGHT//8, MAX_HEIGHT//8))

            ## draw pieces ##
            piece_x = pos_x + scale_offset
            piece_y = pos_y + scale_offset

            if chess_game.board[i] != None:
                if chess_game.board[i].piece_color == chess.PlayerColor.WHITE:
                    if chess_game.board[i].piece_type == chess.PieceType.PAWN:
                        win.blit(w_pawn_image, (piece_x, piece_y))
                    elif chess_game.board[i].piece_type == chess.PieceType.KNIGHT:
                        win.blit(w_knight_image, (piece_x, piece_y))
                    elif chess_game.board[i].piece_type == chess.PieceType.BISHOP:
                        win.blit(w_bishop_image, (piece_x, piece_y))
                    elif chess_game.board[i].piece_type == chess.PieceType.ROOK:
                        win.blit(w_rook_image, (piece_x, piece_y))
                    elif chess_game.board[i].piece_type == chess.PieceType.QUEEN:
                        win.blit(w_queen_image, (piece_x, piece_y))
                    else:
                        win.blit(w_king_image, (piece_x, piece_y))
                else:
                    if chess_game.board[i].piece_type == chess.PieceType.PAWN:
                        win.blit(b_pawn_image, (piece_x, piece_y))
                    elif chess_game.board[i].piece_type == chess.PieceType.KNIGHT:
                        win.blit(b_knight_image, (piece_x, piece_y))
                    elif chess_game.board[i].piece_type == chess.PieceType.BISHOP:
                        win.blit(b_bishop_image, (piece_x, piece_y))
                    elif chess_game.board[i].piece_type == chess.PieceType.ROOK:
                        win.blit(b_rook_image, (piece_x, piece_y))
                    elif chess_game.board[i].piece_type == chess.PieceType.QUEEN:
                        win.blit(b_queen_image, (piece_x, piece_y))
                    else:
                        win.blit(b_king_image, (piece_x, piece_y))    

        if piece_moves != None:
            for move in piece_moves:
                pos_x = (MAX_WIDTH//8) * (move % 8)
                pos_y = (MAX_HEIGHT//8) * math.floor(move/8)
                pos_x = (pos_x + MAX_HEIGHT//16)
                pos_y = (pos_y + MAX_HEIGHT//16)
                pygame.draw.circle(win, (0,255,0), (pos_x, pos_y), (MAX_HEIGHT//8 - scale_offset*2)//2)

        pygame.display.update()

    pygame.quit()