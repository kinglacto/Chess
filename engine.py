"""
Author - @kinglacto

This is a base chess engine that takes (a) a board_state, (b) a turn value and also (c) a list of logged moves up until now; as inputs.
If no board state is passed, the base engine assumes the start_state input with white to move and an empty moves_log.

# The word "move" henceforth refers to a "ply".

Functions:
1. It can make moves. The method is instance_name.make_move(start_cord, end_cord , promotion_piece);
where start_cord is the start cord (x, y) and end_cord is the end cord (x, y) and promotion_piece is the promotion piece, 
which you need not always pass in unless the move you are making is a promotion move.

2. It can undo moves. The method is instance_name.undo_move();
which undoes the most recent move.


(a) The board_state is an 8 x 8 list where
{
     1: white rook   
     2: white knight  
     3: white bishop  
     4: white queen  
     5: white king  
     6: white pawn 
    
    -1: black rook   
    -2: black knight  
    -3: black bishop  
    -4: black queen  
    -5: black king  
    -6: black pawn 
    
     0: empty square
}

(b) for var turn:
 1: white's turn
-1: black's turn

(c) for list moves:
[(p1,s1,o1,e1,add_on1), (p2,s2,o2,e2,add_on2) ... (pN,sN,oN,eN,add_onN)] where N is the number of plies (literally) or N/2 is the number of moves (literally) played.
where {
    p is the piece that was moved 
    s is the cord from which it was moved [a tuple of the form (x, y)]
    o is the piece that was captured [0 if moved to an empty square]
    e is the destination cord [a tuple of the form (x, y)]
}

add_on contains additional information and not every element (tuple) in moves has it. These are the codes for additional info:
{
    10: white pawn en-passant to the right
    11: white pawn en-passant to the left
    12: black pawn en-passant to the right
    13: black pawn en-passant to the left
    14: white king-side castle
    15: white queen-side castle
    16: black king-side castle
    17: black queen-side castle
}
"""


