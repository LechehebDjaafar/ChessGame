import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import chess
import chess.pgn
import random
import threading
import time
import io

class AdvancedChessGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("لعبة الشطرنج المتقدمة")
        self.window.geometry("900x750")
        self.window.resizable(False, False)
        
        # متغيرات اللعبة
        self.board = chess.Board()
        self.selected_square = None
        self.square_size = 70
        self.flipped = False  # متغير قلب الرقعة
        self.game_mode = "1vs1"  # 1vs1 أو 1vsAI
        self.ai_thinking = False
        self.game_started = False
        
        # إنشاء واجهة البداية
        self.create_start_screen()
        
    def create_start_screen(self):
        """إنشاء واجهة البداية"""
        self.start_frame = tk.Frame(self.window, bg="#2E3440")
        self.start_frame.pack(fill=tk.BOTH, expand=True)
        
        # عنوان اللعبة
        title_label = tk.Label(
            self.start_frame,
            text="🏆 لعبة الشطرنج المتقدمة 🏆",
            font=("Arial", 24, "bold"),
            bg="#2E3440",
            fg="#ECEFF4"
        )
        title_label.pack(pady=50)
        
        # أزرار اختيار وضع اللعب
        mode_frame = tk.Frame(self.start_frame, bg="#2E3440")
        mode_frame.pack(pady=30)
        
        tk.Button(
            mode_frame,
            text="🎮 لاعب ضد لاعب",
            font=("Arial", 16),
            bg="#5E81AC",
            fg="white",
            padx=30,
            pady=15,
            command=lambda: self.start_game("1vs1")
        ).pack(pady=10)
        
        tk.Button(
            mode_frame,
            text="🤖 لاعب ضد الحاسوب",
            font=("Arial", 16),
            bg="#BF616A",
            fg="white",
            padx=30,
            pady=15,
            command=lambda: self.start_game("1vsAI")
        ).pack(pady=10)
        
        # زر رفع مباراة
        tk.Button(
            mode_frame,
            text="📁 رفع مباراة PGN",
            font=("Arial", 16),
            bg="#A3BE8C",
            fg="white",
            padx=30,
            pady=15,
            command=self.load_pgn_game
        ).pack(pady=10)
        
    def start_game(self, mode):
        """بدء اللعبة بالوضع المحدد"""
        self.game_mode = mode
        self.game_started = True
        self.start_frame.destroy()
        self.create_game_interface()
        
    def create_game_interface(self):
        """إنشاء واجهة اللعبة الرئيسية"""
        # الإطار الرئيسي
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # الإطار الجانبي للأدوات
        self.tools_frame = tk.Frame(main_frame, width=200, bg="#D8DEE9")
        self.tools_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        self.tools_frame.pack_propagate(False)
        
        # الإطار الرئيسي للعبة
        game_frame = tk.Frame(main_frame)
        game_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # إنشاء Canvas للرقعة
        self.canvas = tk.Canvas(
            game_frame, 
            width=8 * self.square_size, 
            height=8 * self.square_size,
            bg="white"
        )
        self.canvas.pack(pady=10)
        
        # ربط أحداث الماوس
        self.canvas.bind("<Button-1>", self.on_square_click)
        
        # شريط المعلومات
        self.create_status_bar(game_frame)
        
        # أزرار التحكم
        self.create_control_buttons(game_frame)
        
        # الأدوات الجانبية
        self.create_side_tools()
        
        # رسم الرقعة الأولي
        self.draw_board()
        self.update_status()
        
    def create_status_bar(self, parent):
        """إنشاء شريط المعلومات"""
        self.status_frame = tk.Frame(parent)
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(
            self.status_frame,
            text=f"دور الأبيض - الوضع: {'لاعب ضد لاعب' if self.game_mode == '1vs1' else 'لاعب ضد الحاسوب'}",
            font=("Arial", 12, "bold"),
            bg="#ECEFF4",
            relief=tk.SUNKEN,
            padx=10,
            pady=5
        )
        self.status_label.pack(fill=tk.X)
        
    def create_control_buttons(self, parent):
        """إنشاء أزرار التحكم"""
        self.button_frame = tk.Frame(parent)
        self.button_frame.pack(pady=10)
        
        buttons = [
            ("🔄 لعبة جديدة", self.new_game, "#5E81AC"),
            ("↩️ تراجع", self.undo_move, "#D08770"),
            ("🔄 قلب الرقعة", self.flip_board, "#A3BE8C"),
            ("💾 حفظ PGN", self.save_pgn, "#B48EAD"),
            ("🏠 القائمة الرئيسية", self.return_to_menu, "#BF616A")
        ]
        
        for text, command, color in buttons:
            tk.Button(
                self.button_frame,
                text=text,
                command=command,
                font=("Arial", 10),
                bg=color,
                fg="white",
                padx=15,
                pady=5
            ).pack(side=tk.LEFT, padx=5)
            
    def create_side_tools(self):
        """إنشاء الأدوات الجانبية"""
        # عنوان الأدوات
        tk.Label(
            self.tools_frame,
            text="🛠️ أدوات اللعبة",
            font=("Arial", 14, "bold"),
            bg="#D8DEE9"
        ).pack(pady=10)
        
        # عرض تدوين PGN
        tk.Label(
            self.tools_frame,
            text="📝 تدوين المباراة:",
            font=("Arial", 12, "bold"),
            bg="#D8DEE9"
        ).pack(pady=(20, 5))
        
        self.pgn_text = scrolledtext.ScrolledText(
            self.tools_frame,
            height=15,
            width=25,
            font=("Arial", 10),
            bg="white"
        )
        self.pgn_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # معلومات إضافية
        self.info_label = tk.Label(
            self.tools_frame,
            text="ℹ️ معلومات المباراة:",
            font=("Arial", 12, "bold"),
            bg="#D8DEE9"
        )
        self.info_label.pack(pady=(10, 5))
        
        self.moves_count_label = tk.Label(
            self.tools_frame,
            text="عدد الحركات: 0",
            font=("Arial", 10),
            bg="#D8DEE9"
        )
        self.moves_count_label.pack(pady=2)
        
    def draw_board(self):
        """رسم رقعة الشطرنج والقطع"""
        self.canvas.delete("all")
        
        # رسم المربعات
        for row in range(8):
            for col in range(8):
                # تحديد الإحداثيات حسب اتجاه الرقعة
                if self.flipped:
                    display_row = row
                    display_col = 7 - col
                else:
                    display_row = 7 - row
                    display_col = col
                    
                x1 = display_col * self.square_size
                y1 = display_row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                
                # تحديد لون المربع
                if (row + col) % 2 == 0:
                    color = "#F0D9B5"  # مربعات فاتحة
                else:
                    color = "#B58863"  # مربعات داكنة
                
                # تمييز المربع المحدد
                actual_square = chess.square(col, row)
                if actual_square == self.selected_square:
                    color = "#7FB069"  # أخضر للمربع المحدد
                
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline="black",
                    width=1,
                    tags=f"square_{row}_{col}"
                )
                
        # رسم أسماء المربعات (إحداثيات)
        self.draw_coordinates()
        
        # رسم القطع
        self.draw_pieces()
        
    def draw_coordinates(self):
        """رسم إحداثيات الرقعة"""
        files = "abcdefgh"
        ranks = "12345678"
        
        for i in range(8):
            # الأحرف (الأعمدة)
            if self.flipped:
                file_char = files[7-i]
                x = i * self.square_size + self.square_size // 2
            else:
                file_char = files[i]
                x = i * self.square_size + self.square_size // 2
                
            y = 8 * self.square_size + 15
            
            self.canvas.create_text(
                x, y, text=file_char,
                font=("Arial", 10, "bold"),
                fill="black"
            )
            
            # الأرقام (الصفوف)
            if self.flipped:
                rank_char = ranks[i]
                y = (7-i) * self.square_size + self.square_size // 2
            else:
                rank_char = ranks[7-i]
                y = i * self.square_size + self.square_size // 2
                
            x = -15
            
            self.canvas.create_text(
                x, y, text=rank_char,
                font=("Arial", 10, "bold"),
                fill="black"
            )
        
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
                file = chess.square_file(square)
                rank = chess.square_rank(square)
                
                # تحديد الموقع حسب اتجاه الرقعة
                if self.flipped:
                    display_col = 7 - file
                    display_row = rank
                else:
                    display_col = file
                    display_row = 7 - rank
                
                x = display_col * self.square_size + self.square_size // 2
                y = display_row * self.square_size + self.square_size // 2
                
                symbol = piece_symbols.get(piece.symbol(), piece.symbol())
                color = "black" if piece.color == chess.WHITE else "darkred"
                
                self.canvas.create_text(
                    x, y,
                    text=symbol,
                    font=("Arial", 48),
                    fill=color,
                    tags="piece"
                )
    
    def on_square_click(self, event):
        """التعامل مع النقر على مربع"""
        if self.ai_thinking:
            return
            
        col = event.x // self.square_size
        row = event.y // self.square_size
        
        if 0 <= col < 8 and 0 <= row < 8:
            # تحديد المربع الفعلي حسب اتجاه الرقعة
            if self.flipped:
                actual_col = 7 - col
                actual_row = row
            else:
                actual_col = col
                actual_row = 7 - row
                
            clicked_square = chess.square(actual_col, actual_row)
            
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
                    self.make_move(move)
                
                self.selected_square = None
                
            self.draw_board()
            self.update_status()
            self.update_pgn_display()
    
    def make_move(self, move):
        """تنفيذ حركة والتحقق من حالة اللعبة"""
        self.board.push(move)
        self.check_game_status()
        
        # إذا كان الوضع ضد الحاسوب ودور الحاسوب
        if (self.game_mode == "1vsAI" and 
            self.board.turn == chess.BLACK and 
            not self.board.is_game_over()):
            # تأخير قصير ثم تحريك الحاسوب
            self.window.after(500, self.ai_move)
    
    def ai_move(self):
        """حركة الحاسوب (عشوائية)"""
        self.ai_thinking = True
        self.status_label.config(text="🤔 الحاسوب يفكر...")
        
        def think_and_move():
            time.sleep(random.uniform(0.5, 2.0))  # محاكاة التفكير
            
            if not self.board.is_game_over():
                legal_moves = list(self.board.legal_moves)
                if legal_moves:
                    # اختيار حركة عشوائية
                    ai_move = random.choice(legal_moves)
                    
                    # تنفيذ الحركة في الخيط الرئيسي
                    self.window.after(0, lambda: self.execute_ai_move(ai_move))
        
        # تشغيل التفكير في خيط منفصل
        thread = threading.Thread(target=think_and_move)
        thread.daemon = True
        thread.start()
    
    def execute_ai_move(self, move):
        """تنفيذ حركة الحاسوب"""
        self.board.push(move)
        self.ai_thinking = False
        self.check_game_status()
        self.draw_board()
        self.update_status()
        self.update_pgn_display()
    
    def flip_board(self):
        """قلب اتجاه الرقعة"""
        self.flipped = not self.flipped
        self.draw_board()
    
    def update_status(self):
        """تحديث معلومات حالة اللعبة"""
        if self.ai_thinking:
            return
            
        if self.board.turn:
            turn_text = "دور الأبيض"
        else:
            turn_text = "دور الأسود"
            
        if self.board.is_check():
            turn_text += " - كش! ⚠️"
            
        mode_text = "لاعب ضد لاعب" if self.game_mode == "1vs1" else "لاعب ضد الحاسوب"
        full_text = f"{turn_text} - الوضع: {mode_text}"
        
        self.status_label.config(text=full_text)
        self.moves_count_label.config(text=f"عدد الحركات: {len(self.board.move_stack)}")
    
    def update_pgn_display(self):
        """تحديث عرض تدوين PGN"""
        game = chess.pgn.Game.from_board(self.board)
        pgn_string = str(game)
        
        self.pgn_text.delete(1.0, tk.END)
        self.pgn_text.insert(1.0, pgn_string)
    
    def check_game_status(self):
        """فحص حالة انتهاء اللعبة"""
        if self.board.is_checkmate():
            winner = "الأسود" if self.board.turn else "الأبيض"
            messagebox.showinfo("انتهت اللعبة! 🏆", f"كش مات! فاز {winner}")
        elif self.board.is_stalemate():
            messagebox.showinfo("انتهت اللعبة! 🤝", "تعادل - استنفاد الحركات")
        elif self.board.is_insufficient_material():
            messagebox.showinfo("انتهت اللعبة! 🤝", "تعادل - مواد غير كافية")
        elif self.board.is_seventyfive_moves():
            messagebox.showinfo("انتهت اللعبة! 🤝", "تعادل - قاعدة 75 حركة")
        elif self.board.is_fivefold_repetition():
            messagebox.showinfo("انتهت اللعبة! 🤝", "تعادل - تكرار الوضع")
    
    def new_game(self):
        """بدء لعبة جديدة"""
        self.board = chess.Board()
        self.selected_square = None
        self.ai_thinking = False
        self.draw_board()
        self.update_status()
        self.update_pgn_display()
    
    def undo_move(self):
        """التراجع عن آخر حركة"""
        moves_to_undo = 1
        # في وضع ضد الحاسوب، تراجع عن حركتين (اللاعب والحاسوب)
        if self.game_mode == "1vsAI" and len(self.board.move_stack) >= 2:
            moves_to_undo = 2
            
        for _ in range(moves_to_undo):
            if self.board.move_stack:
                self.board.pop()
                
        self.selected_square = None
        self.ai_thinking = False
        self.draw_board()
        self.update_status()
        self.update_pgn_display()
    
    def save_pgn(self):
        """حفظ المباراة بصيغة PGN"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".pgn",
            filetypes=[("PGN files", "*.pgn"), ("All files", "*.*")],
            title="حفظ المباراة"
        )
        
        if filename:
            try:
                game = chess.pgn.Game.from_board(self.board)
                game.headers["Event"] = "مباراة محلية"
                game.headers["Site"] = "البرنامج"
                game.headers["Date"] = "????.??.??"
                game.headers["Round"] = "1"
                game.headers["White"] = "لاعب 1"
                game.headers["Black"] = "لاعب 2" if self.game_mode == "1vs1" else "الحاسوب"
                
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(str(game))
                    
                messagebox.showinfo("تم الحفظ! ✅", f"تم حفظ المباراة في:\n{filename}")
            except Exception as e:
                messagebox.showerror("خطأ! ❌", f"فشل في حفظ الملف:\n{str(e)}")
    
    def load_pgn_game(self):
        """رفع مباراة من ملف PGN"""
        filename = filedialog.askopenfilename(
            filetypes=[("PGN files", "*.pgn"), ("All files", "*.*")],
            title="اختيار ملف PGN"
        )
        
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    game = chess.pgn.read_game(f)
                    
                if game:
                    # إنشاء رقعة من المباراة
                    self.board = game.board()
                    for move in game.mainline_moves():
                        self.board.push(move)
                    
                    # تحديث الواجهة
                    if hasattr(self, 'start_frame'):
                        self.start_frame.destroy()
                    
                    self.game_mode = "1vs1"  # وضع مشاهدة
                    self.game_started = True
                    self.create_game_interface()
                    
                    messagebox.showinfo("تم التحميل! ✅", 
                                      f"تم تحميل المباراة بنجاح!\n"
                                      f"الحدث: {game.headers.get('Event', 'غير محدد')}\n"
                                      f"الأبيض: {game.headers.get('White', 'غير محدد')}\n"
                                      f"الأسود: {game.headers.get('Black', 'غير محدد')}")
                else:
                    messagebox.showerror("خطأ! ❌", "لم يتم العثور على مباراة صحيحة في الملف")
                    
            except Exception as e:
                messagebox.showerror("خطأ! ❌", f"فشل في قراءة الملف:\n{str(e)}")
    
    def return_to_menu(self):
        """العودة للقائمة الرئيسية"""
        # حذف الواجهة الحالية
        for widget in self.window.winfo_children():
            widget.destroy()
            
        # إعادة تعيين المتغيرات
        self.game_started = False
        self.board = chess.Board()
        self.selected_square = None
        self.ai_thinking = False
        
        # إنشاء واجهة البداية مجدداً
        self.create_start_screen()
    
    def run(self):
        """تشغيل اللعبة"""
        self.window.mainloop()

# تشغيل البرنامج
if __name__ == "__main__":
    game = AdvancedChessGame()
    game.run()
