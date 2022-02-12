import pygame
import sys
from engine import Engine

engine = Engine()

BACKGROUND_IMG = pygame.image.load('assets/chess_board.png')
BLACK_QUEEN_IMG = pygame.image.load('assets/black_queen.png')
BLACK_KING_IMG = pygame.image.load('assets/black_king.png')
BLACK_PAWN_IMG = pygame.image.load('assets/black_pawn.png')
BLACK_ROOK_IMG = pygame.image.load('assets/black_rook.png')
BLACK_KNIGHT_IMG = pygame.image.load('assets/black_knight.png')
BLACK_BISHOP_IMG = pygame.image.load('assets/black_bishop.png')
WHITE_QUEEN_IMG = pygame.image.load('assets/white_queen.png')
WHITE_KING_IMG = pygame.image.load('assets/white_king.png')
WHITE_PAWN_IMG = pygame.image.load('assets/white_pawn.png')
WHITE_ROOK_IMG = pygame.image.load('assets/white_rook.png')
WHITE_KNIGHT_IMG = pygame.image.load('assets/white_knight.png')
WHITE_BISHOP_IMG = pygame.image.load('assets/white_bishop.png')
RESET_BTN_IMG = pygame.image.load('assets/reset.png')
UNDO_BTN_IMG = pygame.image.load('assets/undo.png')
NEW_GAME_BTN_IMG = pygame.image.load('assets/new_game.png')
WHITE_WIN_MSG_IMG = pygame.image.load('assets/white_win.png')
BLACK_WIN_MSG_IMG = pygame.image.load('assets/black_win.png')
STALEMATE_MSG_IMG = pygame.image.load('assets/stalemate.png')
DRAW_MSG_IMG = pygame.image.load('assets/draw.png')
WHITE_IN_CHECK_MSG_IMG = pygame.image.load('assets/white_in_check.png')
BLACK_IN_CHECK_MSG_IMG = pygame.image.load('assets/black_in_check.png')

# All values are hard-coded

