import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import chess
import chess.pgn
import random
import threading
import time
import io
from PIL import Image, ImageTk, ImageEnhance
import os

class ProfessionalChessGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("♔ لعبة الشطرنج الاحترافية ♔")
        self.window.geometry("1000x800")
        self.window.resizable(False, False)
        self.window.configure(bg="#2E3440")
        
        # متغيرات اللعبة
        self.board = chess.Board()
        self.selected_square = None
        self.square_size = 80
        self.flipped = False
        self.game_mode = "1vs1"
        self.ai_thinking = False
        self.game_started = False
        self.game_result = None
        self.paused = False
        
        # متغيرات التنقل في التاريخ
        self.move_history = []  # تاريخ كامل للحركات
        self.current_position = 0  # الموقع الحالي في التاريخ
        self.in_review_mode = False  # وضع مراجعة المباراة
        
        # متغيرات عرض الحركات القانونية
        self.show_legal_moves = True
        self.highlight_last_move = True
        self.last_move = None
        
        # متغيرات الواجهة
        self.status_label = None
        self.canvas = None
        self.moves_count_label = None
        self.game_status_label = None
        self.board_orientation_label = None
        self.pgn_text = None
        self.position_label = None
        
        # متغيرات الصور
        self.piece_images = {}
        self.shadow_images = {}
        
        # تحديد مسار مجلد الصور
        self.images_path = "images"
        
        # تحميل صور القطع
        self.load_local_piece_images()
        
        # إنشاء واجهة البداية
        self.create_start_screen()
        
    def create_main_menu(self):
        """إنشاء شريط القوائم الرئيسي"""
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # قائمة اللعبة
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🎮 اللعبة", menu=game_menu)
        game_menu.add_command(label="🔄 لعبة جديدة", command=self.new_game, accelerator="Ctrl+N")
        game_menu.add_command(label="⏸️ إيقاف/استئناف", command=self.toggle_pause, accelerator="Space")
        game_menu.add_separator()
        game_menu.add_command(label="🏳️ استسلام", command=self.resign_game)
        game_menu.add_command(label="⏹️ إلغاء المباراة", command=self.cancel_game)
        game_menu.add_separator()
        game_menu.add_command(label="🏠 القائمة الرئيسية", command=self.return_to_menu)
        game_menu.add_command(label="❌ خروج", command=self.quit_application, accelerator="Alt+F4")
        
        # قائمة التحكم
        control_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🎯 التحكم", menu=control_menu)
        control_menu.add_command(label="↩️ تراجع", command=self.undo_move, accelerator="Ctrl+Z")
        control_menu.add_command(label="🔄 قلب الرقعة", command=self.flip_board_enhanced, accelerator="Ctrl+F")
        control_menu.add_separator()
        control_menu.add_command(label="💡 إظهار الحركات القانونية", command=self.toggle_show_moves)
        control_menu.add_command(label="🎯 تمييز آخر حركة", command=self.toggle_highlight_last_move)
        
        # قائمة التنقل (جديدة)
        navigation_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="⏭️ التنقل", menu=navigation_menu)
        navigation_menu.add_command(label="⏪ البداية", command=self.go_to_start, accelerator="Home")
        navigation_menu.add_command(label="◀️ السابق", command=self.go_previous, accelerator="Left")
        navigation_menu.add_command(label="▶️ التالي", command=self.go_next, accelerator="Right")
        navigation_menu.add_command(label="⏩ النهاية", command=self.go_to_end, accelerator="End")
        navigation_menu.add_separator()
        navigation_menu.add_command(label="🔄 وضع المراجعة", command=self.toggle_review_mode)
        
        # قائمة الملف
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 ملف", menu=file_menu)
        file_menu.add_command(label="📂 فتح PGN", command=self.load_pgn_game, accelerator="Ctrl+O")
        file_menu.add_command(label="💾 حفظ PGN", command=self.save_pgn, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="📊 إحصائيات المباراة", command=self.show_game_stats)
        file_menu.add_command(label="📋 نسخ PGN", command=self.copy_pgn_to_clipboard)
        
        # قائمة الإعدادات
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="⚙️ إعدادات", menu=settings_menu)
        settings_menu.add_command(label="🎨 إعدادات الرقعة", command=self.show_board_settings)
        settings_menu.add_command(label="🖼️ إعدادات الصور", command=self.show_image_settings)
        settings_menu.add_command(label="🎵 إعدادات الصوت", command=self.show_sound_settings)
        
        # قائمة المساعدة
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ مساعدة", menu=help_menu)
        help_menu.add_command(label="📖 قواعد الشطرنج", command=self.show_chess_rules)
        help_menu.add_command(label="🎯 حركات القطع", command=self.show_piece_moves)
        help_menu.add_command(label="⌨️ اختصارات لوحة المفاتيح", command=self.show_keyboard_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ حول البرنامج", command=self.show_about)
        
        # ربط اختصارات لوحة المفاتيح
        self.bind_keyboard_shortcuts()

    def bind_keyboard_shortcuts(self):
        """ربط اختصارات لوحة المفاتيح"""
        self.window.bind('<Control-n>', lambda e: self.new_game())
        self.window.bind('<Control-z>', lambda e: self.undo_move())
        self.window.bind('<Control-f>', lambda e: self.flip_board_enhanced())
        self.window.bind('<Control-o>', lambda e: self.load_pgn_game())
        self.window.bind('<Control-s>', lambda e: self.save_pgn())
        self.window.bind('<space>', lambda e: self.toggle_pause())
        self.window.bind('<F1>', lambda e: self.show_chess_rules())
        self.window.bind('<Escape>', lambda e: self.return_to_menu())
        
        # اختصارات التنقل في تاريخ المباراة
        self.window.bind('<Left>', lambda e: self.go_previous())
        self.window.bind('<Right>', lambda e: self.go_next())
        self.window.bind('<Home>', lambda e: self.go_to_start())
        self.window.bind('<End>', lambda e: self.go_to_end())
        
        # التركيز على النافذة
        self.window.focus_set()

    # ================ دوال التنقل في تاريخ المباراة ================

    def save_move_to_history(self, move):
        """حفظ الحركة في التاريخ"""
        if not self.in_review_mode:
            # إضافة الحركة الجديدة إلى التاريخ
            self.move_history.append({
                'move': move,
                'board_state': self.board.copy(),
                'move_number': len(self.move_history) + 1
            })
            self.current_position = len(self.move_history)
            self.last_move = move

    def go_to_start(self):
        """الذهاب إلى بداية المباراة"""
        if not self.move_history:
            return
            
        self.current_position = 0
        self.board = chess.Board()  # رقعة فارغة
        self.last_move = None
        self.in_review_mode = True
        self.update_board_display()

    def go_previous(self):
        """الحركة السابقة"""
        if self.current_position > 0:
            self.current_position -= 1
            self.update_position_from_history()

    def go_next(self):
        """الحركة التالية"""
        if self.current_position < len(self.move_history):
            self.current_position += 1
            self.update_position_from_history()

    def go_to_end(self):
        """الذهاب إلى نهاية المباراة"""
        if not self.move_history:
            return
            
        self.current_position = len(self.move_history)
        self.update_position_from_history()
        self.in_review_mode = False  # العودة لوضع اللعب العادي

    def update_position_from_history(self):
        """تحديث موقع الرقعة من التاريخ"""
        if self.current_position == 0:
            self.board = chess.Board()
            self.last_move = None
        else:
            # إعادة بناء الرقعة حتى الموقع المحدد
            self.board = chess.Board()
            for i in range(self.current_position):
                if i < len(self.move_history):
                    self.board.push(self.move_history[i]['move'])
                    if i == self.current_position - 1:
                        self.last_move = self.move_history[i]['move']
        
        self.in_review_mode = (self.current_position < len(self.move_history))
        self.update_board_display()

    def update_board_display(self):
        """تحديث عرض الرقعة"""
        if self.canvas:
            self.draw_enhanced_board()
        self.update_status()
        self.update_pgn_display()

    def toggle_review_mode(self):
        """تبديل وضع المراجعة"""
        if self.in_review_mode:
            self.go_to_end()  # العودة لنهاية المباراة
        else:
            self.in_review_mode = True
        
        message = "تم تفعيل وضع المراجعة" if self.in_review_mode else "تم إلغاء وضع المراجعة"
        messagebox.showinfo("🔄 وضع المراجعة", f"🎯 {message}\n\nاستخدم الأسهم للتنقل في تاريخ المباراة!")

    # ================ دوال عرض الحركات القانونية ================

    def toggle_show_moves(self):
        """تبديل إظهار الحركات القانونية"""
        self.show_legal_moves = not self.show_legal_moves
        if self.canvas:
            self.draw_enhanced_board()
        
        status = "تم تفعيل" if self.show_legal_moves else "تم إلغاء"
        messagebox.showinfo("💡 الحركات القانونية", f"{status} عرض الحركات القانونية!")

    def toggle_highlight_last_move(self):
        """تبديل تمييز آخر حركة"""
        self.highlight_last_move = not self.highlight_last_move
        if self.canvas:
            self.draw_enhanced_board()
        
        status = "تم تفعيل" if self.highlight_last_move else "تم إلغاء"
        messagebox.showinfo("🎯 تمييز الحركة", f"{status} تمييز آخر حركة!")

    def get_legal_moves_for_square(self, square):
        """الحصول على الحركات القانونية لمربع معين"""
        legal_moves = []
        for move in self.board.legal_moves:
            if move.from_square == square:
                legal_moves.append(move.to_square)
        return legal_moves

    def show_piece_moves(self):
        """عرض نافذة حركات القطع"""
        moves_window = tk.Toplevel(self.window)
        moves_window.title("🎯 حركات قطع الشطرنج")
        moves_window.geometry("700x600")
        moves_window.configure(bg="#3B4252")
        
        moves_text = scrolledtext.ScrolledText(
            moves_window,
            bg="#434C5E", fg="#ECEFF4",
            font=("Arial", 11),
            wrap=tk.WORD
        )
        moves_text.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        moves_content = """
🎯 حركات قطع الشطرنج التفصيلية:

♔ الملك (King):
• يتحرك مربعاً واحداً في أي اتجاه (أفقي، عمودي، قطري)
• هو أهم قطعة - لا يمكن أسره، وإذا تعرض للتهديد فهذا "كش"
• له حركة خاصة تسمى "التبييت" مع الرخ
• القيمة: لا تُقدر (أهم من كل شيء)

♕ الملكة/الوزير (Queen):
• تجمع حركات الرخ والفيل معاً
• تتحرك أفقياً وعمودياً وقطرياً لأي عدد من المربعات
• أقوى قطعة على الرقعة
• القيمة: 9 نقاط

♖ الرخ/القلعة (Rook):
• يتحرك أفقياً وعمودياً لأي عدد من المربعات
• لا يستطيع القفز فوق القطع الأخرى
• له حركة خاصة تسمى "التبييت" مع الملك
• القيمة: 5 نقاط

♗ الفيل (Bishop):
• يتحرك قطرياً فقط لأي عدد من المربعات
• لا يستطيع القفز فوق القطع الأخرى
• فيل المربعات البيضاء يبقى على البيضاء دائماً
• فيل المربعات السوداء يبقى على السوداء دائماً
• القيمة: 3 نقاط

♘ الحصان (Knight):
• يتحرك على شكل حرف "L"
• مربعين في اتجاه ثم مربع واحد عمودياً عليه
• القطعة الوحيدة التي تستطيع القفز فوق القطع الأخرى
• دائماً ينتقل من مربع أبيض إلى أسود أو العكس
• القيمة: 3 نقاط

♙ البيدق (Pawn):
• يتحرك للأمام مربعاً واحداً فقط
• في أول حركة له يمكن أن يتحرك مربعين
• يأسر قطرياً (ليس للأمام)
• له حركات خاصة: "الأسر بالمرور" و "الترقية"
• عند وصوله للصف الأخير يترقى لأي قطعة (عادة ملكة)
• القيمة: 1 نقطة

🎮 حركات خاصة:

🏰 التبييت (Castling):
• حركة خاصة بين الملك والرخ
• الملك يتحرك مربعين نحو الرخ
• الرخ ينتقل للجانب الآخر من الملك
• شروط: لم يتحرك الملك أو الرخ من قبل، المربعات بينهما فارغة

👻 الأسر بالمرور (En Passant):
• حركة خاصة للبيدق
• عندما يتحرك بيدق الخصم مربعين ويصبح بجانب بيدقك
• يمكن أسره كأنه تحرك مربعاً واحداً فقط

⬆️ ترقية البيدق (Pawn Promotion):
• عندما يصل البيدق للصف الأخير
• يجب ترقيته لقطعة أخرى (ملكة، رخ، فيل، أو حصان)
• عادة يُرقى إلى ملكة لأنها الأقوى

💡 نصائح مهمة:
• لا يمكن تحريك قطعة إذا كان سيعرض ملكك للخطر
• إذا كان ملكك في "كش" يجب إزالة التهديد فوراً
• "كش مات" يعني أن الملك مهدد ولا يمكن إنقاذه
• "تعادل" يحدث عندما لا توجد حركات قانونية والملك ليس في كش
        """
        
        moves_text.insert(1.0, moves_content)
        moves_text.configure(state=tk.DISABLED)

    def toggle_pause(self):
        """تبديل حالة الإيقاف المؤقت"""
        if not self.game_started or self.game_result is not None or self.status_label is None:
            return
            
        self.paused = not self.paused
        
        if self.paused:
            self.ai_thinking = False
            self.status_label.config(
                text="⏸️ المباراة متوقفة مؤقتاً - اضغط Space للاستئناف",
                fg="#9B59B6"
            )
            if self.canvas:
                self.canvas.create_rectangle(
                    0, 0, self.canvas.winfo_reqwidth(), self.canvas.winfo_reqheight(),
                    fill="black", stipple="gray50", tags="pause_overlay"
                )
        else:
            if self.canvas:
                self.canvas.delete("pause_overlay")
            self.update_status()

    def show_game_stats(self):
        """عرض إحصائيات المباراة"""
        if not self.game_started:
            messagebox.showinfo("⚠️ تنبيه", "لا توجد مباراة جارية!")
            return
            
        stats_window = tk.Toplevel(self.window)
        stats_window.title("📊 إحصائيات المباراة")
        stats_window.geometry("400x350")
        stats_window.configure(bg="#3B4252")
        
        move_count = len(self.move_history)
        white_moves = (move_count + 1) // 2
        black_moves = move_count // 2
        
        # حساب القطع المأسورة
        captured_pieces = self.get_captured_pieces_detailed()
        
        stats_text = f"""
📊 إحصائيات المباراة الحالية:

🎮 وضع اللعب: {'لاعب ضد لاعب' if self.game_mode == '1vs1' else 'لاعب ضد الحاسوب'}

📈 عدد الحركات الإجمالي: {move_count}
⚪ حركات الأبيض: {white_moves}
⚫ حركات الأسود: {black_moves}

🎯 الحالة الحالية: {'جارية' if self.game_result is None else self.game_result}
👤 دور اللعب: {'الأبيض' if self.board.turn else 'الأسود'}

⚠️ كش: {'نعم' if self.board.is_check() else 'لا'}
🔄 الرقعة مقلوبة: {'نعم' if self.flipped else 'لا'}

📍 موقع المراجعة: {self.current_position}/{len(self.move_history)}
🔍 وضع المراجعة: {'مفعل' if self.in_review_mode else 'معطل'}

{captured_pieces}
"""

        tk.Label(
            stats_window,
            text=stats_text,
            font=("Arial", 11),
            bg="#3B4252",
            fg="#ECEFF4",
            justify=tk.LEFT
        ).pack(padx=20, pady=20)

    def get_captured_pieces_detailed(self):
        """حساب القطع المأسورة بالتفصيل"""
        initial_pieces = {
            chess.PAWN: 8, chess.ROOK: 2, chess.KNIGHT: 2,
            chess.BISHOP: 2, chess.QUEEN: 1, chess.KING: 1
        }
        
        current_white = {piece_type: 0 for piece_type in initial_pieces}
        current_black = {piece_type: 0 for piece_type in initial_pieces}
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                if piece.color == chess.WHITE:
                    current_white[piece.piece_type] += 1
                else:
                    current_black[piece.piece_type] += 1
        
        piece_names = {
            chess.PAWN: "بيدق", chess.ROOK: "رخ", chess.KNIGHT: "حصان",
            chess.BISHOP: "فيل", chess.QUEEN: "ملكة", chess.KING: "ملك"
        }
        
        captured_white = []
        captured_black = []
        
        for piece_type in initial_pieces:
            white_lost = initial_pieces[piece_type] - current_white[piece_type]
            black_lost = initial_pieces[piece_type] - current_black[piece_type]
            
            if white_lost > 0:
                captured_white.extend([piece_names[piece_type]] * white_lost)
            if black_lost > 0:
                captured_black.extend([piece_names[piece_type]] * black_lost)
        
        result = "🏴 القطع المأسورة:\n"
        if captured_white:
            result += f"⚪ أبيض: {', '.join(captured_white)}\n"
        if captured_black:
            result += f"⚫ أسود: {', '.join(captured_black)}\n"
        if not captured_white and not captured_black:
            result += "لا توجد قطع مأسورة حتى الآن"
            
        return result

    def copy_pgn_to_clipboard(self):
        """نسخ PGN إلى الحافظة"""
        if self.pgn_text is None:
            messagebox.showwarning("⚠️ تحذير", "لا توجد مباراة لنسخها!")
            return
            
        try:
            pgn_content = self.pgn_text.get(1.0, tk.END).strip()
            self.window.clipboard_clear()
            self.window.clipboard_append(pgn_content)
            messagebox.showinfo("✅ تم النسخ", "تم نسخ PGN إلى الحافظة!")
        except Exception as e:
            messagebox.showerror("❌ خطأ", f"فشل في النسخ: {str(e)}")

    def show_board_settings(self):
        """إعدادات الرقعة المتقدمة"""
        settings_window = tk.Toplevel(self.window)
        settings_window.title("🎨 إعدادات الرقعة")
        settings_window.geometry("500x450")
        settings_window.configure(bg="#3B4252")
        
        # حجم الرقعة
        size_frame = tk.LabelFrame(settings_window, text="📏 حجم الرقعة", bg="#3B4252", fg="#88C0D0")
        size_frame.pack(padx=20, pady=10, fill=tk.X)
        
        size_var = tk.IntVar(value=self.square_size)
        tk.Scale(
            size_frame,
            from_=60, to=120,
            orient=tk.HORIZONTAL,
            variable=size_var,
            label="حجم المربع",
            bg="#434C5E", fg="#ECEFF4"
        ).pack(padx=10, pady=10, fill=tk.X)
        
        # إعدادات العرض
        display_frame = tk.LabelFrame(settings_window, text="👁️ إعدادات العرض", bg="#3B4252", fg="#88C0D0")
        display_frame.pack(padx=20, pady=10, fill=tk.X)
        
        show_moves_var = tk.BooleanVar(value=self.show_legal_moves)
        tk.Checkbutton(
            display_frame, text="إظهار الحركات القانونية",
            variable=show_moves_var, bg="#3B4252", fg="#ECEFF4",
            selectcolor="#434C5E"
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        highlight_move_var = tk.BooleanVar(value=self.highlight_last_move)
        tk.Checkbutton(
            display_frame, text="تمييز آخر حركة",
            variable=highlight_move_var, bg="#3B4252", fg="#ECEFF4",
            selectcolor="#434C5E"
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        # أزرار التحكم
        btn_frame = tk.Frame(settings_window, bg="#3B4252")
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame, text="✅ تطبيق",
            bg="#A3BE8C", fg="white",
            command=lambda: self.apply_display_settings(
                size_var.get(), show_moves_var.get(), 
                highlight_move_var.get(), settings_window
            )
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame, text="❌ إلغاء",
            bg="#BF616A", fg="white",
            command=settings_window.destroy
        ).pack(side=tk.LEFT, padx=10)

    def apply_display_settings(self, new_size, show_moves, highlight_move, window):
        """تطبيق إعدادات العرض"""
        settings_changed = False
        
        if new_size != self.square_size:
            self.square_size = new_size
            self.load_local_piece_images()
            settings_changed = True
            
        if show_moves != self.show_legal_moves:
            self.show_legal_moves = show_moves
            settings_changed = True
            
        if highlight_move != self.highlight_last_move:
            self.highlight_last_move = highlight_move
            settings_changed = True
            
        if settings_changed and self.canvas:
            if new_size != 80:  # إذا تغير الحجم
                self.canvas.configure(
                    width=8 * self.square_size + 40,
                    height=8 * self.square_size + 40
                )
            self.draw_enhanced_board()
        
        window.destroy()
        messagebox.showinfo("✅ تم التطبيق", "تم تطبيق الإعدادات بنجاح!")

    def show_image_settings(self):
        """إعدادات الصور"""
        settings_window = tk.Toplevel(self.window)
        settings_window.title("🖼️ إعدادات الصور")
        settings_window.geometry("400x300")
        settings_window.configure(bg="#3B4252")
        
        tk.Label(
            settings_window,
            text="🖼️ إعدادات الصور",
            font=("Arial", 16, "bold"),
            bg="#3B4252", fg="#ECEFF4"
        ).pack(pady=20)
        
        tk.Button(
            settings_window,
            text="🔄 إعادة تحميل الصور",
            bg="#D08770", fg="white",
            command=self.reload_images
        ).pack(pady=10)
        
        tk.Button(
            settings_window,
            text="📁 تغيير مجلد الصور",
            bg="#5E81AC", fg="white",
            command=self.change_images_folder
        ).pack(pady=10)

    def show_sound_settings(self):
        """إعدادات الصوت"""
        messagebox.showinfo("🎵 إعدادات الصوت", "إعدادات الصوت قيد التطوير!")

    def show_chess_rules(self):
        """عرض قواعد الشطرنج"""
        rules_window = tk.Toplevel(self.window)
        rules_window.title("📖 قواعد الشطرنج")
        rules_window.geometry("600x500")
        rules_window.configure(bg="#3B4252")
        
        rules_text = scrolledtext.ScrolledText(
            rules_window,
            bg="#434C5E", fg="#ECEFF4",
            font=("Arial", 11),
            wrap=tk.WORD
        )
        rules_text.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        rules_content = """
📖 قواعد الشطرنج الأساسية:

🎯 الهدف:
- الهدف من اللعبة هو وضع ملك الخصم في حالة "كش مات"
- "كش مات" يعني أن الملك مهدد ولا يمكن إنقاذه

🎮 بداية اللعبة:
- يبدأ اللاعب الأبيض دائماً
- يتناوب اللاعبان في تحريك قطعة واحدة في كل دور

🏆 انتهاء اللعبة:
- كش مات: الملك مهدد ولا يمكن إنقاذه
- تعادل: عدة أسباب منها استنفاد الحركات
- استسلام: أحد اللاعبين يستسلم

⚖️ أسباب التعادل:
- استنفاد الحركات (stalemate)
- تكرار الوضع 3 مرات
- قاعدة 50 حركة بدون أسر أو تحريك بيدق
- عدم كفاية القطع للكش مات
- اتفاق الطرفين على التعادل

🎯 قوانين مهمة:
- لا يمكن ترك الملك في وضع كش
- إذا كان الملك في كش يجب إزالة التهديد فوراً
- لا يمكن تحريك قطعة إذا كان سيعرض الملك للخطر
- بعض الحركات لها قوانين خاصة (التبييت، الأسر بالمرور، الترقية)
        """
        
        rules_text.insert(1.0, rules_content)
        rules_text.configure(state=tk.DISABLED)

    def show_keyboard_shortcuts(self):
        """عرض اختصارات لوحة المفاتيح"""
        shortcuts_window = tk.Toplevel(self.window)
        shortcuts_window.title("⌨️ اختصارات لوحة المفاتيح")
        shortcuts_window.geometry("500x450")
        shortcuts_window.configure(bg="#3B4252")
        
        shortcuts_text = """
⌨️ اختصارات لوحة المفاتيح:

🎮 التحكم في اللعبة:
Ctrl + N        لعبة جديدة
Space           إيقاف مؤقت / استئناف
Ctrl + Z        تراجع عن الحركة
Ctrl + F        قلب الرقعة
Esc             العودة للقائمة الرئيسية

📁 الملفات:
Ctrl + O        فتح ملف PGN
Ctrl + S        حفظ ملف PGN

⏭️ التنقل في تاريخ المباراة:
←              الحركة السابقة
→              الحركة التالية
Home           بداية المباراة
End            نهاية المباراة

❓ المساعدة:
F1              قواعد الشطرنج

🔧 أخرى:
Alt + F4        خروج من البرنامج

💡 نصيحة: في وضع المراجعة يمكنك استخدام الأسهم للتنقل عبر تاريخ المباراة!
        """
        
        tk.Label(
            shortcuts_window,
            text=shortcuts_text,
            font=("Consolas", 11),
            bg="#3B4252", fg="#ECEFF4",
            justify=tk.LEFT
        ).pack(padx=20, pady=20)

    def show_about(self):
        """عرض معلومات البرنامج"""
        messagebox.showinfo(
            "ℹ️ حول البرنامج",
            "♔ لعبة الشطرنج الاحترافية ♛\n\n"
            "🔧 تطوير: مساعد الذكي الاصطناعي\n"
            "📅 الإصدار: 3.0 المتقدم\n"
            "🐍 Python + Tkinter + python-chess\n\n"
            "✨ مميزات جديدة:\n"
            "• عرض الحركات القانونية\n"
            "• التنقل في تاريخ المباراة\n"
            "• وضع المراجعة المتقدم\n"
            "• واجهة احترافية\n"
            "• دعم PGN كامل\n"
            "• تحكم متقدم\n\n"
            "🎯 استمتع باللعب!"
        )

    def quit_application(self):
        """خروج من التطبيق مع تأكيد"""
        if len(self.move_history) > 0 and self.game_result is None:
            result = messagebox.askyesnocancel(
                "❌ تأكيد الخروج",
                "هل تريد حفظ المباراة الحالية قبل الخروج؟"
            )
            if result is True:
                if self.save_pgn():
                    self.window.quit()
            elif result is False:
                self.window.quit()
        else:
            self.window.quit()

    def change_images_folder(self):
        """تغيير مجلد الصور"""
        new_folder = filedialog.askdirectory(title="اختر مجلد الصور الجديد")
        if new_folder:
            self.images_path = new_folder
            self.load_local_piece_images()
            if self.game_started and self.canvas:
                self.draw_enhanced_board()
            messagebox.showinfo("✅ تم التغيير", f"تم تغيير مجلد الصور إلى:\n{new_folder}")

    def load_local_piece_images(self):
        """تحميل صور قطع الشطرنج من مجلد images المحلي"""
        piece_files = {
            'wK': 'wK.png',    'wQ': 'wQ.png',    'wR': 'wR.png',
            'wB': 'wB.png',    'wN': 'wN.png',    'wP': 'wP.png',
            'bK': 'bk.png',    'bQ': 'bq.png',    'bR': 'br.png',
            'bB': 'bb.png',    'bN': 'bn.png',    'bP': 'bp.png'
        }
        
        print(f"البحث عن الصور في المجلد: {self.images_path}")
        
        if not os.path.exists(self.images_path):
            messagebox.showerror(
                "خطأ في الصور", 
                f"لم يتم العثور على مجلد الصور: {self.images_path}"
            )
            self.use_text_pieces()
            return
            
        loaded_count = 0
        for piece_code, filename in piece_files.items():
            file_path = os.path.join(self.images_path, filename)
            
            if os.path.exists(file_path):
                try:
                    img = Image.open(file_path)
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    img = img.resize((self.square_size - 10, self.square_size - 10), Image.Resampling.LANCZOS)
                    self.piece_images[piece_code] = ImageTk.PhotoImage(img)
                    
                    shadow_img = self.create_shadow_image(img)
                    if shadow_img:
                        self.shadow_images[piece_code] = ImageTk.PhotoImage(shadow_img)
                    else:
                        self.shadow_images[piece_code] = None
                    
                    loaded_count += 1
                    print(f"✅ تم تحميل: {filename}")
                    
                except Exception as e:
                    print(f"❌ خطأ في تحميل {filename}: {e}")
                    self.piece_images[piece_code] = None
                    self.shadow_images[piece_code] = None
            else:
                print(f"❌ لم يتم العثور على: {file_path}")
                self.piece_images[piece_code] = None
                self.shadow_images[piece_code] = None
        
        print(f"✅ تم تحميل {loaded_count} صورة من أصل {len(piece_files)}")

    def create_shadow_image(self, img):
        """إنشاء صورة الظل بطريقة آمنة"""
        try:
            shadow_img = img.copy()
            enhancer = ImageEnhance.Brightness(shadow_img)
            shadow_img = enhancer.enhance(0.3)
            
            if shadow_img.mode == 'RGBA':
                r, g, b, a = shadow_img.split()
                gray = Image.new('L', r.size, 50)
                alpha_enhancer = ImageEnhance.Brightness(a)
                a = alpha_enhancer.enhance(0.5)
                shadow_img = Image.merge('RGBA', (gray, gray, gray, a))
            
            return shadow_img
            
        except Exception as e:
            print(f"تحذير: فشل في إنشاء الظل - {e}")
            return None

    def use_text_pieces(self):
        """استخدام النصوص كبديل للصور"""
        for piece_code in ['wK', 'wQ', 'wR', 'wB', 'wN', 'wP', 'bK', 'bQ', 'bR', 'bB', 'bN', 'bP']:
            self.piece_images[piece_code] = None
            self.shadow_images[piece_code] = None
            
    def create_start_screen(self):
        """إنشاء واجهة البداية"""
        self.start_frame = tk.Frame(self.window, bg="#2E3440")
        self.start_frame.pack(fill=tk.BOTH, expand=True)
        
        title_frame = tk.Frame(self.start_frame, bg="#2E3440")
        title_frame.pack(pady=40)
        
        title_label = tk.Label(
            title_frame,
            text="♔ لعبة الشطرنج الاحترافية ♛",
            font=("Arial", 28, "bold"),
            bg="#2E3440",
            fg="#ECEFF4",
            relief=tk.RAISED,
            bd=3
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="🎯 تجربة شطرنج احترافية مع رسوميات عالية الجودة والحركات القانونية",
            font=("Arial", 14),
            bg="#2E3440",
            fg="#D8DEE9"
        )
        subtitle_label.pack(pady=10)
        
        button_frame = tk.Frame(self.start_frame, bg="#2E3440")
        button_frame.pack(pady=30)
        
        buttons_config = [
            ("🎮 لاعب ضد لاعب", "#5E81AC", lambda: self.start_game("1vs1")),
            ("🤖 لاعب ضد الحاسوب", "#BF616A", lambda: self.start_game("1vsAI")),
            ("📁 رفع مباراة PGN", "#A3BE8C", self.load_pgn_game),
            ("⚙️ الإعدادات", "#B48EAD", self.show_settings)
        ]
        
        for text, color, command in buttons_config:
            btn = tk.Button(
                button_frame,
                text=text,
                font=("Arial", 16, "bold"),
                bg=color,
                fg="white",
                padx=40,
                pady=15,
                relief=tk.RAISED,
                bd=3,
                command=command
            )
            btn.pack(pady=8)

    def show_settings(self):
        """نافذة الإعدادات الأساسية"""
        settings_window = tk.Toplevel(self.window)
        settings_window.title("⚙️ إعدادات اللعبة")
        settings_window.geometry("400x350")
        settings_window.configure(bg="#3B4252")
        settings_window.resizable(False, False)
        
        tk.Label(
            settings_window,
            text="⚙️ إعدادات اللعبة",
            font=("Arial", 18, "bold"),
            bg="#3B4252",
            fg="#ECEFF4"
        ).pack(pady=20)
        
        size_frame = tk.Frame(settings_window, bg="#3B4252")
        size_frame.pack(pady=10)
        
        tk.Label(
            size_frame,
            text="حجم المربع:",
            font=("Arial", 12),
            bg="#3B4252",
            fg="#D8DEE9"
        ).pack(side=tk.LEFT)
        
        size_var = tk.IntVar(value=self.square_size)
        size_scale = tk.Scale(
            size_frame,
            from_=60,
            to=100,
            orient=tk.HORIZONTAL,
            variable=size_var,
            bg="#434C5E",
            fg="#ECEFF4",
            highlightbackground="#3B4252"
        )
        size_scale.pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            settings_window,
            text="🔄 إعادة تحميل الصور",
            font=("Arial", 12, "bold"),
            bg="#D08770",
            fg="white",
            padx=20,
            pady=10,
            command=self.reload_images
        ).pack(pady=10)
        
        tk.Button(
            settings_window,
            text="✅ تطبيق",
            font=("Arial", 12, "bold"),
            bg="#A3BE8C",
            fg="white",
            padx=20,
            pady=10,
            command=lambda: self.apply_settings(size_var.get(), settings_window)
        ).pack(pady=20)
        
    def reload_images(self):
        """إعادة تحميل الصور"""
        self.load_local_piece_images()
        if self.game_started and self.canvas:
            self.draw_enhanced_board()
        messagebox.showinfo("✅ تم", "تم إعادة تحميل الصور بنجاح!")
        
    def apply_settings(self, new_size, window):
        """تطبيق الإعدادات الجديدة"""
        if new_size != self.square_size:
            self.square_size = new_size
            self.load_local_piece_images()
            if self.game_started and self.canvas:
                self.canvas.configure(
                    width=8 * self.square_size + 40,
                    height=8 * self.square_size + 40
                )
                self.draw_enhanced_board()
        
        window.destroy()
        messagebox.showinfo("✅ تم التطبيق", "تم تطبيق الإعدادات بنجاح!")

    def start_game(self, mode):
        """بدء اللعبة بالوضع المحدد"""
        self.game_mode = mode
        self.game_started = True
        self.game_result = None
        self.paused = False
        self.move_history = []
        self.current_position = 0
        self.in_review_mode = False
        self.last_move = None
        self.start_frame.destroy()
        self.create_game_interface()
        
    def create_game_interface(self):
        """إنشاء واجهة اللعبة المحسنة"""
        # إنشاء شريط القوائم أولاً
        self.create_main_menu()
        
        main_frame = tk.Frame(self.window, bg="#2E3440")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # الإطار الجانبي للأدوات
        self.tools_frame = tk.Frame(main_frame, width=280, bg="#3B4252", relief=tk.RAISED, bd=2)
        self.tools_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))
        self.tools_frame.pack_propagate(False)
        
        # الإطار الرئيسي للعبة
        game_frame = tk.Frame(main_frame, bg="#2E3440")
        game_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # إنشاء Canvas محسن للرقعة
        canvas_frame = tk.Frame(game_frame, bg="#2E3440", relief=tk.SUNKEN, bd=3)
        canvas_frame.pack(pady=15)
        
        self.canvas = tk.Canvas(
            canvas_frame, 
            width=8 * self.square_size + 40,
            height=8 * self.square_size + 40,
            bg="#4C566A",
            highlightthickness=0
        )
        self.canvas.pack(padx=20, pady=20)
        
        # ربط أحداث الماوس
        self.canvas.bind("<Button-1>", self.on_square_click)
        self.canvas.bind("<Motion>", self.on_mouse_motion)
        self.canvas.bind("<Leave>", self.on_mouse_leave)
        
        # شريط المعلومات المحسن
        self.create_enhanced_status_bar(game_frame)
        
        # أزرار التحكم المحسنة
        self.create_enhanced_control_buttons(game_frame)
        
        # الأدوات الجانبية المحسنة
        self.create_enhanced_side_tools()
        
        # رسم الرقعة الأولي
        self.draw_enhanced_board()
        self.update_status()
        
    def create_enhanced_status_bar(self, parent):
        """إنشاء شريط معلومات محسن"""
        status_frame = tk.Frame(parent, bg="#434C5E", relief=tk.RAISED, bd=2)
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text=f"🎯 دور الأبيض - الوضع: {'لاعب ضد لاعب' if self.game_mode == '1vs1' else 'لاعب ضد الحاسوب'}",
            font=("Arial", 14, "bold"),
            bg="#434C5E",
            fg="#ECEFF4",
            padx=15,
            pady=8
        )
        self.status_label.pack()
        
    def create_enhanced_control_buttons(self, parent):
        """إنشاء أزرار تحكم محسنة"""
        button_frame = tk.Frame(parent, bg="#2E3440")
        button_frame.pack(pady=15)
        
        # الصف الأول من الأزرار
        first_row = tk.Frame(button_frame, bg="#2E3440")
        first_row.pack(pady=5)
        
        buttons_row1 = [
            ("🔄", "لعبة جديدة", self.new_game, "#5E81AC"),
            ("↩️", "تراجع", self.undo_move, "#D08770"),
            ("🔄", "قلب الرقعة", self.flip_board_enhanced, "#A3BE8C"),
            ("💾", "حفظ PGN", self.save_pgn, "#B48EAD")
        ]
        
        for icon, text, command, color in buttons_row1:
            self.create_control_button(first_row, icon, text, command, color)
        
        # الصف الثاني من الأزرار
        second_row = tk.Frame(button_frame, bg="#2E3440")
        second_row.pack(pady=5)
        
        buttons_row2 = [
            ("🏳️", "استسلام", self.resign_game, "#E74C3C"),
            ("⏹️", "إلغاء المباراة", self.cancel_game, "#F39C12"),
            ("⏸️", "إيقاف مؤقت", self.toggle_pause, "#9B59B6"),
            ("🏠", "القائمة الرئيسية", self.return_to_menu, "#BF616A")
        ]
        
        for icon, text, command, color in buttons_row2:
            self.create_control_button(second_row, icon, text, command, color)
    
    def create_control_button(self, parent, icon, text, command, color):
        """إنشاء زر تحكم واحد"""
        btn_container = tk.Frame(parent, bg="#2E3440")
        btn_container.pack(side=tk.LEFT, padx=3)
        
        btn = tk.Button(
            btn_container,
            text=f"{icon}\n{text}",
            command=command,
            font=("Arial", 9, "bold"),
            bg=color,
            fg="white",
            padx=10,
            pady=6,
            relief=tk.RAISED,
            bd=3,
            width=7
        )
        btn.pack()

    def flip_board_enhanced(self):
        """قلب الرقعة مع تحسينات بصرية"""
        if self.paused:
            messagebox.showinfo("⚠️ تنبيه", "لا يمكن قلب الرقعة أثناء الإيقاف المؤقت!")
            return
            
        if not self.canvas:
            return
            
        self.flipped = not self.flipped
        
        flip_text = "🔄 تم قلب الرقعة" if self.flipped else "🔄 تم إعادة الرقعة للوضع الطبيعي"
        
        self.draw_enhanced_board()
        
        self.canvas.create_text(
            (8 * self.square_size + 40) // 2,
            (8 * self.square_size + 40) // 2,
            text=flip_text,
            font=("Arial", 16, "bold"),
            fill="#88C0D0",
            tags="flip_message"
        )
        
        self.window.after(1000, lambda: self.canvas.delete("flip_message"))

    def resign_game(self):
        """استسلام أحد اللاعبين"""
        if self.game_result is not None:
            messagebox.showinfo("⚠️ تنبيه", "المباراة انتهت بالفعل!")
            return
            
        current_player = "الأبيض" if self.board.turn else "الأسود"
        winner = "الأسود" if self.board.turn else "الأبيض"
        
        result = messagebox.askyesno(
            "🏳️ تأكيد الاستسلام",
            f"هل أنت متأكد من استسلام {current_player}؟\n\n"
            f"🏆 سيفوز {winner} بالمباراة!"
        )
        
        if result:
            self.game_result = "استسلام"
            self.ai_thinking = False
            
            if self.status_label:
                self.status_label.config(
                    text=f"🏳️ استسلم {current_player} - فاز {winner} 🏆",
                    fg="#E74C3C"
                )
            
            self.update_pgn_with_result("استسلام", winner)
            
            messagebox.showinfo(
                "🏆 انتهت المباراة!",
                f"🏳️ استسلم {current_player}\n\n"
                f"🎉 تهانينا {winner} على الفوز!\n\n"
                f"💡 يمكنك الآن استخدام الأسهم لمراجعة المباراة!"
            )

    def cancel_game(self):
        """إلغاء المباراة الحالية"""
        if not self.move_history and self.game_result is None:
            messagebox.showinfo("⚠️ تنبيه", "لم تبدأ المباراة بعد!")
            return
            
        result = messagebox.askyesno(
            "⏹️ تأكيد الإلغاء",
            "هل أنت متأكد من إلغاء المباراة الحالية؟\n\n"
            "⚠️ ستفقد جميع الحركات إذا لم تحفظ المباراة!"
        )
        
        if result:
            self.game_result = "ملغاة"
            self.ai_thinking = False
            self.paused = False
            
            self.board = chess.Board()
            self.selected_square = None
            self.move_history = []
            self.current_position = 0
            self.in_review_mode = False
            self.last_move = None
            
            if self.canvas:
                self.draw_enhanced_board()
                
            if self.status_label:
                self.status_label.config(
                    text="⏹️ تم إلغاء المباراة - جاهز لبدء مباراة جديدة",
                    fg="#F39C12"
                )
            
            if self.pgn_text:
                self.pgn_text.delete(1.0, tk.END)
                self.pgn_text.insert(1.0, "المباراة ملغاة - لا توجد حركات")
            
            messagebox.showinfo("⏹️ تم الإلغاء", "تم إلغاء المباراة بنجاح!")

    def update_pgn_with_result(self, result_type, winner):
        """تحديث PGN مع نتيجة المباراة"""
        try:
            game = chess.pgn.Game.from_board(self.board)
            game.headers["Event"] = "مباراة احترافية"
            game.headers["Date"] = time.strftime("%Y.%m.%d")
            game.headers["White"] = "اللاعب الأبيض"
            game.headers["Black"] = "اللاعب الأسود" if self.game_mode == "1vs1" else "الحاسوب"
            
            if result_type == "استسلام":
                if winner == "الأبيض":
                    game.headers["Result"] = "1-0"
                else:
                    game.headers["Result"] = "0-1"
            else:
                game.headers["Result"] = "*"
            
            pgn_string = str(game)
            if result_type == "استسلام":
                pgn_string += f"\n\n[النتيجة: {result_type} - فاز {winner}]"
            
            if self.pgn_text:
                self.pgn_text.delete(1.0, tk.END)
                self.pgn_text.insert(1.0, pgn_string)
                
        except Exception as e:
            print(f"خطأ في تحديث PGN: {e}")
            
    def create_enhanced_side_tools(self):
        """إنشاء أدوات جانبية محسنة"""
        header = tk.Label(
            self.tools_frame,
            text="🛠️ لوحة التحكم",
            font=("Arial", 16, "bold"),
            bg="#3B4252",
            fg="#ECEFF4"
        )
        header.pack(pady=15)
        
        # معلومات المباراة
        info_frame = tk.LabelFrame(
            self.tools_frame,
            text="📊 معلومات المباراة",
            font=("Arial", 12, "bold"),
            bg="#3B4252",
            fg="#88C0D0",
            relief=tk.GROOVE,
            bd=2
        )
        info_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.moves_count_label = tk.Label(
            info_frame,
            text="عدد الحركات: 0",
            font=("Arial", 11),
            bg="#3B4252",
            fg="#D8DEE9"
        )
        self.moves_count_label.pack(pady=3)
        
        self.game_status_label = tk.Label(
            info_frame,
            text="الحالة: جارية",
            font=("Arial", 11),
            bg="#3B4252",
            fg="#D8DEE9"
        )
        self.game_status_label.pack(pady=3)
        
        self.board_orientation_label = tk.Label(
            info_frame,
            text="الرقعة: عادية",
            font=("Arial", 11),
            bg="#3B4252",
            fg="#D8DEE9"
        )
        self.board_orientation_label.pack(pady=3)
        
        # معلومات التنقل
        self.position_label = tk.Label(
            info_frame,
            text="الموقع: الحالي",
            font=("Arial", 11),
            bg="#3B4252",
            fg="#D8DEE9"
        )
        self.position_label.pack(pady=3)
        
        # أزرار التنقل
        nav_frame = tk.LabelFrame(
            self.tools_frame,
            text="⏭️ التنقل في التاريخ",
            font=("Arial", 12, "bold"),
            bg="#3B4252",
            fg="#88C0D0",
            relief=tk.GROOVE,
            bd=2
        )
        nav_frame.pack(padx=10, pady=5, fill=tk.X)
        
        nav_buttons_frame = tk.Frame(nav_frame, bg="#3B4252")
        nav_buttons_frame.pack(pady=10)
        
        nav_buttons = [
            ("⏪", self.go_to_start, "البداية"),
            ("◀️", self.go_previous, "السابق"),
            ("▶️", self.go_next, "التالي"),
            ("⏩", self.go_to_end, "النهاية")
        ]
        
        for symbol, command, tooltip in nav_buttons:
            btn = tk.Button(
                nav_buttons_frame,
                text=symbol,
                command=command,
                font=("Arial", 12, "bold"),
                bg="#434C5E",
                fg="#ECEFF4",
                width=3,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # عرض تدوين PGN
        pgn_frame = tk.LabelFrame(
            self.tools_frame,
            text="📝 تدوين المباراة (PGN)",
            font=("Arial", 12, "bold"),
            bg="#3B4252",
            fg="#88C0D0",
            relief=tk.GROOVE,
            bd=2
        )
        pgn_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.pgn_text = scrolledtext.ScrolledText(
            pgn_frame,
            height=10,
            width=30,
            font=("Consolas", 10),
            bg="#434C5E",
            fg="#ECEFF4",
            insertbackground="#ECEFF4",
            relief=tk.SUNKEN,
            bd=1
        )
        self.pgn_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
    def draw_enhanced_board(self):
        """رسم رقعة شطرنج محسنة مع الألوان الصحيحة والحركات القانونية"""
        if not self.canvas:
            return
            
        self.canvas.delete("all")
        
        # رسم الخلفية
        self.canvas.create_rectangle(
            0, 0, 8 * self.square_size + 40, 8 * self.square_size + 40,
            fill="#4C566A", outline="#2E3440", width=3
        )
        
        # رسم المربعات مع الألوان الصحيحة
        for row in range(8):
            for col in range(8):
                self.draw_correct_square(row, col)
                
        # رسم تمييز آخر حركة
        if self.highlight_last_move and self.last_move:
            self.draw_last_move_highlight()
                
        # رسم الحركات القانونية للقطعة المحددة
        if self.show_legal_moves and self.selected_square is not None:
            self.draw_legal_moves()
        
        # رسم إحداثيات محسنة
        self.draw_enhanced_coordinates()
        
        # رسم القطع مع صور
        self.draw_pieces_with_images()
        
    def draw_last_move_highlight(self):
        """رسم تمييز آخر حركة"""
        if not self.last_move:
            return
            
        # تمييز مربع المصدر
        from_square = self.last_move.from_square
        from_file = chess.square_file(from_square)
        from_rank = chess.square_rank(from_square)
        
        if self.flipped:
            from_display_col = 7 - from_file
            from_display_row = from_rank
        else:
            from_display_col = from_file
            from_display_row = 7 - from_rank
            
        x1 = from_display_col * self.square_size + 20
        y1 = from_display_row * self.square_size + 20
        x2 = x1 + self.square_size
        y2 = y1 + self.square_size
        
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="#FFD700",
            width=4,
            tags="last_move"
        )
        
        # تمييز مربع الهدف
        to_square = self.last_move.to_square
        to_file = chess.square_file(to_square)
        to_rank = chess.square_rank(to_square)
        
        if self.flipped:
            to_display_col = 7 - to_file
            to_display_row = to_rank
        else:
            to_display_col = to_file
            to_display_row = 7 - to_rank
            
        x1 = to_display_col * self.square_size + 20
        y1 = to_display_row * self.square_size + 20
        x2 = x1 + self.square_size
        y2 = y1 + self.square_size
        
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="#FFD700",
            width=4,
            tags="last_move"
        )

    def draw_legal_moves(self):
        """رسم الحركات القانونية للقطعة المحددة"""
        if not self.selected_square:
            return
            
        legal_moves = self.get_legal_moves_for_square(self.selected_square)
        
        for target_square in legal_moves:
            file = chess.square_file(target_square)
            rank = chess.square_rank(target_square)
            
            if self.flipped:
                display_col = 7 - file
                display_row = rank
            else:
                display_col = file
                display_row = 7 - rank
            
            x = display_col * self.square_size + self.square_size // 2 + 20
            y = display_row * self.square_size + self.square_size // 2 + 20
            
            # رسم دائرة للحركات العادية
            piece_on_target = self.board.piece_at(target_square)
            if piece_on_target:
                # مربع للأسر
                self.canvas.create_rectangle(
                    x - 20, y - 20, x + 20, y + 20,
                    outline="#FF6B6B",
                    width=3,
                    tags="legal_move"
                )
            else:
                # دائرة للحركة العادية
                self.canvas.create_oval(
                    x - 8, y - 8, x + 8, y + 8,
                    fill="#4ECDC4",
                    outline="#45B7AF",
                    width=2,
                    tags="legal_move"
                )

    def draw_correct_square(self, row, col):
        """رسم مربع بالألوان الصحيحة - a1 أسود"""
        if self.flipped:
            display_row = row
            display_col = 7 - col
        else:
            display_row = 7 - row
            display_col = col
            
        x1 = display_col * self.square_size + 20
        y1 = display_row * self.square_size + 20
        x2 = x1 + self.square_size
        y2 = y1 + self.square_size
        
        # الخوارزمية الصحيحة لألوان الشطرنج
        square_is_dark = (row + col) % 2 == 0
        
        if square_is_dark:
            main_color = "#B58863"  # بني داكن (مربعات داكنة)
            shadow_color = "#A67C52"
        else:
            main_color = "#F0D9B5"  # بيج فاتح (مربعات فاتحة)  
            shadow_color = "#E8D1A5"
        
        # تمييز المربع المحدد
        actual_square = chess.square(col, row)
        if actual_square == self.selected_square:
            main_color = "#7FB069"  # أخضر للمربع المحدد
            shadow_color = "#6FA058"
        
        # رسم ظل المربع
        self.canvas.create_rectangle(
            x1 + 2, y1 + 2, x2 + 2, y2 + 2,
            fill=shadow_color, outline="", width=0
        )
        
        # رسم المربع الرئيسي
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=main_color,
            outline="#8B6914",
            width=1,
            tags=f"square_{row}_{col}"
        )
        
        # تأثير ثلاثي الأبعاد
        self.canvas.create_line(x1, y1, x2, y1, fill="#FFFFFF", width=1)
        self.canvas.create_line(x1, y1, x1, y2, fill="#FFFFFF", width=1)
        self.canvas.create_line(x2-1, y1, x2-1, y2, fill="#000000", width=1)
        self.canvas.create_line(x1, y2-1, x2, y2-1, fill="#000000", width=1)

    def draw_enhanced_coordinates(self):
        """رسم إحداثيات محسنة"""
        files = "abcdefgh"
        ranks = "12345678"
        
        for i in range(8):
            # الأحرف (الأعمدة)
            if self.flipped:
                file_char = files[7-i]
                x = i * self.square_size + self.square_size // 2 + 20
            else:
                file_char = files[i]
                x = i * self.square_size + self.square_size // 2 + 20
                
            y = 8 * self.square_size + 35
            
            self.canvas.create_oval(
                x-8, y-8, x+8, y+8,
                fill="#434C5E", outline="#88C0D0", width=2
            )
            
            self.canvas.create_text(
                x, y, text=file_char,
                font=("Arial", 12, "bold"),
                fill="#ECEFF4"
            )
            
            # الأرقام (الصفوف)
            if self.flipped:
                rank_char = ranks[i]
                y = (7-i) * self.square_size + self.square_size // 2 + 20
            else:
                rank_char = ranks[7-i]
                y = i * self.square_size + self.square_size // 2 + 20
                
            x = 10
            
            self.canvas.create_oval(
                x-8, y-8, x+8, y+8,
                fill="#434C5E", outline="#88C0D0", width=2
            )
            
            self.canvas.create_text(
                x, y, text=rank_char,
                font=("Arial", 12, "bold"),
                fill="#ECEFF4"
            )
            
    def draw_pieces_with_images(self):
        """رسم القطع باستخدام الصور المحلية"""
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                self.draw_single_piece_with_image(square, piece)
                
    def draw_single_piece_with_image(self, square, piece):
        """رسم قطعة واحدة بصورة"""
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        
        if self.flipped:
            display_col = 7 - file
            display_row = rank
        else:
            display_col = file
            display_row = 7 - rank
        
        x = display_col * self.square_size + self.square_size // 2 + 20
        y = display_row * self.square_size + self.square_size // 2 + 20
        
        # تحديد رمز القطعة
        color_code = 'w' if piece.color == chess.WHITE else 'b'
        piece_code = f"{color_code}{piece.symbol().upper()}"
        
        # رسم ظل القطعة
        if piece_code in self.shadow_images and self.shadow_images[piece_code]:
            self.canvas.create_image(
                x + 2, y + 2,
                image=self.shadow_images[piece_code],
                tags="piece_shadow"
            )
        
        # رسم القطعة الرئيسية
        if piece_code in self.piece_images and self.piece_images[piece_code]:
            self.canvas.create_image(
                x, y,
                image=self.piece_images[piece_code],
                tags="piece"
            )
        else:
            # استخدام النص كبديل
            piece_symbols = {
                'wK': '♔', 'wQ': '♕', 'wR': '♖', 'wB': '♗', 'wN': '♘', 'wP': '♙',
                'bK': '♚', 'bQ': '♛', 'bR': '♜', 'bB': '♝', 'bN': '♞', 'bP': '♟'
            }
            
            symbol = piece_symbols.get(piece_code, piece.symbol())
            
            # ظل النص
            self.canvas.create_text(
                x + 2, y + 2,
                text=symbol,
                font=("Arial", int(self.square_size * 0.6)),
                fill="#2E3440",
                tags="text_shadow"
            )
            
            # النص الرئيسي
            color = "#ECEFF4" if piece.color == chess.WHITE else "#434C5E"
            self.canvas.create_text(
                x, y,
                text=symbol,
                font=("Arial", int(self.square_size * 0.6), "bold"),
                fill=color,
                tags="piece"
            )

    def on_mouse_motion(self, event):
        """تتبع حركة الماوس"""
        if self.game_result is not None or self.paused or not self.canvas or self.in_review_mode:
            return
            
        col = (event.x - 20) // self.square_size
        row = (event.y - 20) // self.square_size
        
        if 0 <= col < 8 and 0 <= row < 8:
            if self.flipped:
                actual_col = 7 - col
                actual_row = row
            else:
                actual_col = col
                actual_row = 7 - row
                
            square = chess.square(actual_col, actual_row)
            
            self.canvas.delete("hover")
            
            if square != self.selected_square:
                x1 = col * self.square_size + 20
                y1 = row * self.square_size + 20
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline="#88C0D0",
                    width=3,
                    tags="hover"
                )

    def on_mouse_leave(self, event):
        """إزالة تأثيرات التفاعل"""
        if self.canvas:
            self.canvas.delete("hover")

    def on_square_click(self, event):
        """التعامل مع النقر على مربع"""
        if (self.ai_thinking or self.game_result is not None or 
            self.paused or not self.canvas or self.in_review_mode):
            return
            
        col = (event.x - 20) // self.square_size
        row = (event.y - 20) // self.square_size
        
        if 0 <= col < 8 and 0 <= row < 8:
            if self.flipped:
                actual_col = 7 - col
                actual_row = row
            else:
                actual_col = col
                actual_row = 7 - row
                
            clicked_square = chess.square(actual_col, actual_row)
            
            if self.selected_square is None:
                piece = self.board.piece_at(clicked_square)
                if piece and piece.color == self.board.turn:
                    self.selected_square = clicked_square
            else:
                move = chess.Move(self.selected_square, clicked_square)
                
                piece = self.board.piece_at(self.selected_square)
                if (piece and piece.piece_type == chess.PAWN and 
                    (chess.square_rank(clicked_square) == 0 or 
                     chess.square_rank(clicked_square) == 7)):
                    move = chess.Move(self.selected_square, clicked_square, 
                                    promotion=chess.QUEEN)
                
                if move in self.board.legal_moves:
                    self.make_move(move)
                
                self.selected_square = None
                
            self.draw_enhanced_board()
            self.update_status()
            self.update_pgn_display()

    def make_move(self, move):
        """تنفيذ حركة والتحقق من حالة اللعبة"""
        self.board.push(move)
        self.save_move_to_history(move)  # حفظ في التاريخ
        self.check_game_status()
        
        if (self.game_mode == "1vsAI" and 
            self.board.turn == chess.BLACK and 
            not self.board.is_game_over() and
            self.game_result is None):
            self.window.after(500, self.ai_move)
    
    def ai_move(self):
        """حركة الحاسوب العشوائية"""
        if self.game_result is not None or self.paused:
            return
            
        self.ai_thinking = True
        if self.status_label:
            self.status_label.config(
                text="🤔 الحاسوب يفكر...",
                fg="#D08770"
            )
        
        def think_and_move():
            thinking_time = random.uniform(1.0, 3.0)
            time.sleep(thinking_time)
            
            if not self.board.is_game_over() and self.game_result is None and not self.paused:
                legal_moves = list(self.board.legal_moves)
                if legal_moves:
                    ai_move = random.choice(legal_moves)
                    self.window.after(0, lambda: self.execute_ai_move(ai_move))
        
        thread = threading.Thread(target=think_and_move)
        thread.daemon = True
        thread.start()
    
    def execute_ai_move(self, move):
        """تنفيذ حركة الحاسوب"""
        if self.game_result is not None or self.paused:
            return
            
        self.board.push(move)
        self.save_move_to_history(move)  # حفظ في التاريخ
        self.ai_thinking = False
        self.check_game_status()
        self.draw_enhanced_board()
        self.update_status()
        self.update_pgn_display()
    
    def update_status(self):
        """تحديث معلومات حالة اللعبة"""
        if self.ai_thinking or self.paused or not self.status_label:
            return
        
        if self.game_result is not None and not self.in_review_mode:
            return
            
        if self.in_review_mode:
            review_text = f"🔍 وضع المراجعة - الحركة {self.current_position}/{len(self.move_history)}"
            self.status_label.config(text=review_text, fg="#9B59B6")
        else:
            if self.board.turn:
                turn_text = "🎯 دور الأبيض"
            else:
                turn_text = "⚫ دور الأسود"
                
            if self.board.is_check():
                turn_text += " - كش! ⚠️"
                
            mode_text = "لاعب ضد لاعب" if self.game_mode == "1vs1" else "لاعب ضد الحاسوب"
            full_text = f"{turn_text} - الوضع: {mode_text}"
            
            self.status_label.config(text=full_text, fg="#ECEFF4")
        
        if self.moves_count_label:
            self.moves_count_label.config(text=f"عدد الحركات: {len(self.move_history)}")
        
        # تحديث حالة المباراة
        if self.game_status_label:
            if self.board.is_game_over():
                self.game_status_label.config(text="الحالة: انتهت")
            elif self.game_result == "ملغاة":
                self.game_status_label.config(text="الحالة: ملغاة")
            elif self.game_result == "استسلام":
                self.game_status_label.config(text="الحالة: استسلام")
            else:
                self.game_status_label.config(text="الحالة: جارية")
                
        # تحديث اتجاه الرقعة
        if self.board_orientation_label:
            self.board_orientation_label.config(
                text=f"الرقعة: {'مقلوبة' if self.flipped else 'عادية'}"
            )
            
        # تحديث موقع التنقل
        if self.position_label:
            if self.in_review_mode:
                self.position_label.config(text=f"الموقع: {self.current_position}/{len(self.move_history)}")
            else:
                self.position_label.config(text="الموقع: الحالي")
        
    def update_pgn_display(self):
        """تحديث عرض تدوين PGN"""
        if not self.pgn_text:
            return
            
        try:
            game = chess.pgn.Game.from_board(self.board)
            game.headers["Event"] = "مباراة احترافية"
            game.headers["Date"] = time.strftime("%Y.%m.%d")
            game.headers["White"] = "اللاعب الأبيض"
            game.headers["Black"] = "اللاعب الأسود" if self.game_mode == "1vs1" else "الحاسوب"
            
            pgn_string = str(game)
            
            # إضافة معلومات التنقل إذا كان في وضع المراجعة
            if self.in_review_mode:
                pgn_string += f"\n\n[وضع المراجعة - الحركة {self.current_position}/{len(self.move_history)}]"
            
            self.pgn_text.delete(1.0, tk.END)
            self.pgn_text.insert(1.0, pgn_string)
            self.pgn_text.see(tk.END)
        except Exception as e:
            print(f"خطأ في تحديث PGN: {e}")
    
    def check_game_status(self):
        """فحص حالة انتهاء اللعبة"""
        if self.board.is_checkmate():
            winner = "🏆 الأسود" if self.board.turn else "🏆 الأبيض"
            self.game_result = "كش مات"
            messagebox.showinfo(
                "🎉 انتهت اللعبة!", 
                f"✨ كش مات! فاز {winner} ✨\n\n"
                f"🎯 تهانينا على المباراة الرائعة!\n\n"
                f"💡 يمكنك الآن استخدام الأسهم لمراجعة المباراة!"
            )
        elif self.board.is_stalemate():
            self.game_result = "تعادل"
            messagebox.showinfo(
                "🤝 انتهت اللعبة!", 
                "⚖️ تعادل - استنفاد الحركات\n\n"
                f"🎭 مباراة متوازنة ممتازة!\n\n"
                f"💡 يمكنك الآن استخدام الأسهم لمراجعة المباراة!"
            )
    
    def new_game(self):
        """بدء لعبة جديدة"""
        if len(self.move_history) > 0 or self.game_result is not None:
            result = messagebox.askyesno(
                "🔄 تأكيد اللعبة الجديدة",
                "هل تريد بدء لعبة جديدة؟\n\n⚠️ ستفقد المباراة الحالية!"
            )
            if not result:
                return
                
        self.board = chess.Board()
        self.selected_square = None
        self.ai_thinking = False
        self.game_result = None
        self.paused = False
        self.move_history = []
        self.current_position = 0
        self.in_review_mode = False
        self.last_move = None
        
        if self.canvas:
            self.canvas.delete("pause_overlay")
            self.draw_enhanced_board()
            
        self.update_status()
        self.update_pgn_display()
        messagebox.showinfo("✨ لعبة جديدة!", "🎮 تم بدء مباراة جديدة بنجاح!")
    
    def undo_move(self):
        """التراجع عن آخر حركة"""
        if not self.move_history:
            messagebox.showwarning("⚠️ تحذير", "لا توجد حركات للتراجع عنها!")
            return
            
        if self.game_result is not None:
            messagebox.showinfo("⚠️ تنبيه", "لا يمكن التراجع بعد انتهاء المباراة!")
            return
            
        if self.paused:
            messagebox.showinfo("⚠️ تنبيه", "لا يمكن التراجع أثناء الإيقاف المؤقت!")
            return
            
        if self.in_review_mode:
            messagebox.showinfo("⚠️ تنبيه", "لا يمكن التراجع في وضع المراجعة! استخدم أزرار التنقل.")
            return
            
        moves_to_undo = 1
        if self.game_mode == "1vsAI" and len(self.move_history) >= 2:
            moves_to_undo = 2
            
        for _ in range(moves_to_undo):
            if self.move_history:
                self.move_history.pop()
                self.board.pop()
                
        self.current_position = len(self.move_history)
        self.selected_square = None
        self.ai_thinking = False
        
        # تحديث آخر حركة
        if self.move_history:
            self.last_move = self.move_history[-1]['move']
        else:
            self.last_move = None
        
        if self.canvas:
            self.draw_enhanced_board()
            
        self.update_status()
        self.update_pgn_display()
        
    def save_pgn(self):
        """حفظ المباراة بصيغة PGN"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".pgn",
            filetypes=[("PGN files", "*.pgn"), ("جميع الملفات", "*.*")],
            title="💾 حفظ المباراة الاحترافية"
        )
        
        if filename:
            try:
                game = chess.pgn.Game.from_board(self.board)
                game.headers["Event"] = "مباراة احترافية"
                game.headers["Date"] = time.strftime("%Y.%m.%d")
                game.headers["White"] = "اللاعب الأبيض"
                game.headers["Black"] = "اللاعب الأسود" if self.game_mode == "1vs1" else "الحاسوب"
                
                if self.game_result == "كش مات":
                    game.headers["Result"] = "0-1" if self.board.turn else "1-0"
                elif self.game_result == "استسلام":
                    game.headers["Result"] = "0-1" if self.board.turn else "1-0"
                elif self.game_result == "تعادل":
                    game.headers["Result"] = "1/2-1/2"
                else:
                    game.headers["Result"] = "*"
                
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(str(game))
                    
                messagebox.showinfo(
                    "✅ تم الحفظ بنجاح!", 
                    f"💾 تم حفظ المباراة في:\n📁 {filename}"
                )
                return True
            except Exception as e:
                messagebox.showerror("❌ خطأ!", f"🚫 فشل في الحفظ:\n{str(e)}")
                return False
        return False
    
    def load_pgn_game(self):
        """رفع مباراة من ملف PGN"""
        filename = filedialog.askopenfilename(
            filetypes=[("PGN files", "*.pgn"), ("جميع الملفات", "*.*")],
            title="📁 اختيار ملف PGN"
        )
        
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    game = chess.pgn.read_game(f)
                    
                if game:
                    # إعادة تعيين حالة اللعبة
                    self.board = chess.Board()
                    self.move_history = []
                    self.current_position = 0
                    self.in_review_mode = False
                    self.last_move = None
                    
                    # تطبيق جميع الحركات
                    for move in game.mainline_moves():
                        self.board.push(move)
                        self.save_move_to_history(move)
                    
                    if hasattr(self, 'start_frame'):
                        self.start_frame.destroy()
                    
                    self.game_mode = "1vs1"
                    self.game_started = True
                    self.game_result = None
                    self.paused = False
                    self.create_game_interface()
                    
                    # تفعيل وضع المراجعة تلقائياً
                    self.in_review_mode = True
                    messagebox.showinfo(
                        "✅ تم التحميل!", 
                        "📂 تم تحميل المباراة بنجاح!\n\n"
                        "💡 تم تفعيل وضع المراجعة - استخدم الأسهم للتنقل!"
                    )
                else:
                    messagebox.showerror("❌ خطأ!", "🚫 ملف PGN غير صحيح")
                    
            except Exception as e:
                messagebox.showerror("❌ خطأ!", f"🚫 فشل في القراءة:\n{str(e)}")
    
    def return_to_menu(self):
        """العودة للقائمة الرئيسية"""
        if len(self.move_history) > 0 and self.game_result is None:
            result = messagebox.askyesnocancel(
                "🏠 تأكيد العودة",
                "هل تريد حفظ المباراة قبل العودة للقائمة الرئيسية؟"
            )
            if result is True:  # نعم - احفظ
                if not self.save_pgn():
                    return  # إذا فشل الحفظ، لا تعد للقائمة
            elif result is None:  # إلغاء
                return
        
        # إزالة شريط القوائم
        self.window.config(menu="")
        
        for widget in self.window.winfo_children():
            widget.destroy()
            
        # إعادة تعيين جميع المتغيرات
        self.game_started = False
        self.board = chess.Board()
        self.selected_square = None
        self.ai_thinking = False
        self.game_result = None
        self.paused = False
        self.move_history = []
        self.current_position = 0
        self.in_review_mode = False
        self.last_move = None
        
        # إعادة تعيين متغيرات الواجهة
        self.status_label = None
        self.canvas = None
        self.moves_count_label = None
        self.game_status_label = None
        self.board_orientation_label = None
        self.pgn_text = None
        self.position_label = None
        
        self.create_start_screen()
    
    def run(self):
        """تشغيل اللعبة الاحترافية"""
        try:
            self.window.mainloop()
        except Exception as e:
            messagebox.showerror("خطأ في النظام", f"حدث خطأ غير متوقع:\n{str(e)}")

# تشغيل البرنامج
if __name__ == "__main__":
    try:
        game = ProfessionalChessGame()
        game.run()
    except Exception as e:
        print(f"خطأ في بدء التشغيل: {e}")
        messagebox.showerror("خطأ", f"فشل في تشغيل البرنامج:\n{str(e)}")
