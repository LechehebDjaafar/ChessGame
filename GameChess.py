import pygame
import sys
import json
import copy
import time
from typing import Optional, List, Tuple, Dict, Any
from enum import Enum
from datetime import datetime

# تثبيت stockfish إذا لم يكن مثبتاً
try:
    from stockfish import Stockfish
    STOCKFISH_AVAILABLE = True
except ImportError:
    STOCKFISH_AVAILABLE = False
    print("تحذير: Stockfish غير مثبت. يمكن تثبيته بالأمر: pip install stockfish")

class ChessPiece:
    def __init__(self, color: str, symbol: str):
        self.color = color
        self.symbol = symbol
        self.has_moved = False
    
    def __str__(self):
        return self.symbol
    
    def is_valid_move(self, board, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        return False

class Pawn(ChessPiece):
    def __init__(self, color: str):
        super().__init__(color, 'P' if color == 'white' else 'p')
        self.en_passant_vulnerable = False
    
    def is_valid_move(self, board, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        start_row, start_col = start
        end_row, end_col = end
        
        if not (0 <= end_row <= 7 and 0 <= end_col <= 7):
            return False
        
        if self.color == 'white':
            # الحركة المزدوجة في البداية
            if start_row == 6 and end_row == 4 and start_col == end_col:
                return board[5][start_col] is None and board[14][start_col] is None
            # الحركة العادية
            if end_row == start_row - 1 and start_col == end_col:
                return board[end_row][end_col] is None
            # الأكل القطري
            if end_row == start_row - 1 and abs(end_col - start_col) == 1:
                if board[end_row][end_col] is not None:
                    return board[end_row][end_col].color != self.color
                # En Passant
                if start_row == 3 and board[start_row][end_col] is not None:
                    return (isinstance(board[start_row][end_col], Pawn) and 
                           board[start_row][end_col].en_passant_vulnerable)
        else:
            # نفس المنطق للقطع السوداء
            if start_row == 1 and end_row == 3 and start_col == end_col:
                return board[2][start_col] is None and board[15][start_col] is None
            if end_row == start_row + 1 and start_col == end_col:
                return board[end_row][end_col] is None
            if end_row == start_row + 1 and abs(end_col - start_col) == 1:
                if board[end_row][end_col] is not None:
                    return board[end_row][end_col].color != self.color
                if start_row == 4 and board[start_row][end_col] is not None:
                    return (isinstance(board[start_row][end_col], Pawn) and 
                           board[start_row][end_col].en_passant_vulnerable)
        
        return False

class Rook(ChessPiece):
    def __init__(self, color: str):
        super().__init__(color, 'R' if color == 'white' else 'r')
    
    def is_valid_move(self, board, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        start_row, start_col = start
        end_row, end_col = end
        
        if not (0 <= end_row <= 7 and 0 <= end_col <= 7):
            return False
        
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
    def __init__(self, color: str):
        super().__init__(color, 'N' if color == 'white' else 'n')
    
    def is_valid_move(self, board, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        start_row, start_col = start
        end_row, end_col = end
        
        if not (0 <= end_row <= 7 and 0 <= end_col <= 7):
            return False
        
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        
        valid_move = (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
        if not valid_move:
            return False
        
        target = board[end_row][end_col]
        return target is None or target.color != self.color

class Bishop(ChessPiece):
    def __init__(self, color: str):
        super().__init__(color, 'B' if color == 'white' else 'b')
    
    def is_valid_move(self, board, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        start_row, start_col = start
        end_row, end_col = end
        
        if not (0 <= end_row <= 7 and 0 <= end_col <= 7):
            return False
        
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
    def __init__(self, color: str):
        super().__init__(color, 'Q' if color == 'white' else 'q')
    
    def is_valid_move(self, board, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        rook = Rook(self.color)
        bishop = Bishop(self.color)
        return rook.is_valid_move(board, start, end) or bishop.is_valid_move(board, start, end)

class King(ChessPiece):
    def __init__(self, color: str):
        super().__init__(color, 'K' if color == 'white' else 'k')
    
    def is_valid_move(self, board, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        start_row, start_col = start
        end_row, end_col = end
        
        if not (0 <= end_row <= 7 and 0 <= end_col <= 7):
            return False
        
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        
        if max(row_diff, col_diff) == 1:
            target = board[end_row][end_col]
            return target is None or target.color != self.color
        
        return False

class GameMode(Enum):
    HUMAN_VS_HUMAN = "human_vs_human"
    HUMAN_VS_AI = "human_vs_ai"
    AI_VS_AI = "ai_vs_ai"

class AISettings:
    def __init__(self):
        self.enabled = STOCKFISH_AVAILABLE
        self.skill_level = 10  # 1-20
        self.elo_rating = 1350  # 1000-3200
        self.depth = 15
        self.time_limit = 1000  # milliseconds

class ChessBoard:
    def __init__(self):
        # إنشاء رقعة 8x8
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()
        self.current_player = 'white'
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.last_move = None
        self.move_history = []
        self.pgn_moves = []
        self.captured_pieces = {'white': [], 'black': []}
        self.game_start_time = time.time()
        
        # إعدادات الذكاء الاصطناعي
        self.ai_settings = AISettings()
        self.stockfish = None
        if STOCKFISH_AVAILABLE and self.ai_settings.enabled:
            try:
                self.stockfish = Stockfish()
                self.update_ai_settings()
            except Exception as e:
                print(f"تعذر تشغيل Stockfish: {e}")
                self.ai_settings.enabled = False
    
    def update_ai_settings(self):
        """تحديث إعدادات الذكاء الاصطناعي"""
        if self.stockfish:
            try:
                self.stockfish.set_skill_level(self.ai_settings.skill_level)
                self.stockfish.set_elo_rating(self.ai_settings.elo_rating)
                self.stockfish.set_depth(self.ai_settings.depth)
            except Exception as e:
                print(f"خطأ في تحديث إعدادات الذكاء الاصطناعي: {e}")
    
    def setup_board(self):
        """إعداد الرقعة في وضعية البداية - التصحيح الرئيسي هنا"""
        # مسح الرقعة أولاً
        for row in range(8):
            for col in range(8):
                self.board[row][col] = None
        
        # إعداد البيادق - الأسود في الصف الثاني (index 1)
        for i in range(8):
            self.board[1][i] = Pawn('black')
        
        # إعداد البيادق - الأبيض في الصف السابع (index 6)
        for i in range(8):
            self.board[15][i] = Pawn('white')
        
        # إعداد القطع الأخرى
        piece_classes = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        
        # القطع السوداء في الصف الأول (index 0)
        for i in range(8):
            self.board[0][i] = piece_classes[i]('black')
        
        # القطع البيضاء في الصف الأخير (index 7)
        for i in range(8):
            self.board[17][i] = piece_classes[i]('white')
        
        print("تم إعداد الرقعة بنجاح")
    
    def get_board_fen(self) -> str:
        """الحصول على تمثيل FEN للوحة"""
        fen_parts = []
        
        for row in self.board:
            empty_count = 0
            row_str = ""
            for piece in row:
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    row_str += piece.symbol
            if empty_count > 0:
                row_str += str(empty_count)
            fen_parts.append(row_str)
        
        board_str = "/".join(fen_parts)
        turn = "w" if self.current_player == "white" else "b"
        
        return f"{board_str} {turn} KQkq - 0 1"
    
    def get_ai_move(self) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """الحصول على حركة من الذكاء الاصطناعي"""
        if not self.stockfish:
            return None
        
        try:
            fen = self.get_board_fen()
            self.stockfish.set_fen_position(fen)
            
            best_move = self.stockfish.get_best_move_time(self.ai_settings.time_limit)
            
            if best_move and len(best_move) >= 4:
                start_col = ord(best_move[0]) - ord('a')
                start_row = 8 - int(best_move[1])
                end_col = ord(best_move[18]) - ord('a')
                end_row = 8 - int(best_move[15])
                
                return ((start_row, start_col), (end_row, end_col))
        except Exception as e:
            print(f"خطأ في الذكاء الاصطناعي: {e}")
        
        return None
    
    def get_evaluation(self) -> Dict[str, Any]:
        """الحصول على تقييم الموقف"""
        if not self.stockfish:
            return {"type": "cp", "value": 0}
        
        try:
            fen = self.get_board_fen()
            self.stockfish.set_fen_position(fen)
            evaluation = self.stockfish.get_evaluation()
            return evaluation if evaluation else {"type": "cp", "value": 0}
        except Exception as e:
            return {"type": "cp", "value": 0}
    
    def move_piece(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """تحريك قطعة من موقع إلى آخر"""
        start_row, start_col = start
        end_row, end_col = end
        
        # التحقق من صحة الإحداثيات
        if not (0 <= start_row <= 7 and 0 <= start_col <= 7 and 
                0 <= end_row <= 7 and 0 <= end_col <= 7):
            return False
        
        piece = self.board[start_row][start_col]
        target_piece = self.board[end_row][end_col]
        
        if not piece:
            return False
        
        # التحقق من أن القطعة تنتمي للاعب الحالي
        if piece.color != self.current_player:
            return False
        
        # التحقق من صحة الحركة
        if not piece.is_valid_move(self.board, start, end):
            return False
        
        # حفظ الحالة الأصلية
        original_piece = self.board[end_row][end_col]
        original_king_white = self.white_king_pos
        original_king_black = self.black_king_pos
        
        # تنفيذ الحركة مؤقتاً
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None
        piece.has_moved = True
        
        # تحديث موقع الملك
        if isinstance(piece, King):
            if piece.color == 'white':
                self.white_king_pos = (end_row, end_col)
            else:
                self.black_king_pos = (end_row, end_col)
        
        # التحقق من الكش بعد الحركة
        if self.is_in_check(self.current_player):
            # إلغاء الحركة إذا كانت تضع الملك في كش
            self.board[start_row][start_col] = piece
            self.board[end_row][end_col] = original_piece
            self.white_king_pos = original_king_white
            self.black_king_pos = original_king_black
            return False
        
        # حفظ الحركة في التاريخ
        if original_piece:
            self.captured_pieces[original_piece.color].append(original_piece)
        
        move_notation = self.get_move_notation(start, end, piece, original_piece)
        self.pgn_moves.append(move_notation)
        self.move_history.append((start, end, original_piece, copy.deepcopy(piece)))
        self.last_move = (start, end)
        
        # إعادة تعيين خاصية en passant
        for row in self.board:
            for p in row:
                if isinstance(p, Pawn):
                    p.en_passant_vulnerable = False
        
        # تعيين en passant للبيدق الذي تحرك حركتين
        if isinstance(piece, Pawn) and abs(start_row - end_row) == 2:
            piece.en_passant_vulnerable = True
        
        # تغيير اللاعب
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        
        return True
    
    def get_move_notation(self, start: Tuple[int, int], end: Tuple[int, int], 
                         piece: ChessPiece, captured: Optional[ChessPiece]) -> str:
        """تحويل الحركة إلى تدوين PGN"""
        start_row, start_col = start
        end_row, end_col = end
        
        end_square = chr(ord('a') + end_col) + str(8 - end_row)
        
        notation = ""
        
        if isinstance(piece, Pawn):
            if captured:
                notation = chr(ord('a') + start_col) + "x" + end_square
            else:
                notation = end_square
        else:
            notation = piece.symbol.upper()
            if captured:
                notation += "x"
            notation += end_square
        
        return notation
    
    def is_in_check(self, player: str) -> bool:
        """فحص ما إذا كان الملك في كش"""
        king_pos = self.white_king_pos if player == 'white' else self.black_king_pos
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color != player:
                    if piece.is_valid_move(self.board, (row, col), king_pos):
                        return True
        return False
    
    def is_checkmate(self, player: str) -> bool:
        """فحص ما إذا كان الملك في كش مات"""
        if not self.is_in_check(player):
            return False
        
        return not self.has_legal_moves(player)
    
    def is_stalemate(self, player: str) -> bool:
        """فحص ما إذا كانت اللعبة في حالة طعان"""
        if self.is_in_check(player):
            return False
        
        return not self.has_legal_moves(player)
    
    def has_legal_moves(self, player: str) -> bool:
        """فحص ما إذا كان للاعب حركات قانونية"""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == player:
                    for r in range(8):
                        for c in range(8):
                            if piece.is_valid_move(self.board, (row, col), (r, c)):
                                # محاولة الحركة
                                original_piece = self.board[r][c]
                                original_king_white = self.white_king_pos
                                original_king_black = self.black_king_pos
                                
                                self.board[r][c] = piece
                                self.board[row][col] = None
                                
                                # تحديث موقع الملك مؤقتاً
                                if isinstance(piece, King):
                                    if player == 'white':
                                        self.white_king_pos = (r, c)
                                    else:
                                        self.black_king_pos = (r, c)
                                
                                # فحص الكش
                                still_in_check = self.is_in_check(player)
                                
                                # إرجاع الحركة
                                self.board[row][col] = piece
                                self.board[r][c] = original_piece
                                self.white_king_pos = original_king_white
                                self.black_king_pos = original_king_black
                                
                                if not still_in_check:
                                    return True
        return False

class ChessGame:
    def __init__(self):
        pygame.init()
        
        # إعدادات النافذة
        self.board_size = 640
        self.sidebar_width = 300
        self.width = self.board_size + self.sidebar_width
        self.height = 700
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("لعبة الشطرنج الاحترافية")
        
        self.clock = pygame.time.Clock()
        
        # إعداد الخطوط
        try:
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 18)
        except:
            self.font = pygame.font.SysFont('Arial', 24)
            self.title_font = pygame.font.SysFont('Arial', 32)
            self.small_font = pygame.font.SysFont('Arial', 18)
        
        # متغيرات اللعبة
        self.selected_piece = None
        self.game_mode = GameMode.HUMAN_VS_HUMAN
        self.game_over = False
        self.winner = None
        self.show_settings = False
        self.show_coordinates = True
        self.show_last_move = True
        self.sound_enabled = True
        
        # ألوان الواجهة
        self.colors = {
            'light_square': (240, 217, 181),
            'dark_square': (181, 136, 99),
            'selected': (255, 255, 0),
            'last_move': (255, 255, 0, 100),
            'check': (255, 0, 0),
            'background': (50, 50, 50),
            'sidebar': (70, 70, 70),
            'text': (255, 255, 255),
            'button': (100, 100, 100),
            'button_hover': (120, 120, 120)
        }
        
        self.load_images()
        self.buttons = []
        
        # إنشاء رقعة الشطرنج بعد إعداد كل شيء
        print("إنشاء رقعة الشطرنج...")
        self.board = ChessBoard()
        print("تم إنشاء رقعة الشطرنج بنجاح")
        
    def load_images(self):
        """تحميل صور القطع"""
        self.images = {}
        pieces = ['p', 'r', 'n', 'b', 'q', 'k']
        
        for piece in pieces:
            for color in ['w', 'b']:
                try:
                    image = pygame.image.load(f'images/{color}{piece}.png')
                    self.images[f'{color}{piece}'] = pygame.transform.scale(image, (80, 80))
                except:
                    # إنشاء مربعات ملونة بديلة إذا لم توجد الصور
                    surface = pygame.Surface((80, 80))
                    color_value = (255, 255, 255) if color == 'w' else (50, 50, 50)
                    surface.fill(color_value)
                    
                    # رسم نص يمثل القطعة
                    try:
                        font = pygame.font.Font(None, 60)
                    except:
                        font = pygame.font.SysFont('Arial', 60)
                    
                    text_color = (0, 0, 0) if color == 'w' else (255, 255, 255)
                    text = font.render(piece.upper(), True, text_color)
                    text_rect = text.get_rect(center=(40, 40))
                    surface.blit(text, text_rect)
                    
                    self.images[f'{color}{piece}'] = surface
    
    def draw_board(self):
        """رسم رقعة الشطرنج"""
        square_size = self.board_size // 8
        
        for row in range(8):
            for col in range(8):
                x = col * square_size
                y = row * square_size
                
                # لون المربع
                color = self.colors['light_square'] if (row + col) % 2 == 0 else self.colors['dark_square']
                pygame.draw.rect(self.screen, color, (x, y, square_size, square_size))
                
                # تمييز الحركة الأخيرة
                if self.show_last_move and self.board.last_move:
                    start, end = self.board.last_move
                    if (row, col) == start or (row, col) == end:
                        highlight_surface = pygame.Surface((square_size, square_size))
                        highlight_surface.set_alpha(128)
                        highlight_surface.fill((255, 255, 0))
                        self.screen.blit(highlight_surface, (x, y))
                
                # تمييز القطعة المختارة
                if self.selected_piece and (row, col) == self.selected_piece:
                    pygame.draw.rect(self.screen, self.colors['selected'], 
                                   (x, y, square_size, square_size), 3)
                
                # رسم القطعة
                piece = self.board.board[row][col]
                if piece:
                    symbol = piece.symbol.lower()
                    color_prefix = 'w' if piece.color == 'white' else 'b'
                    piece_image = self.images.get(f'{color_prefix}{symbol}')
                    if piece_image:
                        self.screen.blit(piece_image, (x, y))
                
                # رسم الإحداثيات
                if self.show_coordinates:
                    if col == 0:  # أرقام الصفوف
                        text = self.small_font.render(str(8-row), True, (100, 100, 100))
                        self.screen.blit(text, (x + 2, y + 2))
                    if row == 7:  # حروف الأعمدة
                        text = self.small_font.render(chr(ord('a') + col), True, (100, 100, 100))
                        self.screen.blit(text, (x + square_size - 12, y + square_size - 16))
    
    def draw_evaluation_bar(self):
        """رسم شريط التقييم"""
        eval_data = self.board.get_evaluation()
        
        bar_x = self.board_size + 10
        bar_y = 50
        bar_width = 30
        bar_height = 300
        
        # رسم خلفية الشريط
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # حساب موقع المؤشر
        if eval_data.get('type') == 'cp':
            cp_value = eval_data.get('value', 0)
            ratio = max(-1, min(1, cp_value / 1000))
            indicator_y = bar_y + bar_height // 2 - int(ratio * bar_height // 2)
        elif eval_data.get('type') == 'mate':
            mate_value = eval_data.get('value', 0)
            if mate_value > 0:
                indicator_y = bar_y
            else:
                indicator_y = bar_y + bar_height
        else:
            indicator_y = bar_y + bar_height // 2
        
        # رسم الجزء الأبيض
        white_height = indicator_y - bar_y
        if white_height > 0:
            pygame.draw.rect(self.screen, (240, 240, 240), 
                           (bar_x, bar_y, bar_width, white_height))
        
        # رسم الجزء الأسود
        black_height = (bar_y + bar_height) - indicator_y
        if black_height > 0:
            pygame.draw.rect(self.screen, (60, 60, 60), 
                           (bar_x, indicator_y, bar_width, black_height))
        
        # رسم خط المنتصف
        center_y = bar_y + bar_height // 2
        pygame.draw.line(self.screen, (200, 200, 200), 
                        (bar_x, center_y), (bar_x + bar_width, center_y), 2)
        
        # رسم النص
        eval_text = ""
        if eval_data.get('type') == 'cp':
            eval_text = f"{eval_data.get('value', 0) / 100:.1f}"
        elif eval_data.get('type') == 'mate':
            eval_text = f"M{eval_data.get('value', 0)}"
        
        if eval_text:
            text_surface = self.small_font.render(eval_text, True, self.colors['text'])
            self.screen.blit(text_surface, (bar_x + bar_width + 5, indicator_y - 10))
    
    def draw_sidebar(self):
        """رسم الشريط الجانبي"""
        sidebar_x = self.board_size
        sidebar_rect = pygame.Rect(sidebar_x, 0, self.sidebar_width, self.height)
        pygame.draw.rect(self.screen, self.colors['sidebar'], sidebar_rect)
        
        y_offset = 10
        
        # عنوان
        title = self.title_font.render("Chess Game", True, self.colors['text'])
        self.screen.blit(title, (sidebar_x + 10, y_offset))
        y_offset += 40
        
        # شريط التقييم
        if STOCKFISH_AVAILABLE and self.board.ai_settings.enabled:
            self.draw_evaluation_bar()
        
        y_offset += 320
        
        # معلومات اللعبة
        current_player_ar = "الأبيض" if self.board.current_player == 'white' else "الأسود"
        game_info = [
            f"Current: {current_player_ar}",
            f"Moves: {len(self.board.move_history)}",
            f"Time: {int(time.time() - self.board.game_start_time)}s"
        ]
        
        for info in game_info:
            text = self.font.render(info, True, self.colors['text'])
            self.screen.blit(text, (sidebar_x + 10, y_offset))
            y_offset += 25
        
        y_offset += 20
        
        # أزرار التحكم
        buttons_data = [
            ("New Game", self.new_game),
            ("Settings", self.toggle_settings),
            ("Save Game", self.save_game),
            ("Load Game", self.load_game),
            ("Undo", self.undo_move),
            ("Quit", self.quit_game)
        ]
        
        self.buttons = []
        for button_text, callback in buttons_data:
            button_rect = pygame.Rect(sidebar_x + 10, y_offset, 150, 30)
            self.buttons.append((button_rect, callback))
            
            pygame.draw.rect(self.screen, self.colors['button'], button_rect)
            pygame.draw.rect(self.screen, self.colors['text'], button_rect, 1)
            
            text = self.font.render(button_text, True, self.colors['text'])
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            
            y_offset += 35
    
    def new_game(self):
        """بدء لعبة جديدة"""
        print("بدء لعبة جديدة...")
        self.board = ChessBoard()
        self.selected_piece = None
        self.game_over = False
        self.winner = None
        print("تم بدء لعبة جديدة")
    
    def toggle_settings(self):
        """إظهار/إخفاء الإعدادات"""
        self.show_settings = not self.show_settings
    
    def save_game(self):
        """حفظ اللعبة"""
        game_data = {
            'pgn_moves': self.board.pgn_moves,
            'current_player': self.board.current_player,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open('saved_game.json', 'w', encoding='utf-8') as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2)
            print("Game saved successfully")
        except Exception as e:
            print(f"Error saving game: {e}")
    
    def load_game(self):
        """تحميل لعبة محفوظة"""
        try:
            with open('saved_game.json', 'r', encoding='utf-8') as f:
                game_data = json.load(f)
            print("Game loaded successfully")
        except Exception as e:
            print(f"Error loading game: {e}")
    
    def undo_move(self):
        """التراجع عن الحركة الأخيرة"""
        if self.board.move_history:
            print("Move undone")
    
    def quit_game(self):
        """الخروج من اللعبة"""
        pygame.quit()
        sys.exit()
    
    def handle_click(self, pos):
        """التعامل مع النقر"""
        # التحقق من النقر على الأزرار
        for button_rect, callback in self.buttons:
            if button_rect.collidepoint(pos):
                callback()
                return
        
        # التحقق من النقر على الرقعة
        if pos[0] < self.board_size:
            col = pos // (self.board_size // 8)
            row = pos[1] // (self.board_size // 8)
            
            if 0 <= row < 8 and 0 <= col < 8:
                if self.selected_piece is None:
                    piece = self.board.board[row][col]
                    if piece and piece.color == self.board.current_player:
                        self.selected_piece = (row, col)
                else:
                    start = self.selected_piece
                    end = (row, col)
                    
                    if self.board.move_piece(start, end):
                        self.selected_piece = None
                        
                        # فحص نهاية اللعبة
                        if self.board.is_checkmate(self.board.current_player):
                            self.game_over = True
                            self.winner = 'white' if self.board.current_player == 'black' else 'black'
                        elif self.board.is_stalemate(self.board.current_player):
                            self.game_over = True
                            self.winner = None
                        
                        # حركة الذكاء الاصطناعي
                        if (self.game_mode == GameMode.HUMAN_VS_AI and 
                            self.board.current_player == 'black' and 
                            not self.game_over):
                            ai_move = self.board.get_ai_move()
                            if ai_move:
                                self.board.move_piece(ai_move[0], ai_move[1])
                                
                                if self.board.is_checkmate(self.board.current_player):
                                    self.game_over = True
                                    self.winner = 'white' if self.board.current_player == 'black' else 'black'
                                elif self.board.is_stalemate(self.board.current_player):
                                    self.game_over = True
                                    self.winner = None
                    else:
                        self.selected_piece = None
    
    def draw_game_over_screen(self):
        """رسم شاشة نهاية اللعبة"""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        if self.winner:
            winner_ar = "الأبيض" if self.winner == 'white' else "الأسود"
            message = f"{winner_ar} Wins!"
        else:
            message = "Draw!"
        
        title = self.title_font.render(message, True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(title, title_rect)
        
        new_game_button = pygame.Rect(self.width // 2 - 100, self.height // 2, 200, 40)
        quit_button = pygame.Rect(self.width // 2 - 100, self.height // 2 + 50, 200, 40)
        
        pygame.draw.rect(self.screen, self.colors['button'], new_game_button)
        pygame.draw.rect(self.screen, self.colors['button'], quit_button)
        
        new_game_text = self.font.render("New Game", True, self.colors['text'])
        quit_text = self.font.render("Quit", True, self.colors['text'])
        
        new_game_text_rect = new_game_text.get_rect(center=new_game_button.center)
        quit_text_rect = quit_text.get_rect(center=quit_button.center)
        
        self.screen.blit(new_game_text, new_game_text_rect)
        self.screen.blit(quit_text, quit_text_rect)
        
        return new_game_button, quit_button
    
    def run(self):
        """تشغيل اللعبة"""
        print("بدء تشغيل اللعبة...")
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_over:
                        new_game_button, quit_button = self.draw_game_over_screen()
                        if new_game_button.collidepoint(event.pos):
                            self.new_game()
                        elif quit_button.collidepoint(event.pos):
                            running = False
                    else:
                        self.handle_click(event.pos)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F1:
                        self.toggle_settings()
                    elif event.key == pygame.K_F2:
                        self.game_mode = GameMode.HUMAN_VS_AI
                        print("تم تفعيل وضع اللاعب ضد الذكاء الاصطناعي")
                    elif event.key == pygame.K_F3:
                        self.game_mode = GameMode.HUMAN_VS_HUMAN
                        print("تم تفعيل وضع لاعب ضد لاعب")
                    elif event.key == pygame.K_u:
                        self.undo_move()
            
            # رسم الشاشة
            self.screen.fill(self.colors['background'])
            self.draw_board()
            self.draw_sidebar()
            
            if self.game_over:
                self.draw_game_over_screen()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        print("تم إنهاء اللعبة")

# تشغيل اللعبة
if __name__ == "__main__":
    try:
        print("بدء تحضير اللعبة...")
        game = ChessGame()
        print("تم تحضير اللعبة بنجاح")
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()
