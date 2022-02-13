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
        self.game_over = False

        self.end_message_key = {1: WHITE_WIN_MSG_IMG, 2: BLACK_WIN_MSG_IMG, 3: STALEMATE_MSG_IMG, 4: DRAW_MSG_IMG, 5: WHITE_IN_CHECK_MSG_IMG, 6: BLACK_IN_CHECK_MSG_IMG}

        self.piece_image_key = {1: WHITE_ROOK_IMG,   -1: BLACK_ROOK_IMG,
                                2: WHITE_KNIGHT_IMG, -2: BLACK_KNIGHT_IMG,
                                3: WHITE_BISHOP_IMG, -3: BLACK_BISHOP_IMG,
                                4: WHITE_QUEEN_IMG,  -4: BLACK_QUEEN_IMG,
                                5: WHITE_KING_IMG,   -5: BLACK_KING_IMG,
                                6: WHITE_PAWN_IMG,   -6: BLACK_PAWN_IMG}

        self.buttons_rect_key = {"reset": pygame.Rect(401, 350, 107, 48), "undo": pygame.Rect(400, 300, 112, 52)}
        self.promotion_piece_rects = [pygame.Rect(420, 100 + i*50, 50, 50) for i in range(4)]

        self.squares_centers_list = [[((48 * j) + 13 + 24, (48 * i) + 3 + 24) for j in range(8)] for i in range(8)]
        self.squares_list = [[pygame.Rect((48 * j) + 13, (48 * i) + 3, 48, 48) for j in range(8)] for i in range(8)]

    def update_screen(self) -> None:
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

    def draw_possible_end_cords(self, start_cord) -> bool:
        all_legal_moves = engine.get_all_legal_moves(start_cord)
        if len(all_legal_moves) > 0:
            for cord in all_legal_moves:
                pygame.draw.circle(self.screen, (255, 0, 0), self.squares_centers_list[cord[0]][cord[1]], 5)
            return True
        return False

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

    def should_end_game(self) -> bool:
        is_over = False
        in_checkmate = engine.is_checkmate()
        if in_checkmate in (1, -1):
            n = 1 if engine.turn == -1 else 2
            self.screen.blit(self.end_message_key[n], (400, 0))
            is_over = True

        elif engine.is_stalemate():
            self.screen.blit(self.end_message_key[3], (400, 0))
            is_over = True
                
        elif engine.is_draw():
            self.screen.blit(self.end_message_key[4], (400, 0))
            is_over = True
        return is_over
        
    def run(self) -> None:
        self.update_screen()
        pygame.display.update()

        while True:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONUP:
                    x, y = event.pos

                    if self.buttons_rect_key["reset"].collidepoint((x, y)):
                        engine.reset()
                        self.update_screen()
                        self.game_over = False
                        pygame.display.update()
                        return None

                    elif self.buttons_rect_key["undo"].collidepoint((x, y)):
                        engine.undo_move()
                        self.update_screen()
                        self.game_over = False
                        pygame.display.update()

                    if self.start_cord == None and self.game_over == False:
                        for i in range(8):
                            for j in range(8):
                                if self.squares_list[i][j].collidepoint((x, y)):
                                    if (engine.board[i][j] > 0 and engine.turn > 0) or (engine.board[i][j] < 0 and engine.turn < 0):
                                        if self.draw_possible_end_cords((i, j)):
                                            self.start_cord = (i, j)
                                            pygame.display.update()
                                    break

                    elif self.start_cord != None and self.game_over == False:
                        for m in range(8):
                            for n in range(8):
                                if self.squares_list[m][n].collidepoint((x, y)):
                                    self.end_cord = (m, n)

                                    if engine.is_promotion_move(self.start_cord, self.end_cord):
                                        engine.make_move(self.start_cord, self.end_cord, self.ask_for_promotion())
                                    else:
                                        engine.make_move(self.start_cord, self.end_cord, None)

                                    self.update_screen()
                                    self.start_cord = None
                                    
                                    if self.should_end_game():
                                        self.game_over = True

                                    pygame.display.update()
                                    break   
           
            pygame.time.wait(30)

if __name__ == "__main__":
    chess = Chess()
    while True:
        chess.run()