import numpy as np

class Board():
    piece_map = { 1: 10, -1: 11, 2: 0, -2: 1, 3: 4, -3: 5, 4: 6, -4: 7, 5: 2, -5: 3, 6: 8, -6: 9 }
    int_to_letter = {
        0: ' ', 1: 'K',  2: 'P',  3: 'N',  4: 'B',  5: 'R',  6: 'Q',
                -1: 'k', -2: 'p', -3: 'n', -4: 'b', -5: 'r', -6: 'q'
    }
    letter_to_int = {
        'K':  1, 'P':  2, 'N':  3, 'B':  4, 'R':  5, 'Q':  6,
        'k': -1, 'p': -2, 'n': -3, 'b': -4, 'r': -5, 'q': -6
    }
    def __init__(self, fen='rnbqkbnr/pppppppp/8/8/8/8/3PPP2/4K3 w kq - 0 1'):
        self.reset_game(fen)

    def reset_game(self, fen):
        self.board = np.zeros((8, 8))

        piece_loc, turn, castles, en_passant, halfmove, fullmove = fen.split(' ')
        for row_index, row in enumerate(piece_loc.split('/')[::-1]):
            col_index = 0
            for chr in row:
                if chr in self.letter_to_int:
                    self.board[row_index, col_index] = self.letter_to_int[chr]
                elif chr.isnumeric():
                    col_index += int(chr) - 1
                else:
                    raise ValueError(f'FEN position is invalid: {fen}')
                col_index += 1

        self.turn = (turn == 'w')

        self._white_castle_kingside = 'K' in castles
        self._white_castle_queenside = 'Q' in castles
        self._black_castle_kingside = 'k' in castles
        self._black_castle_queenside = 'q' in castles

    def __repr__(self):
        fboard = np.flip(self.board, axis=0)
        repr = '-----------------\n'
        for row in range(8):
            row_repr = '|'
            for col in range(8):
                row_repr += f'{self.int_to_letter[int(fboard[row, col])]}|'
            repr += row_repr + '\n'
        return repr + '-----------------'

    def _blackbird_board_state(self):
        """ Convert the human board state into a binary array for BlackBird
            Layers are defined as follow:

            0: White pawns
            1: Black pawns
            2: White rooks
            3: Black rooks
            4: White knights
            5: Black knights
            6: White bishops
            7: Black bishops
            8: White queens
            9: Black queens
            10: White kings
            11: Black kings
            12: White can castle kingside
            13: Black can castle kingside
            14: White can castle queenside
            15: Black can castle queenside
        """
        state = np.zeros((8, 8, 16))

        for row in range(self.board.shape[0]):
            for col in range(self.board.shape[1]):
                if self.board[row, col] != 0:
                    state[row, col, self.piece_map[self.board[row, col]]] = 1

        state[:, :, 12] = int(self._white_castle_kingside)
        state[:, :, 13] = int(self._white_castle_queenside)
        state[:, :, 14] = int(self._black_castle_kingside)
        state[:, :, 15] = int(self._black_castle_queenside)

        return state

    def get_legal_moves(self): # white king, white pawn, ..., black king, black pawn, white castle king, white castle queen, black castle king, black castle queen
        legal = np.zeros((7352))
        color = int(not self.turn) # 0 = white, 1 = black
        legal[3674*color+0] = self._is_legal_move_king(0, 0, 1, 0)
        legal[3674*color+1] = self._is_legal_move_king(0, 0, 1, 1)
        legal[3674*color+2] = self._is_legal_move_king(0, 0, 0, 1)
        for col in range(1, 7):
            legal[3674*color+5*col-2] = self._is_legal_move_king(0, col, 0, col-1)
            for i in range(col-1, col+2):
                legal[3674*color+5*col+(i-col)] = self._is_legal_move_king(0, col, 1, i)
            legal[3674*color+5*col+2] = self._is_legal_move_king(0, col, 0, col+1)
        legal[3674*color+33] = self._is_legal_move_king(0, 7, 0, 6)
        legal[3674*color+34] = self._is_legal_move_king(0, 7, 1, 6)
        legal[3674*color+35] = self._is_legal_move_king(0, 7, 1, 7)
        for row in range(1, 7):
            for col in [0, 7]:
                legal[3674*color+int(36+5*(2*row-2+col/7))] = self._is_legal_move_king(row, col, row+1, col)
                legal[3674*color+int(37+5*(2*row-2+col/7))] = self._is_legal_move_king(row, col, row+1, col+1)
                legal[3674*color+int(38+5*(2*row-2+col/7))] = self._is_legal_move_king(row, col, row, col+1)
                legal[3674*color+int(39+5*(2*row-2+col/7))] = self._is_legal_move_king(row, col, row-1, col+1)
                legal[3674*color+int(40+5*(2*row-2+col/7))] = self._is_legal_move_king(row, col, row-1, col)
        legal[3674*color+96] = self._is_legal_move_king(7, 0, 7, 1)
        legal[3674*color+97] = self._is_legal_move_king(7, 0, 6, 1)
        legal[3674*color+98] = self._is_legal_move_king(7, 0, 6, 0)
        for col in range(1, 7):
            legal[3674*color+5*col+94] = self._is_legal_move_king(7, col, 7, col+1)
            for i in range(-1, 2):
                legal[3674*color+5*col+96+i] = self._is_legal_move_king(7, col, 6, col-i)
            legal[3674*color+5*col+98] = self._is_legal_move_king(7, col, 7, col-1)
        legal[3674*color+129] = self._is_legal_move_king(7, 7, 6, 7)
        legal[3674*color+130] = self._is_legal_move_king(7, 7, 6, 6)
        legal[3674*color+131] = self._is_legal_move_king(7, 7, 7, 6)
        for row in range(1, 7):
            for col in range(1, 7):
                legal[3674*color+132+8*(6*(row-1)+col-1)] = self._is_legal_move_king(row, col, row+1, col)
                legal[3674*color+133+8*(6*(row-1)+col-1)] = self._is_legal_move_king(row, col, row+1, col+1)
                legal[3674*color+134+8*(6*(row-1)+col-1)] = self._is_legal_move_king(row, col, row, col+1)
                legal[3674*color+135+8*(6*(row-1)+col-1)] = self._is_legal_move_king(row, col, row-1, col+1)
                legal[3674*color+136+8*(6*(row-1)+col-1)] = self._is_legal_move_king(row, col, row-1, col)
                legal[3674*color+137+8*(6*(row-1)+col-1)] = self._is_legal_move_king(row, col, row-1, col-1)
                legal[3674*color+138+8*(6*(row-1)+col-1)] = self._is_legal_move_king(row, col, row, col-1)
                legal[3674*color+139+8*(6*(row-1)+col-1)] = self._is_legal_move_king(row, col, row+1, col-1)
        # for col in range(8): # white pawns
        #     legal[10*col] = self._is_legal_move_pawn(1, col, 3, col)
        #     for start in range(1, 6):
        #         legal[10*col+start] = self._is_legal_move_pawn(start, col, )

        ######## DON'T FORGET CASTLING
        return legal
   
    def _is_legal_move(self, loc_row, loc_col, new_row, new_col):
        if not (-1 < new_row < 8) or not (-1 < new_col < 8): # Moving outside of the board
            return False
        if [new_row, new_col] == [loc_row, loc_col]: # Moving to the square you're already on
            return False
        if self.board[loc_row, loc_col] > 0: # Moving to a square occupied by the same color piece
            if self.board[new_row, new_col] > 0:
                return False
        else:
            if self.board[new_row, new_col] < 0:
                return False
        if self.board[loc_row, loc_col] < 0 and self.turn: # black piece on white's turn
            return False
        elif self.board[loc_row, loc_col] > 0 and not self.turn: # white piece on black's turn
            return False
        elif self.board[loc_row, loc_col] == 0: # no piece
            return False
        return True

    def _is_legal_move_pawn(self, loc_row, loc_col, new_row, new_col):
        if not self._is_legal_move(loc_row, loc_col, new_row, new_col):
            return False
        if not abs(self.board[loc_row, loc_col]) == 2:
            return False
        if self.board[loc_row, loc_col] > 0:
            if loc_row == 1:
                if loc_col == new_col:
                    if new_row == 3 and self.board[3, new_col] == 0 and self.board[2, new_col] == 0:
                        return True
                    elif new_row == 2 and self.board[2, new_col] == 0:
                        return True
                    return False
            if abs(loc_col - new_col) == 1:
                if new_row == loc_row + 1:
                    if self.board[new_row, new_col] < 0:
                        return True
        else:
            if loc_row == 6:
                if loc_col == new_col:
                    if new_row == 4 and self.board[4, new_col] == 0 and self.board[5, new_col] == 0:
                        return True
                    elif new_row == 5 and self.board[5, new_col] == 0:
                        return True
                    return False
            if abs(loc_col - new_col) == 1:
                if new_row == loc_row-1:
                    if self.board[new_row, new_col] > 0:
                        return True
        return False

    def _is_legal_move_rook(self, loc_row, loc_col, new_row, new_col):
        if not self._is_legal_move(loc_row, loc_col, new_row, new_col):
            return False

        direction = (new_row == loc_row or new_col == loc_col)

        if not direction:
            return False

        no_obstacle = True
        if new_row == loc_row:
            for col in range(min(new_col, loc_col)+1, max(new_col, loc_col)):
                if self.board[new_row, col] != 0:
                    no_obstacle = False
                    break
        else:
            for row in range(min(new_row, loc_row)+1, max(new_row, loc_row)):
                if self.board[row, new_col] != 0:
                    no_obstacle = False
                    break

        return direction and no_obstacle

    def _is_legal_move_bishop(self, loc_row, loc_col, new_row, new_col):
        if not self._is_legal_move(loc_row, loc_col, new_row, new_col):
            return False
        if abs(loc_row-new_row) != abs(loc_col-new_col):
            return False
        for diag in range(1, abs(loc_row-new_row)):
            if self.board[loc_row+diag*np.sign(new_row-loc_row), loc_col+diag*np.sign(new_col-loc_col)] != 0:
                return False
        return True

    def _is_legal_move_queen(self, loc_row, loc_col, new_row, new_col):
        return self._is_legal_move_bishop(loc_row, loc_col, new_row, new_col) or \
               self._is_legal_move_rook(loc_row, loc_col, new_row, new_col)

    def _is_legal_move_king(self, loc_row, loc_col, new_row, new_col):
        if not self._is_legal_move(loc_row, loc_col, new_row, new_col):
            return False
        if not abs(self.board[loc_row, loc_col]) == 1:
            return False
        if abs(loc_row-new_row) <= 1 and abs(loc_col-new_col) <= 1:
            return True
        return False

    def _is_legal_move_knight(self, loc_row, loc_col, new_row, new_col):
        if not self._is_legal_move(loc_row, loc_col, new_row, new_col):
            return False
        if abs(loc_row-new_row) == 1 and abs(loc_col-new_col) == 2:
            return True
        elif abs(loc_row-new_row) == 2 and abs(loc_col-new_col) == 1:
            return True
        return False

    def move(self, loc_row, loc_col, new_row, new_col):
        piece_map = {
            1: self._is_legal_move_king,
            2: self._is_legal_move_pawn,
            3: self._is_legal_move_knight,
            4: self._is_legal_move_bishop,
            5: self._is_legal_move_rook,
            6: self._is_legal_move_queen,
        }
        pieceType = abs(self.board[loc_row, loc_col])
        if pieceType <= 0 or pieceType > 6: # Nothing on the square you're moving from
            return ValueError
        if piece_map[pieceType](loc_row, loc_col, new_row, new_col):
            self.board[new_row, new_col] = self.board[loc_row, loc_col]
            self.board[loc_row, loc_col] = 0
            self.turn = not self.turn
        else:
            return ValueError

if __name__ == '__main__':
    board = Board('1r3r1k/p2b2p1/7p/2pBb2Q/3pP1P1/4q3/PPP3K1/R6R w - - 4 28')
    lm = board.get_legal_moves()
    for i in range(len(lm)):
        if lm[i] == 1:
            print(i)
    # board.move(6, 4, 4, 4)
    # board.move(7, 5, 5, 3)
    # print(board._blackbird_board_state()[:, :, 0])
    print(board)
