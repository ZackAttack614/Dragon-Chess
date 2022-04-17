import numpy as np

class Board():
    piece_map = { 1: 10, -1: 11, 2: 0, -2: 1, 3: 4, -3: 5, 4: 6, -4: 7, 5: 2, -5: 3, 6: 8, -6: 9 }
    def __init__(self): # +-1 = king, +-2 = pawn, -3 = knight, -4 = bishop, -5 = rook, -6 = queen
        self.board = np.zeros((8, 8))
        self.board[0, 4] = 1
        self.board[1, 3:6] = 2
        self.board[6, :] = -2
        self.board[7, 0] = -5
        self.board[7, 1] = -3
        self.board[7, 2] = -4
        self.board[7, 3] = -6
        self.board[7, 4] = -1
        self.board[7, 5] = -4
        self.board[7, 6] = -3
        self.board[7, 7] = -5

        self._white_castle_kingside = False
        self._white_castle_queenside = False
        self._black_castle_kingside = True
        self._black_castle_queenside = True

    def __repr__(self):
        int_to_letter = {
            0: ' ', 1: 'K', 2: 'P', 3: 'N', 4: 'B', 5: 'R', 6: 'Q',
            -1: 'k', -2: 'p', -3: 'n', -4: 'b', -5: 'r', -6: 'q'
        }
        fboard = np.flip(self.board, axis=0)
        repr = '-----------------\n'
        for row in range(8):
            row_repr = '|'
            for col in range(8):
                row_repr += f'{int_to_letter[int(fboard[row, col])]}|'
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

    def get_legal_moves(self): # white king, black king, white pawn, black pawn, ..., black castle king, black castle queen
        legal = np.array((4000))
        legal[0] = self._is_legal_move_king(0, 0, 1, 0)
        legal[1] = self._is_legal_move_king(0, 0, 1, 1)
        legal[2] = self._is_legal_move_king(0, 0, 0, 1)
        for col in range(1, 7):
            legal[5*col-2] = self._is_legal_move_king(0, col, 0, col-1)
            for i in range(col-1, col+2):
                legal[5*col+(i-col)] = self._is_legal_move_king(0, col, 1, i)
            legal[5*col+2] = self._is_legal_move_king(0, col, 0, col+1)
        legal[33] = self._is_legal_move_king(0, 7, 0, 6)
        legal[34] = self._is_legal_move_king(0, 7, 1, 6)
        legal[35] = self._is_legal_move_king(0, 7, 1, 7)
        for row in range(1, 7):
            for col in [0, 7]:
                legal[36+5*(2*row-2+col/7)] = self._is_legal_move_king(row, col, row+1, col)
                legal[37+5*(2*row-2+col/7)] = self._is_legal_move_king(row, col, row+1, col+1)
                legal[38+5*(2*row-2+col/7)] = self._is_legal_move_king(row, col, row, col+1)
                legal[39+5*(2*row-2+col/7)] = self._is_legal_move_king(row, col, row-1, col+1)
                legal[40+5*(2*row-2+col/7)] = self._is_legal_move_king(row, col, row-1, col)
        legal[96] = self._is_legal_move_king(7, 0, 7, 1)
        legal[97] = self._is_legal_move_king(7, 0, 6, 1)
        legal[98] = self._is_legal_move_king(7, 0, 6, 0)
        for col in range(1, 7):
            legal[5*col+94] = self._is_legal_move_
        # for col in range(8): # white king first row
            
        # for col in range(8): # white pawns
        #     legal[10*col] = self._is_legal_move_pawn(1, col, 3, col)
        #     for start in range(1, 6):
        #         legal[10*col+start] = self._is_legal_move_pawn(start, col, )
   
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
        else:
            return ValueError

if __name__ == '__main__':
    board = Board()
    board.move(6, 4, 4, 4)
    board.move(7, 5, 5, 3)
    print(board._blackbird_board_state()[:, :, 0])
    # print(board)