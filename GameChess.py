import copy

class ChessPiece:
    def __init__(self, color, symbol):
        self.color = color
        self.symbol = symbol
        self.has_moved = False

    def __str__(self):
        return self.symbol

    def is_valid_move(self, board, start, end):
        return False

class Pawn(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'P' if color == 'white' else 'p')
        self.en_passant_vulnerable = False

    def is_valid_move(self, board, start, end):
        start_row, start_col = start
        end_row, end_col = end
        
        if self.color == 'white':
            if start_row == 6 and end_row == 4 and start_col == end_col:
                return board[5][start_col] is None and board[4][start_col] is None
            if end_row == start_row - 1 and start_col == end_col:
                return board[end_row][end_col] is None
            if end_row == start_row - 1 and abs(end_col - start_col) == 1:
                if board[end_row][end_col] is not None:
                    return board[end_row][end_col].color != self.color
                # En Passant
                if start_row == 3 and board[start_row][end_col] is not None:
                    return isinstance(board[start_row][end_col], Pawn) and board[start_row][end_col].en_passant_vulnerable
        else:
            if start_row == 1 and end_row == 3 and start_col == end_col:
                return board[2][start_col] is None and board[3][start_col] is None
            if end_row == start_row + 1 and start_col == end_col:
                return board[end_row][end_col] is None
            if end_row == start_row + 1 and abs(end_col - start_col) == 1:
                if board[end_row][end_col] is not None:
                    return board[end_row][end_col].color != self.color
                # En Passant
                if start_row == 4 and board[start_row][end_col] is not None:
                    return isinstance(board[start_row][end_col], Pawn) and board[start_row][end_col].en_passant_vulnerable
        
        return False


class Rook(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'R' if color == 'white' else 'r')

    def is_valid_move(self, board, start, end):
        start_row, start_col = start
        end_row, end_col = end
        
        if start_row != end_row and start_col != end_col:
            return False
        
        direction_row = 0 if start_row == end_row else (1 if end_row > start_row else -1)
        direction_col = 0 if start_col == end_col else (1 if end_col > start_col else -1)
        
        current_row, current_col = start_row + direction_row, start_col + direction_col
        while (current_row, current_col) != (end_row, end_col):
            if board[current_row][current_col] is not None:
                return False
            current_row += direction_row
            current_col += direction_col
        
        return board[end_row][end_col] is None or board[end_row][end_col].color != self.color

class Knight(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'N' if color == 'white' else 'n')

    def is_valid_move(self, board, start, end):
        start_row, start_col = start
        end_row, end_col = end
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

class Bishop(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'B' if color == 'white' else 'b')

    def is_valid_move(self, board, start, end):
        start_row, start_col = start
        end_row, end_col = end
        if abs(end_row - start_row) != abs(end_col - start_col):
            return False
        
        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1
        
        current_row, current_col = start_row + row_step, start_col + col_step
        while (current_row, current_col) != (end_row, end_col):
            if board[current_row][current_col] is not None:
                return False
            current_row += row_step
            current_col += col_step
        
        return board[end_row][end_col] is None or board[end_row][end_col].color != self.color

class Queen(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'Q' if color == 'white' else 'q')

    def is_valid_move(self, board, start, end):
        rook = Rook(self.color)
        bishop = Bishop(self.color)
        return rook.is_valid_move(board, start, end) or bishop.is_valid_move(board, start, end)

class King(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'K' if color == 'white' else 'k')

    def is_valid_move(self, board, start, end):
        start_row, start_col = start
        end_row, end_col = end
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        return max(row_diff, col_diff) == 1

import pygame
import sys

