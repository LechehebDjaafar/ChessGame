import tkinter as tk
from tkinter import messagebox
import chess
import chess.svg

class ChessGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("لعبة الشطرنج")
        self.window.geometry("650x700")
        self.window.resizable(False, False)
        
        # إنشاء رقعة الشطرنج
        self.board = chess.Board()
        
        # متغيرات اللعبة
        self.selected_square = None
        self.square_size = 80
        
        # إنشاء الواجهة
        self.create_widgets()
        self.draw_board()
        self.update_status()
        
    def create_widgets(self):
        # إنشاء Canvas للرقعة
        self.canvas = tk.Canvas(
            self.window, 
            width=8 * self.square_size, 
            height=8 * self.square_size,
            bg="white"
        )
        self.canvas.pack(pady=10)
        
        # ربط النقر بالماوس
        self.canvas.bind("<Button-1>", self.on_square_click)
        
        # شريط المعلومات
        self.status_frame = tk.Frame(self.window)
        self.status_frame.pack(fill=tk.X, padx=10)
        
        self.status_label = tk.Label(
            self.status_frame, 
            text="دور الأبيض", 
            font=("Arial", 12, "bold")
        )
        self.status_label.pack(side=tk.LEFT)
        
        # أزرار التحكم
        self.button_frame = tk.Frame(self.window)
        self.button_frame.pack(pady=10)
        
        tk.Button(
            self.button_frame, 
            text="لعبة جديدة", 
            command=self.new_game,
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            self.button_frame, 
            text="تراجع", 
            command=self.undo_move,
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)
        
    def draw_board(self):
        """رسم رقعة الشطرنج والقطع"""
        self.canvas.delete("all")
        
        # رسم المربعات
        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                
                # تحديد لون المربع
                if (row + col) % 2 == 0:
                    color = "#F0D9B5"  # مربعات فاتحة
                else:
                    color = "#B58863"  # مربعات داكنة
                
                # تمييز المربع المحدد
                square = chess.square(col, 7-row)
                if square == self.selected_square:
                    color = "#7FB069"  # أخضر للمربع المحدد
                
                self.canvas.create_rectangle(
                    x1, y1, x2, y2, 
                    fill=color, 
                    outline="black",
                    tags=f"square_{row}_{col}"
                )
                
        # رسم القطع
        self.draw_pieces()
        
    def draw_pieces(self):
        """رسم قطع الشطرنج على الرقعة"""
        # رموز قطع الشطرنج Unicode
        piece_symbols = {
            'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
            'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
        }
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                row = 7 - chess.square_rank(square)
                col = chess.square_file(square)
                
                x = col * self.square_size + self.square_size // 2
                y = row * self.square_size + self.square_size // 2
                
                symbol = piece_symbols.get(piece.symbol(), piece.symbol())
                
                self.canvas.create_text(
                    x, y, 
                    text=symbol, 
                    font=("Arial", 48), 
                    fill="black" if piece.color else "darkred",
                    tags="piece"
                )
    
    def on_square_click(self, event):
        """التعامل مع النقر على مربع"""
        col = event.x // self.square_size
        row = event.y // self.square_size
        
        if 0 <= col < 8 and 0 <= row < 8:
            clicked_square = chess.square(col, 7-row)
            
            if self.selected_square is None:
                # تحديد قطعة جديدة
                piece = self.board.piece_at(clicked_square)
                if piece and piece.color == self.board.turn:
                    self.selected_square = clicked_square
            else:
                # محاولة تحريك القطعة
                move = chess.Move(self.selected_square, clicked_square)
                
                # التحقق من الترقية للبيدق
                piece = self.board.piece_at(self.selected_square)
                if (piece and piece.piece_type == chess.PAWN and 
                    (chess.square_rank(clicked_square) == 0 or 
                     chess.square_rank(clicked_square) == 7)):
                    move = chess.Move(self.selected_square, clicked_square, 
                                    promotion=chess.QUEEN)
                
                if move in self.board.legal_moves:
                    self.board.push(move)
                    self.check_game_status()
                
                self.selected_square = None
                
            self.draw_board()
            self.update_status()
    
    def update_status(self):
        """تحديث معلومات حالة اللعبة"""
        if self.board.turn:
            turn_text = "دور الأبيض"
        else:
            turn_text = "دور الأسود"
            
        if self.board.is_check():
            turn_text += " - كش!"
            
        self.status_label.config(text=turn_text)
    
    def check_game_status(self):
        """فحص حالة انتهاء اللعبة"""
        if self.board.is_checkmate():
            winner = "الأسود" if self.board.turn else "الأبيض"
            messagebox.showinfo("انتهت اللعبة", f"كش مات! فاز {winner}")
        elif self.board.is_stalemate():
            messagebox.showinfo("انتهت اللعبة", "تعادل - استنفاد الحركات")
        elif self.board.is_insufficient_material():
            messagebox.showinfo("انتهت اللعبة", "تعادل - مواد غير كافية")
        elif self.board.is_seventyfive_moves():
            messagebox.showinfo("انتهت اللعبة", "تعادل - قاعدة 75 حركة")
        elif self.board.is_fivefold_repetition():
            messagebox.showinfo("انتهت اللعبة", "تعادل - تكرار الوضع")
    
    def new_game(self):
        """بدء لعبة جديدة"""
        self.board = chess.Board()
        self.selected_square = None
        self.draw_board()
        self.update_status()
    
    def undo_move(self):
        """التراجع عن آخر حركة"""
        if self.board.move_stack:
            self.board.pop()
            self.selected_square = None
            self.draw_board()
            self.update_status()
    
    def run(self):
        """تشغيل اللعبة"""
        self.window.mainloop()

# تشغيل البرنامج
if __name__ == "__main__":
    game = ChessGame()
    game.run()