class Chess(): 
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((510, 400))
        pygame.display.set_caption("Chess")

        self.start_cord = None
        self.end_cord = None
        self.promotion_piece = None  

        self.end_message_key = {1: WHITE_WIN_MSG_IMG, 2: BLACK_WIN_MSG_IMG, 3: STALEMATE_MSG_IMG, 4: DRAW_MSG_IMG, 5: WHITE_IN_CHECK_MSG_IMG, 6: BLACK_IN_CHECK_MSG_IMG}

        self.piece_image_key = {1: WHITE_ROOK_IMG, -1: BLACK_ROOK_IMG,
                                2: WHITE_KNIGHT_IMG, -2: BLACK_KNIGHT_IMG,
                                3: WHITE_BISHOP_IMG, -3: BLACK_BISHOP_IMG,
                                4: WHITE_QUEEN_IMG, -4: BLACK_QUEEN_IMG,
                                5: WHITE_KING_IMG, -5: BLACK_KING_IMG,
                                6: WHITE_PAWN_IMG, -6: BLACK_PAWN_IMG}

        self.buttons_rect_key = {"reset": pygame.Rect(401, 350, 107, 48), "undo": pygame.Rect(400, 300, 112, 52), "new_game": pygame.Rect(400, 52, 108, 54)}
        self.promotion_piece_rects = [pygame.Rect(420, 100 + i*50, 50, 50) for i in range(4)]

        self.squares_centers_list = [[((48 * j) + 13 + 24, (48 * i) + 3 + 24) for j in range(8)] for i in range(8)]
        self.squares_list = [[pygame.Rect((48 * j) + 13, (48 * i) + 3, 48, 48) for j in range(8)] for i in range(8)]

    def update_board(self) -> None:
        self.screen.fill("white")
        self.screen.blit(BACKGROUND_IMG, (0, 0))
        self.screen.blit(RESET_BTN_IMG, (401, 350))
        self.screen.blit(UNDO_BTN_IMG, (400, 300))

        for i in range(8):
            for j in range(8):
                if engine.board[i][j] != 0:
                    self.screen.blit(self.piece_image_key[engine.board[i][j]], self.squares_list[i][j])

        if engine.in_check(engine.turn):
            end_message_index = 5 if engine.turn == 1 else 6
            self.screen.blit(self.end_message_key[end_message_index], (400, 0))

    def show_possible_end_cords(self, start_cord) -> bool:
        all_legal_moves = engine.get_all_legal_moves(start_cord)
        if len(all_legal_moves) > 0:
            for cord in all_legal_moves:
                pygame.draw.circle(self.screen, (255, 0, 0), self.squares_centers_list[cord[0]][cord[1]], 5)
            pygame.display.update()
            return True
        return False

    def ask_for_restart(self) -> bool:
        self.screen.blit(NEW_GAME_BTN_IMG, (400, 52))
        pygame.display.update()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONUP:
                    x, y = event.pos

                    if self.buttons_rect_key["reset"].collidepoint((x, y)) or self.buttons_rect_key["new_game"].collidepoint((x, y)):
                        return True

                    elif self.buttons_rect_key["undo"].collidepoint((x, y)):
                        engine.undo_move()
                        self.update_board()
                        pygame.display.update()
                        return False

            pygame.time.wait(30)

    def ask_for_promotion(self) -> int:
        for i in range(4):
            self.screen.blit(self.piece_image_key[engine.turn * (i + 1)], (420, 100 + i*50))
                
        pygame.display.update()
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONUP:
                    for i in range(4):
                        if self.promotion_piece_rects[i].collidepoint(event.pos):
                            return engine.turn * (i + 1)
  
            pygame.time.wait(30)
        
    def run(self):
        self.update_board()
        pygame.display.update()

        while True:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONUP:
                    x, y = event.pos

                    if self.start_cord == None:
                        if self.buttons_rect_key["reset"].collidepoint((x, y)):
                            engine.reset()
                            self.update_board()

                        elif self.buttons_rect_key["undo"].collidepoint((x, y)):
                            engine.undo_move()
                            self.update_board()

                        else:
                            for i in range(8):
                                for j in range(8):
                                    if self.squares_list[i][j].collidepoint((x, y)):
                                        if (engine.board[i][j] > 0 and engine.turn > 0) or (engine.board[i][j] < 0 and engine.turn < 0):
                                            if self.show_possible_end_cords((i, j)):
                                                self.start_cord = (i, j)
                                        break

                        pygame.display.update()

                    elif self.start_cord is not None:
                        x, y = event.pos  
                        for m in range(8):
                            for n in range(8):
                                if self.squares_list[m][n].collidepoint((x, y)):
                                    self.end_cord = (m, n)

                                    if engine.is_promotion_move(self.start_cord, self.end_cord):
                                        self.promotion_piece = self.ask_for_promotion()

                                    engine.make_move(self.start_cord, self.end_cord, self.promotion_piece)

                                    self.start_cord = None
                                    self.promotion_piece = None
                                    
                                    is_over = False
                                    winner = engine.is_checkmate()
                                    if winner in (1, -1):
                                        n = 1 if engine.turn == -1 else 2
                                        self.screen.blit(self.end_message_key[n], (400, 0))
                                        is_over = True
                        
                                    elif engine.is_stalemate():
                                        self.screen.blit(self.end_message_key[3], (400, 0))
                                        is_over = True
                                            
                                    elif engine.is_draw():
                                        self.screen.blit(self.end_message_key[4], (400, 0))
                                        is_over = True

                                    self.update_board()
                                    pygame.display.update()
                                    
                                    if is_over and self.ask_for_restart():
                                        engine.reset()

                                    self.update_board()
                                    pygame.display.update()

                                    break   
           
            pygame.time.wait(30)

if __name__ == "__main__":
    chess = Chess()
    chess.run()