class Engine():
    def __init__(self, board=None, turn=1, moves=[]) -> None:

        # Three lists of offsets - horizontal, diagonal and the third one is for the knight's movement.
        self.horizontal_offsets = ((1, 0), (-1, 0), (0, -1), (0, 1))
        self.diagonal_offsets = ((1, 1), (1, -1), (-1, 1), (-1, -1))
        self.knight_offsets = ((1, 2), (-1, 2), (1, -2), (-1, -2), (2, 1), (-2, 1), (2, -1), (-2, -1))

        # A dictionary of pieces being linked to the functions that return their possible end_cords.
        self.piece_function_key = {1: self.rook_cords,   -1: self.rook_cords, 
                                   2: self.knight_cords, -2: self.knight_cords, 
                                   3: self.bishop_cords, -3: self.bishop_cords, 
                                   4: self.queen_cords,  -4: self.queen_cords, 
                                   5: self.king_cords,   -5: self.king_cords, 
                                   6: self.pawn_cords,   -6: self.pawn_cords}

        # A list of all pieces, black_pieces and white_pieces.
        self.pieces = (-1, -2, -3, -4, -5, -6, 1, 2, 3, 4, 5, 6)
        self.black_pieces = tuple(self.pieces[:6])
        self.white_pieces = tuple(self.pieces[6:])

        # If board not given, simply reset the board, else take the values and store.
        if board == None:
            self.reset()
        else:
            self.board = board
            self.turn = turn 
            self.moves = moves

    # This function resets the board and empties the move log while setting the turn to 1 (white's turn).
    def reset(self) -> None:
        """
        - resets the board, player_turn and move log

        parameters:
            None

        returns:
            None
        """

        self.turn = 1 
        self.moves = []
        
        self.board = [[0 for _ in range(8)] for __ in range(8)]
            
        self.board[0][0] = self.pieces[0]
        self.board[0][1] = self.pieces[1]
        self.board[0][2] = self.pieces[2]
        self.board[0][3] = self.pieces[3]
        self.board[0][4] = self.pieces[4]
        self.board[0][5] = self.pieces[2]
        self.board[0][6] = self.pieces[1]
        self.board[0][7] = self.pieces[0]
        
        self.board[7][0] = self.pieces[6]
        self.board[7][1] = self.pieces[7]
        self.board[7][2] = self.pieces[8]
        self.board[7][3] = self.pieces[9]
        self.board[7][4] = self.pieces[10]
        self.board[7][5] = self.pieces[8]
        self.board[7][6] = self.pieces[7]
        self.board[7][7] = self.pieces[6]
        
        for i in range(8):
            self.board[1][i] = self.pieces[5]
            self.board[6][i] = self.pieces[11]

    # This function takes a cord as input and adds an offset to it with a multiple, i.e the number_of_squares.
    def offset(self, cord, offset, number_of_squares) -> list:
        return [cord[0] + offset[0] * number_of_squares, cord[1] + offset[1] * number_of_squares]

    # Generates all the possible cords that the rook can move to from the start cord (which is a tuple of the form (x, y)).
    # This includes illegal squares as well.
    def rook_cords(self, start_cord) -> list:
        possible_end_cords = []
        enemy_pieces = self.black_pieces if self.board[start_cord[0]][start_cord[1]] > 0 else self.white_pieces # List of enemy pieces.
        max_squares = 8 if self.board[start_cord[0]][start_cord[1]] not in (5, -5) else 2 # Max offset multiplier.

        # 4 offsets - 4 directions, i.e top, down, left and right.
        for direction_index in range(4):
            # Max of 8 squares for rook and 1 square for king.
            for n in range(1, max_squares):
                # adds the offset
                m, n = self.offset(start_cord, self.horizontal_offsets[direction_index], n)

                # If the end_cord is in enemy_pieces then it is a valid_cord but the search must stop.
                if 0 <= m <= 7 and 0 <= n <= 7 and self.board[m][n] in enemy_pieces:
                    possible_end_cords.append((m, n))
                    break

                # If the end_cord is empty, it is a valid_cord and search must continue.
                elif 0 <= m <= 7 and 0 <= n <= 7 and self.board[m][n] == 0:
                    possible_end_cords.append((m, n))

                # If neither, it is either an invalid cord on an 8 x 8 board or it is occupied by a same color piece (also invalid); nevertheless, search must stop.
                else:
                    break

        return possible_end_cords

    # Generates all the possible cords that the bishop can move to from the start cord (which is a tuple of the form (x, y)).
    # This includes illegal squares as well.
    # Same logic as above but with a different offsets.
    def bishop_cords(self, start_cord) -> list:
        possible_end_cords = []
        enemy_pieces = self.black_pieces if self.board[start_cord[0]][start_cord[1]] > 0 else self.white_pieces
        max_squares = 8 if self.board[start_cord[0]][start_cord[1]] not in (5, -5) else 2
        
        for direction_index in range(4):
            for n in range(1, max_squares):
                m, n = self.offset(start_cord, self.diagonal_offsets[direction_index], n)
                if 0 <= m <= 7 and 0 <= n <= 7 and self.board[m][n] in enemy_pieces:
                    possible_end_cords.append((m, n))
                    break
                elif 0 <= m <= 7 and 0 <= n <= 7 and self.board[m][n] == 0:
                    possible_end_cords.append((m, n))
                else:
                    break

        return possible_end_cords

    # Generates all possible cords that the pawns can move to from the start cord (which is a tuple of the form (x, y)).
    # This includes illegal squares as well.
    def pawn_cords(self, start_cord) -> list:
        possible_end_cords = []
        enemy_pieces = self.black_pieces if self.board[start_cord[0]][start_cord[1]] > 0 else self.white_pieces

        x = start_cord[0]
        y = start_cord[1]

        # If color is white.
        if enemy_pieces[0] == -1:

            if len(self.moves) > 0: # If a previous move has been made.
                previous_move = self.moves[-1] # The previous move

                # If right square is occupied by black pawn AND if start_cord of prev move is of form (1, y + 1), i.e from 7th rank 
                # AND if the destination was DIRECTLY to the adjacent right cord (on 5th rank),
                # then en-passant is possible.
                if x > 0 and y < 7 and self.board[x][y + 1] == -6 and previous_move[0] == -6 and previous_move[1] == (1, y + 1) and previous_move[3] == (3, y + 1): 
                    possible_end_cords.append((x - 1, y + 1))

                # Same logic as above but with left square.
                if x > 0 and y > 0 and self.board[x][y - 1] == -6 and previous_move[0] == -6 and previous_move[1] == (1, y - 1) and previous_move[3] == (3, y - 1): 
                    possible_end_cords.append((x - 1, y - 1))

            # Diagonal movement (diagonal_offsets [3] and [4] for top-right and top-left) with offset multiplier equal to 1.
            for direction_index in range(2, 4):
                m, n = self.offset(start_cord, self.diagonal_offsets[direction_index], 1)
                # Only if the diagonal square is occupied by enemy piece, is the square valid.
                if 0 <= m <= 7 and 0 <= n <= 7 and self.board[m][n] in enemy_pieces:
                    possible_end_cords.append((m, n))

            # Checks if square above is free, i.e if it can move to the 3rd rank.
            if x > 0 and self.board[x - 1][y] == 0: 
                possible_end_cords.append((x - 1, y))

            # If start rank is the 2nd rank and all squares in between are empty, then it can move to 4th rank.
            if x == 6 and self.board[x - 2][y] == 0 and self.board[x - 1][y] == 0: 
                possible_end_cords.append((x - 2, y))    

        # Same logic as above but for black pawns.
        if enemy_pieces[0] == 1:

            if len(self.moves) > 0:
                previous_move = self.moves[-1]
                if x < 7 and y < 7 and self.board[x][y + 1] == 6 and previous_move[0] == 6 and previous_move[1] == (6, y + 1) and previous_move[3] == (4, y + 1): 
                    possible_end_cords.append((x + 1, y + 1))
                if x < 7 and y > 0 and self.board[x][y - 1] == 6 and previous_move[0] == 6 and previous_move[1] == (6, y - 1) and previous_move[3] == (4, y - 1): 
                    possible_end_cords.append((x + 1, y - 1))

            for direction_index in range(2):
                m, n  = self.offset(start_cord, self.diagonal_offsets[direction_index], 1)
                if 0 <= m <= 7 and 0 <= n <= 7 and self.board[m][n] in enemy_pieces:
                    possible_end_cords.append((m, n))

            if x < 7 and self.board[x + 1][y] == 0: 
                possible_end_cords.append((x + 1, y))
            if x == 1 and self.board[x + 2][y] == 0 and self.board[x + 1][y] == 0: 
                possible_end_cords.append((x + 2, y))
        return possible_end_cords
            
    # Generates all possible cords that the knight can move to from the start cord (which is a tuple of the form (x, y)).
    # This includes illegal squares as well.
    def knight_cords(self, start_cord):
        possible_end_cords = []
        enemy_pieces = self.black_pieces if self.board[start_cord[0]][start_cord[1]] > 0 else self.white_pieces

        # For knight_offsets with m const and equal to 1.
        for direction_index in range(8):
            m, n = self.offset(start_cord, self.knight_offsets[direction_index], 1)
            if 0 <= m <= 7 and 0 <= n <= 7 and (self.board[m][n] in enemy_pieces or self.board[m][n] == 0):
                possible_end_cords.append((m, n))
        return possible_end_cords

    # Generates all possible cords that the queen can move to from the start cord (which is a tuple of the form (x, y)).
    # Simply add rook and bishop cords from that square.
    # This includes illegal squares as well.
    def queen_cords(self, start_cord) -> list:
        return list(self.bishop_cords(start_cord) + self.rook_cords(start_cord))

    # Generates all possible cords that the king can move to from a start cord - s (which is a tuple of the form (x, y)).
    # Simply add rook and bishop cords from that square, but with offset multiplier equal to 1.
    # Also checks for castling moves.
    # This includes illegal squares as well.
    def king_cords(self, start_cord) -> list:
        possible_end_cords = []

        # If start cord of king is where it is at the start of the game AND
        # the king on that square has not been moved AND
        # the rook to the right at the end, that is, has not been moved AND
        # all squares in between are empty AND
        # the king is NOT in check.
        if start_cord == (7, 4) and not self.moved(5, (7, 4)) and not self.moved(1, (7, 7)) and self.board[7][5:7] == [0, 0] and not self.in_check(1):
            # Simulate king moving one step to the right.
            self.board[7][4:7] = [0, 5, 0]

            # Check if in that position, check is delivered.
            if not self.in_check(1):

                # Simulate king moving two steps to the right.
                self.board[7][4:7] = [0, 0, 5]

                # Check if in that position, check is delivered.
                if not self.in_check(1): 

                    # Reset to original state.
                    self.board[7][4:7] = [5, 0, 0]

                    # Add two steps to the right as valid, don't worry about hinting that it is a castling move, for the move_maker() will handle that.
                    possible_end_cords.append((7, 6))

            # Reset to original state.
            self.board[7][4:7] = [5, 0, 0]
            

        # Same logic as above.
        if start_cord == (7, 4) and not self.moved(5, (7, 4)) and not self.moved(1, (7, 0)) and self.board[7][1:4] == [0, 0, 0] and not self.in_check(1):
            self.board[7][2:5] = [0, 5, 0]

            if not self.in_check(1):
                self.board[7][2:5] = [5, 0, 0]

                if not self.in_check(1):
                    self.board[7][2:5] = [0, 0, 5]
                    possible_end_cords.append((7, 2))

            self.board[7][2:5] = [0, 0, 5]
            
        if start_cord == (0, 4) and not self.moved(-5, (0, 4)) and not self.moved(-1, (0, 7)) and self.board[0][5:7] == [0, 0] and not self.in_check(-1):
            self.board[0][4:7] = [0, -5, 0]

            if not self.in_check(-1):
                self.board[0][4:7] = [0, 0, -5]

                if not self.in_check(-1):
                    self.board[0][4:7] = [-5, 0, 0]
                    possible_end_cords.append((0, 6))

            self.board[0][4:7] = [-5, 0, 0]
            
        if start_cord == (0, 4) and not self.moved(-5, (0, 4)) and not self.moved(-1, (0, 0)) and self.board[0][1:4] == [0, 0, 0] and not self.in_check(-1):
            self.board[0][2:5] = [0, -5, 0]

            if not self.in_check(-1):
                self.board[0][2:5] = [-5, 0, 0]

                if not self.in_check(-1):
                    self.board[0][2:5] = [0, 0, -5]

                    possible_end_cords.append((0, 2))
            self.board[0][2:5] = [0, 0, -5]
        
        # Extend rook and bishop movement as well but with max_squares constant and equal to 1.
        possible_end_cords.extend(self.bishop_cords(start_cord) + self.rook_cords(start_cord))
        return possible_end_cords

    # Check if a piece had ever moved from a cord.
    def moved(self, piece, cord) -> bool:
        for move in self.moves:
            if move[0] == piece and move[1] == cord:
                return True
        return False

    # checks if the king of color is in check;
    # color is 1 (for white) or -1 (for black).
    def in_check(self, color) -> bool:
        """
        parameters:
            color:
                Type: int
                Values: 1 (white) or -1 (black)

        returns:
            True or False if the color (c) is under check; else None for invalid input
        """

        if color == 1:
            enemy_pieces = self.black_pieces
        elif color == -1:
            enemy_pieces = self.white_pieces
        else:
            return None
        
        # Locate the king's cords.
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == 5 and color == 1: 
                    king_cord = (i, j)
                    break
                elif self.board[i][j] == -5 and color == -1: 
                    king_cord = (i, j)
                    break

        # For every piece on the board, if it is occpied by an enemy piece and its end_cords include the king_cord, then the king is under check.       
        for m in range(8):
            for n in range(8):
                if self.board[m][n] in enemy_pieces and king_cord in self.piece_function_key[self.board[m][n]]((m, n)):
                    return True
        return False

    # Checks if side (color: 1 for white and -1 for black) can move any piece.
    def cannot_move(self, color) -> bool:
        self_pieces = self.white_pieces if color == 1 else self.black_pieces

        for x in range(8):
            for y in range(8):
                # If a cord is occupied by piece of the same color.
                if self.board[x][y] in self_pieces:
                    # If there is any legal move at all
                    if len(self.get_all_legal_moves((x, y))) > 0:
                        return False
        return True

    # Generates all legal moves for a particular start cord
    def get_all_legal_moves(self, start_cord) -> list:
        """
        parameters:
            start_cord:
                Type: iterable object of length 2
                Values: the co-ordinate of the piece to be moved

        returns:
            A list of all possible legal moves
        """

        x, y = start_cord
        color = 1 if self.board[x][y] > 0 else -1
        all_legal_moves = []

        # If square is empty, return the empty list
        if self.board[x][y] == 0:
            return all_legal_moves
  
        # List of possible end cords (including illegal moves).
        all_possible_end_cords = self.piece_function_key[self.board[x][y]]((x, y))

        # If all_possible_end_cords is not empty.
        if all_possible_end_cords != []:
            
            # For each end_cord.
            for cord in all_possible_end_cords:

                # Simulate the move.
                piece_moved = self.board[x][y]
                piece_captured = self.board[cord[0]][cord[1]]

                self.board[x][y] = 0
                self.board[cord[0]][cord[1]] = piece_moved
                
                # Checks if in_check.
                if not self.in_check(color):
                    all_legal_moves.append(cord)
                
                # Undo move to leave self.board unaltered after this function terminates.
                self.board[x][y] = piece_moved
                self.board[cord[0]][cord[1]] = piece_captured

        return all_legal_moves

    # Checks if the board state is a draw.
    def is_draw(self) -> bool:
        """
        parameters:
            None

        returns:
            True if game state is a draw; else False
        """

        # If the previous 3 moves were the same, yes.
        if len(self.moves) >= 9 and self.moves[-1] == self.moves[-5] == self.moves[-9]: 
            return True

        # If in the last 50 moves, no pawn was moved OR no piece was captured, yes.
        if len(self.moves) >= 50:
            for i in range(-1, -51, -1):
                if self.moves[i][3] != 0 or self.moves[i][0] in (6, -6): 
                    return False
            return True
        
        white_pieces = []
        black_pieces = []
        for row in self.board:
            for piece in row:
                if piece < 0 :
                    black_pieces.append(piece)
                elif piece > 0: 
                    white_pieces.append(piece)

        white_pieces = sorted(white_pieces)
        black_pieces = sorted(black_pieces)
        
        # If certain piece combinations are observed on the board, yes:
        # evident below.
        if white_pieces in ([5], [3, 5], [2, 5]) and black_pieces in ([-5], [-5, -3], [-5, -2]): 
            return True
        elif white_pieces == [2, 2, 5] and black_pieces == [-5]: 
            return True
        elif black_pieces == [-5, -2, -2] and white_pieces == [5]: 
            return True 
        return False

    # If a color cannot move and it is in check, checkmate.
    def is_checkmate(self) -> bool:
        """
        paramters:
            None
            
        returns:
            1 if white has been check-mated; -1 if black has been check-mated; else None
        """

        if self.cannot_move(self.turn) and self.in_check(self.turn): 
            return self.turn
    
    # If a color cannot move, but it is NOT in check, stalemate.
    def is_stalemate(self) -> bool:
        """
        parameters:
            None
            
        returns:
            True if game state is a stalemate; else False
        """

        if self.cannot_move(self.turn) and not self.in_check(self.turn): 
            return True

    # Checks if for the start_cord and end_cord, the move is a promotion move.
    def is_promotion_move(self, start_cord, end_cord):
        if ((self.board[start_cord[0]][start_cord[1]] == 6 and end_cord[0] == 0 and end_cord in self.piece_function_key[6](start_cord)) or 
            (self.board[start_cord[0]][start_cord[1]] == -6 and end_cord[0] == 7 and end_cord in self.piece_function_key[-6](start_cord))):
            return True
        return False

    # Move maker function that takes start cord , end cord and possibly a pawn promotion piece.
    # If promotion_piece is not specified, the piece promoted will automatically be the queen of the player's color.
    # It makes the move and returns True if the move making was a success, however if the move could not be made,
    # self.board remains unchanged but False is returned, indicating failure.
    def make_move(self, start_cord, end_cord, promotion_piece=None) -> bool:
        """
        parameters:
            start_cord:
                Type: iterable object of length 2
                Values: the co-ordinate of the piece to be moved

            end_cord:
                Type: iterable object of length 2
                Values: the co-ordinate the piece is to be moved to

            promotion_piece [OPTIONAL]:
                Type: int 
                Values: piece_code of the piece, the pawn is to be promoted to IF the move is a promotion move. Set to Queen (4, -4) by deafult.

        returns:
            True if move was successfully made else False if the move was an illegal move, and thus a failed attempt.
        """

        x1 = start_cord[0]
        y1 = start_cord[1]

        x2 = end_cord[0]
        y2 = end_cord[1]

        # If it is actually the color's turn.
        if (self.turn > 0 and self.board[x1][y1] > 0) or (self.turn < 0 and self.board[x1][y1] < 0):
            
            # If the end_cord is a possible cord (also possibly illegal).
            if end_cord in self.get_all_legal_moves(start_cord):

                # If promotion_piece not given, set to queen of the respective color.
                if promotion_piece == None:
                    promotion_piece = 4 if self.turn == 1 else -4

                # add_on not yet specified, but declared.
                add_on = None

                # Flag for if_promotion is possible.
                is_promotion = False

                # Piece to be moved.
                piece_moved = self.board[x1][y1]

                # Piece to be captured (could be 0).
                piece_captured = self.board[x2][y2]

                # If promotion is possible , flag True.
                if self.is_promotion_move(start_cord, end_cord):
                    is_promotion = True

                # Checks if en-passant is possible AND is the chosen move.
                # The required add_on is set.
                if len(self.moves) > 0:
                    prev = self.moves[-1]
                    if end_cord == (x1 - 1, y1 + 1) and x1 > 0 and y1 < 7 and self.board[x1][y1 + 1] == -6 and prev[0] == -6 and prev[1] == (1, y1 + 1) and prev[3] == (3, y1 + 1): 
                            self.board[x1][y1 + 1] = 0
                            add_on = 10
                        
                    elif end_cord == (x1 - 1, y1 - 1) and x1 > 0 and y1 > 0 and self.board[x1][y1 - 1] == -6 and prev[0] == -6 and prev[1] == (1, y1 - 1) and prev[3] == (3, y1 - 1): 
                            self.board[x1][y1 - 1] = 0
                            add_on = 11

                    elif end_cord == (x1 + 1, y1 + 1) and x1 < 7 and y1 < 7 and self.board[x1][y1 + 1] == 6 and prev[0] == 6 and prev[1] == (6, y1 + 1) and prev[3] == (4, y1 + 1): 
                            self.board[x1][y1 + 1] = 0
                            add_on = 12
                        
                    elif end_cord == (x1 + 1, y1 - 1) and x1 < 7 and y1 > 0 and self.board[x1][y1 - 1] == 6 and prev[0] == 6 and prev[1] == (6, y1 - 1) and prev[3] == (4, y1 - 1): 
                            self.board[x1][y1 - 1] = 0
                            add_on = 13
                
                # Move has been made.
                self.board[x1][y1] = 0
                self.board[x2][y2] = piece_moved

                # Checks if the move is castling and sets the required add_on. 
                if piece_moved == 5 and start_cord == (7, 4) and end_cord == (7, 6): 
                    self.board[7][5] = 1
                    self.board[7][7] = 0
                    add_on = 14
    
                elif piece_moved == 5 and start_cord == (7, 4) and end_cord == (7, 2): 
                    self.board[7][3] = 1
                    self.board[7][0] = 0
                    add_on = 15
            
                elif piece_moved == -5 and start_cord == (0, 4) and end_cord == (0, 6): 
                    self.board[0][5] = -1
                    self.board[0][7] = 0
                    add_on = 16
                
                elif piece_moved == -5 and start_cord == (0, 4) and end_cord == (0, 2): 
                    self.board[0][3] = -1
                    self.board[0][0] = 0
                    add_on = 17

                # If promotion flag is True, the end_cord is replaced with promotion_piece.
                elif is_promotion:
                    self.board[x2][y2] = promotion_piece

                # Move added to logs and success returned.
                if add_on == None:
                    self.moves.append((piece_moved, start_cord, piece_captured, end_cord))
                else:
                    self.moves.append((piece_moved, start_cord, piece_captured, end_cord, add_on))

                # It is now the opponent's turn.
                self.turn *= -1
                return True

        # If not that player's turn or end_cord is invalid, False returned, indicating failure.
        return False

    # Function that undoes the most recent move. 
    def undo_move(self) -> bool:
        """
        parameters:
            None
            
        returns:
            True if the latest move was undone else False if no move was made before call.
        """

        if len(self.moves) > 0:
            # Simple switch.
            previous_move = self.moves[-1]
            self.board[previous_move[1][0]][previous_move[1][1]] = previous_move[0]
            self.board[previous_move[3][0]][previous_move[3][1]] = previous_move[2]
            
            # If add_on detected...
            # pawns are added back in case of en-passant add-ons AND
            # rooks are placed in their previous positions in case of castling add_ons.
            if len(previous_move) == 5:
                if previous_move[4] == 10: 
                    self.board[previous_move[1][0]][previous_move[1][1] + 1] = -6
                    
                elif previous_move[4] == 11:
                    self.board[previous_move[1][0]][previous_move[1][1] - 1] = -6
                    
                elif previous_move[4] == 12:
                    self.board[previous_move[1][0]][previous_move[1][1] + 1] = 6
                    
                elif previous_move[4] == 13:
                    self.board[previous_move[1][0]][previous_move[1][1] - 1] = 6

                elif previous_move[4] == 14: 
                    self.board[7][7] = 1
                    self.board[7][5] = 0
                    
                elif previous_move[4] == 15:
                    self.board[7][0] = 1
                    self.board[7][3] = 0
                    
                elif previous_move[4] == 16: 
                    self.board[0][7] = -1
                    self.board[0][5] = 0
                    
                elif previous_move[4] == 17: 
                    self.board[0][0] = -1
                    self.board[0][3] = 0

            # Delete the log.
            del self.moves[-1]

            # Reverse the turn.
            self.turn *= -1

            return True

        else:
            return False