# ... (previous chess piece classes remain the same)

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()
        self.current_player = 'white'
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.last_move = None
        self.move_history = []

    def setup_board(self):
        # إعداد البيادق
        for i in range(8):
            self.board[1][i] = Pawn('black')
            self.board[6][i] = Pawn('white')

        # إعداد القطع الأخرى
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i in range(8):
            self.board[0][i] = piece_order[i]('black')
            self.board[7][i] = piece_order[i]('white')
    def move_piece(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        piece = self.board[start_row][start_col]
        target_piece = self.board[end_row][end_col]
        en_passant_capture = False

        if piece:
            # التحقق من أن القطعة المستهدفة ليست من نفس لون القطعة التي يتم تحريكها
            if target_piece and target_piece.color == piece.color:
                return False
            
            if piece.is_valid_move(self.board, start, end):
                # حفظ الحركة الحالية للتراجع عنها لاحقًا
                self.move_history.append((start, end, target_piece, piece, en_passant_capture))

                # تحديث الموقع الجديد
                self.board[end_row][end_col] = piece
                self.board[start_row][start_col] = None

                # تحديث موقع الملك إذا تم تحريكه
                if isinstance(piece, King):
                    if piece.color == 'white':
                        self.white_king_pos = (end_row, end_col)
                    else:
                        self.black_king_pos = (end_row, end_col)

                # تغيير اللاعب الحالي
                self.current_player = 'white' if self.current_player == 'black' else 'black'
                return True
        return False

    def undo_last_move(self):
        if not self.move_history:
            return False

        last_move = self.move_history.pop()
        start, end, captured_piece, moved_piece, en_passant_capture = last_move

        # استعادة حالة اللوحة
        self.board[start[0]][start[1]] = moved_piece
        self.board[end[0]][end[1]] = captured_piece

        # معالجة حالة الأخذ بالتجاوز (en passant)
        if en_passant_capture:
            self.board[start[0]][end[1]] = Pawn('white' if self.current_player == 'black' else 'black')

        # تحديث موقع الملك إذا لزم الأمر
        if isinstance(moved_piece, King):
            if moved_piece.color == 'white':
                self.white_king_pos = start
            else:
                self.black_king_pos = start

        # تغيير اللاعب الحالي
        self.current_player = 'white' if self.current_player == 'black' else 'black'

        return True

    def is_in_check(self, player):
        king_pos = self.white_king_pos if player == 'white' else self.black_king_pos

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color != player:
                    if piece.is_valid_move(self.board, (row, col), king_pos):
                        return True
        return False

    def is_checkmate(self, player):
        if not self.is_in_check(player):
            return False

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == player:
                    for r in range(8):
                        for c in range(8):
                            if piece.is_valid_move(self.board, (row, col), (r, c)):
                                # إجراء الحركة مؤقتًا
                                original_piece = self.board[r][c]
                                self.board[r][c] = piece
                                self.board[row][col] = None
                                king_pos = (r, c) if isinstance(piece, King) else (self.white_king_pos if player == 'white' else self.black_king_pos)
                                if not self.is_in_check(player):
                                    # إرجاع الحركة
                                    self.board[row][col] = piece
                                    self.board[r][c] = original_piece
                                    return False
                                # إرجاع الحركة
                                self.board[row][col] = piece
                                self.board[r][c] = original_piece
        return True
class ChessGame:
    def __init__(self):
        pygame.init()
        self.width = 640
        self.height = 640
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self.board = ChessBoard()
        self.load_images()
        self.selected_piece = None
        self.font = pygame.font.Font(None, 36)
        self.game_over = False
        self.winner = None

    def load_images(self):
        pieces = ['p', 'r', 'n', 'b', 'q', 'k']
        self.images = {}
        for piece in pieces:
            self.images[f'w{piece}'] = pygame.transform.scale(pygame.image.load(f'images/w{piece}.png'), (80, 80))
            self.images[f'b{piece}'] = pygame.transform.scale(pygame.image.load(f'images/b{piece}.png'), (80, 80))

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
                pygame.draw.rect(self.screen, color, (col * 80, row * 80, 80, 80))
                
                piece = self.board.board[row][col]
                if piece:
                    symbol = piece.symbol.lower()
                    color = 'w' if piece.color == 'white' else 'b'
                    self.screen.blit(self.images[f'{color}{symbol}'], (col * 80, row * 80))

    def draw_message(self, message):
        text = self.font.render(message, True, (255, 0, 0))
        self.screen.blit(text, (10, 10))

    def draw_end_screen(self):
        if self.winner:
            message = f"{self.winner.capitalize()} wins!"
        else:
            message = "Stalemate!"
        self.draw_message(message)

        restart_button = pygame.Rect(200, 300, 240, 50)
        quit_button = pygame.Rect(200, 400, 240, 50)

        pygame.draw.rect(self.screen, (0, 255, 0), restart_button)
        pygame.draw.rect(self.screen, (255, 0, 0), quit_button)

        restart_text = self.font.render("Restart", True, (0, 0, 0))
        quit_text = self.font.render("Quit", True, (0, 0, 0))

        self.screen.blit(restart_text, (restart_button.x + 50, restart_button.y + 10))
        self.screen.blit(quit_text, (quit_button.x + 80, quit_button.y + 10))

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.collidepoint(event.pos):
                        self.__init__()
                        return
                    elif quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

    def run(self):
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    col = event.pos[0] // 80
                    row = event.pos[1] // 80
                    if self.selected_piece is None:
                        if self.board.board[row][col] and self.board.board[row][col].color == self.board.current_player:
                            self.selected_piece = (row, col)
                    else:
                        start = self.selected_piece
                        end = (row, col)
                        if self.board.move_piece(start, end):
                            self.selected_piece = None
                            if self.board.is_checkmate('white'):
                                print("Checkmate detected! Black wins.")
                                self.game_over = True
                                self.winner = 'black'
                            elif self.board.is_checkmate('black'):
                                print("Checkmate detected! White wins.")
                                self.game_over = True
                                self.winner = 'white'
                        else:
                            self.selected_piece = None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u:  # التراجع عند الضغط على 'U'
                        self.board.undo_last_move()

            self.screen.fill((255, 255, 255))
            self.draw_board()

            if self.selected_piece:
                row, col = self.selected_piece
                pygame.draw.rect(self.screen, (255, 0, 0), (col * 80, row * 80, 80, 80), 3)

            if self.board.is_in_check(self.board.current_player):
                if self.board.is_checkmate(self.board.current_player):
                    self.draw_message(f"Checkmate! {self.board.current_player} loses.")
                    self.game_over = True
                    self.winner = 'white' if self.board.current_player == 'black' else 'black'
                    print(f"Game Over! {self.winner.capitalize()} wins.")
                else:
                    self.draw_message(f"Check! {self.board.current_player}'s turn")
            else:
                self.draw_message(f"{self.board.current_player}'s turn")

            pygame.display.flip()
            self.clock.tick(60)

        self.draw_end_screen()


if __name__ == "__main__":
    game = ChessGame()
    game.run()
# Create and start the game
chess_board = ChessBoard()
chess_board.play()