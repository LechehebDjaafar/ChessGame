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
        
        # متغيرات الصور
        self.piece_images = {}
        self.shadow_images = {}
        
        # تحديد مسار مجلد الصور
        self.images_path = "images"
        
        # تحميل صور القطع
        self.load_local_piece_images()
        
        # إنشاء واجهة البداية
        self.create_start_screen()
        
    def load_local_piece_images(self):
        """تحميل صور قطع الشطرنج من مجلد images المحلي - مُصلح"""
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
                    # تحميل الصورة
                    img = Image.open(file_path)
                    
                    # التأكد من أن الصورة لديها قناة شفافية
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    # تغيير الحجم
                    img = img.resize((self.square_size - 10, self.square_size - 10), Image.Resampling.LANCZOS)
                    self.piece_images[piece_code] = ImageTk.PhotoImage(img)
                    
                    # إنشاء صورة الظل - الطريقة المُصلحة
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
        
        # إذا فشل تحميل معظم الصور، استخدم النصوص
        if loaded_count < len(piece_files) // 2:
            messagebox.showwarning(
                "⚠️ تحذير الصور", 
                f"تم تحميل {loaded_count} صورة فقط من أصل {len(piece_files)}\n"
                f"سيتم استخدام النصوص للقطع المفقودة"
            )

    def create_shadow_image(self, img):
        """إنشاء صورة الظل بطريقة آمنة"""
        try:
            # نسخ الصورة
            shadow_img = img.copy()
            
            # طريقة أبسط وأكثر أماناً لإنشاء الظل
            # تعتيم الصورة
            enhancer = ImageEnhance.Brightness(shadow_img)
            shadow_img = enhancer.enhance(0.3)  # تعتيم بنسبة 30%
            
            # تقليل الشفافية
            if shadow_img.mode == 'RGBA':
                # فصل القنوات
                r, g, b, a = shadow_img.split()
                # تحويل القنوات إلى رمادي داكن
                gray = Image.new('L', r.size, 50)  # رمادي داكن
                # دمج القنوات مع تقليل الشفافية
                alpha_enhancer = ImageEnhance.Brightness(a)
                a = alpha_enhancer.enhance(0.5)  # نصف الشفافية
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
        """إنشاء واجهة البداية المحسنة"""
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
            text="🎯 تجربة شطرنج احترافية مع رسوميات عالية الجودة",
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
            
            btn.bind("<Enter>", lambda e, btn=btn, color=color: btn.config(bg=self.lighten_color(color)))
            btn.bind("<Leave>", lambda e, btn=btn, color=color: btn.config(bg=color))

    def lighten_color(self, color):
        """تفتيح لون للتأثير التفاعلي"""
        color_map = {
            "#5E81AC": "#7C9CC4", "#BF616A": "#CC7A82", 
            "#A3BE8C": "#B5CAA0", "#B48EAD": "#C5A3BD"
        }
        return color_map.get(color, color)
        
    def show_settings(self):
        """نافذة الإعدادات"""
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
        
        # إعدادات حجم الرقعة
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
        
        # زر إعادة تحميل الصور
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
        if self.game_started:
            self.draw_enhanced_board()
        messagebox.showinfo("✅ تم", "تم إعادة تحميل الصور بنجاح!")
        
    def apply_settings(self, new_size, window):
        """تطبيق الإعدادات الجديدة"""
        if new_size != self.square_size:
            self.square_size = new_size
            self.load_local_piece_images()
            if self.game_started:
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
        self.start_frame.destroy()
        self.create_game_interface()
        
    def create_game_interface(self):
        """إنشاء واجهة اللعبة المحسنة"""
        main_frame = tk.Frame(self.window, bg="#2E3440")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # الإطار الجانبي للأدوات
        self.tools_frame = tk.Frame(main_frame, width=250, bg="#3B4252", relief=tk.RAISED, bd=2)
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
        
        # أزرار التحكم المحسنة مع مميزات جديدة
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
        """إنشاء أزرار تحكم محسنة مع مميزات جديدة"""
        button_frame = tk.Frame(parent, bg="#2E3440")
        button_frame.pack(pady=15)
        
        # الصف الأول من الأزرار
        first_row = tk.Frame(button_frame, bg="#2E3440")
        first_row.pack(pady=5)
        
        buttons_row1 = [
            ("🔄", "لعبة جديدة", self.new_game, "#5E81AC"),
            ("↩️", "تراجع", self.undo_move, "#D08770"),
            ("🔄", "قلب الرقعة", self.flip_board, "#A3BE8C"),
            ("💾", "حفظ PGN", self.save_pgn, "#B48EAD")
        ]
        
        for icon, text, command, color in buttons_row1:
            self.create_control_button(first_row, icon, text, command, color)
        
        # الصف الثاني من الأزرار - مميزات جديدة
        second_row = tk.Frame(button_frame, bg="#2E3440")
        second_row.pack(pady=5)
        
        buttons_row2 = [
            ("🏳️", "استسلام", self.resign_game, "#E74C3C"),
            ("⏹️", "إلغاء المباراة", self.cancel_game, "#F39C12"),
            ("⏸️", "إيقاف مؤقت", self.pause_game, "#9B59B6"),
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
        
        # تأثيرات بصرية
        btn.bind("<Enter>", lambda e: btn.config(bg=self.lighten_color(color), relief=tk.GROOVE))
        btn.bind("<Leave>", lambda e: btn.config(bg=color, relief=tk.RAISED))

    def resign_game(self):
        """استسلام أحد اللاعبين"""
        if self.game_result is not None:
            messagebox.showinfo("⚠️ تنبيه", "المباراة انتهت بالفعل!")
            return
            
        # تحديد اللاعب المستسلم
        current_player = "الأبيض" if self.board.turn else "الأسود"
        winner = "الأسود" if self.board.turn else "الأبيض"
        
        # تأكيد الاستسلام
        result = messagebox.askyesno(
            "🏳️ تأكيد الاستسلام",
            f"هل أنت متأكد من استسلام {current_player}؟\n\n"
            f"🏆 سيفوز {winner} بالمباراة!"
        )
        
        if result:
            self.game_result = "استسلام"
            self.ai_thinking = False
            
            # تحديث حالة اللعبة
            self.status_label.config(
                text=f"🏳️ استسلم {current_player} - فاز {winner} 🏆",
                fg="#E74C3C"
            )
            
            # إضافة نتيجة الاستسلام لـ PGN
            self.update_pgn_with_result("استسلام", winner)
            
            messagebox.showinfo(
                "🏆 انتهت المباراة!",
                f"🏳️ استسلم {current_player}\n\n"
                f"🎉 تهانينا {winner} على الفوز!"
            )

    def cancel_game(self):
        """إلغاء المباراة الحالية"""
        if not self.board.move_stack and self.game_result is None:
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
            
            # إعادة تعيين اللعبة
            self.board = chess.Board()
            self.selected_square = None
            
            # تحديث الواجهة
            self.draw_enhanced_board()
            self.status_label.config(
                text="⏹️ تم إلغاء المباراة - جاهز لبدء مباراة جديدة",
                fg="#F39C12"
            )
            
            # مسح PGN
            self.pgn_text.delete(1.0, tk.END)
            self.pgn_text.insert(1.0, "المباراة ملغاة - لا توجد حركات")
            
            messagebox.showinfo("⏹️ تم الإلغاء", "تم إلغاء المباراة بنجاح!")

    def pause_game(self):
        """إيقاف مؤقت للمباراة"""
        if self.game_result is not None:
            messagebox.showinfo("⚠️ تنبيه", "المباراة انتهت بالفعل!")
            return
            
        # إيقاف الحاسوب إذا كان يفكر
        if self.ai_thinking:
            self.ai_thinking = False
            self.status_label.config(
                text="⏸️ المباراة متوقفة مؤقتاً - انقر 'استئناف' للمتابعة",
                fg="#9B59B6"
            )
            messagebox.showinfo("⏸️ إيقاف مؤقت", "تم إيقاف المباراة مؤقتاً!")
        else:
            # استئناف المباراة
            self.update_status()
            messagebox.showinfo("▶️ استئناف", "تم استئناف المباراة!")

    def update_pgn_with_result(self, result_type, winner):
        """تحديث PGN مع نتيجة المباراة"""
        try:
            game = chess.pgn.Game.from_board(self.board)
            game.headers["Event"] = "مباراة احترافية"
            game.headers["Date"] = time.strftime("%Y.%m.%d")
            game.headers["White"] = "اللاعب الأبيض"
            game.headers["Black"] = "اللاعب الأسود" if self.game_mode == "1vs1" else "الحاسوب"
            
            # تحديد النتيجة
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
            height=12,
            width=28,
            font=("Consolas", 10),
            bg="#434C5E",
            fg="#ECEFF4",
            insertbackground="#ECEFF4",
            relief=tk.SUNKEN,
            bd=1
        )
        self.pgn_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
    def draw_enhanced_board(self):
        """رسم رقعة شطرنج محسنة مع الألوان الصحيحة"""
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
                
        # رسم إحداثيات محسنة
        self.draw_enhanced_coordinates()
        
        # رسم القطع مع صور
        self.draw_pieces_with_images()
        
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
        # a1 = (0,0) يجب أن يكون أسود
        # إذا كان مجموع الإحداثيات زوجي = أسود، فردي = أبيض
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
        if self.game_result is not None:
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
        self.canvas.delete("hover")

    def on_square_click(self, event):
        """التعامل مع النقر على مربع"""
        if self.ai_thinking or self.game_result is not None:
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
        self.check_game_status()
        
        if (self.game_mode == "1vsAI" and 
            self.board.turn == chess.BLACK and 
            not self.board.is_game_over() and
            self.game_result is None):
            self.window.after(500, self.ai_move)
    
    def ai_move(self):
        """حركة الحاسوب العشوائية"""
        if self.game_result is not None:
            return
            
        self.ai_thinking = True
        self.status_label.config(
            text="🤔 الحاسوب يفكر...",
            fg="#D08770"
        )
        
        def think_and_move():
            thinking_time = random.uniform(1.0, 3.0)
            time.sleep(thinking_time)
            
            if not self.board.is_game_over() and self.game_result is None:
                legal_moves = list(self.board.legal_moves)
                if legal_moves:
                    ai_move = random.choice(legal_moves)
                    self.window.after(0, lambda: self.execute_ai_move(ai_move))
        
        thread = threading.Thread(target=think_and_move)
        thread.daemon = True
        thread.start()
    
    def execute_ai_move(self, move):
        """تنفيذ حركة الحاسوب"""
        if self.game_result is not None:
            return
            
        self.board.push(move)
        self.ai_thinking = False
        self.check_game_status()
        self.draw_enhanced_board()
        self.update_status()
        self.update_pgn_display()
    
    def flip_board(self):
        """قلب اتجاه الرقعة"""
        self.flipped = not self.flipped
        self.draw_enhanced_board()
    
    def update_status(self):
        """تحديث معلومات حالة اللعبة"""
        if self.ai_thinking:
            return
        
        if self.game_result is not None:
            return
            
        if self.board.turn:
            turn_text = "🎯 دور الأبيض"
        else:
            turn_text = "⚫ دور الأسود"
            
        if self.board.is_check():
            turn_text += " - كش! ⚠️"
            
        mode_text = "لاعب ضد لاعب" if self.game_mode == "1vs1" else "لاعب ضد الحاسوب"
        full_text = f"{turn_text} - الوضع: {mode_text}"
        
        self.status_label.config(text=full_text, fg="#ECEFF4")
        self.moves_count_label.config(text=f"عدد الحركات: {len(self.board.move_stack)}")
        
        # تحديث حالة المباراة
        if self.board.is_game_over():
            self.game_status_label.config(text="الحالة: انتهت")
        elif self.game_result == "ملغاة":
            self.game_status_label.config(text="الحالة: ملغاة")
        elif self.game_result == "استسلام":
            self.game_status_label.config(text="الحالة: استسلام")
        else:
            self.game_status_label.config(text="الحالة: جارية")
        
    def update_pgn_display(self):
        """تحديث عرض تدوين PGN"""
        try:
            game = chess.pgn.Game.from_board(self.board)
            game.headers["Event"] = "مباراة احترافية"
            game.headers["Date"] = time.strftime("%Y.%m.%d")
            game.headers["White"] = "اللاعب الأبيض"
            game.headers["Black"] = "اللاعب الأسود" if self.game_mode == "1vs1" else "الحاسوب"
            
            pgn_string = str(game)
            
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
                f"✨ كش مات! فاز {winner} ✨\n\n🎯 تهانينا على المباراة الرائعة!"
            )
        elif self.board.is_stalemate():
            self.game_result = "تعادل"
            messagebox.showinfo(
                "🤝 انتهت اللعبة!", 
                "⚖️ تعادل - استنفاد الحركات\n\n🎭 مباراة متوازنة ممتازة!"
            )
    
    def new_game(self):
        """بدء لعبة جديدة"""
        if self.board.move_stack or self.game_result is not None:
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
        self.draw_enhanced_board()
        self.update_status()
        self.update_pgn_display()
        messagebox.showinfo("✨ لعبة جديدة!", "🎮 تم بدء مباراة جديدة بنجاح!")
    
    def undo_move(self):
        """التراجع عن آخر حركة"""
        if not self.board.move_stack:
            messagebox.showwarning("⚠️ تحذير", "لا توجد حركات للتراجع عنها!")
            return
            
        if self.game_result is not None:
            messagebox.showinfo("⚠️ تنبيه", "لا يمكن التراجع بعد انتهاء المباراة!")
            return
            
        moves_to_undo = 1
        if self.game_mode == "1vsAI" and len(self.board.move_stack) >= 2:
            moves_to_undo = 2
            
        for _ in range(moves_to_undo):
            if self.board.move_stack:
                self.board.pop()
                
        self.selected_square = None
        self.ai_thinking = False
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
                
                # إضافة نتيجة المباراة
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
            except Exception as e:
                messagebox.showerror("❌ خطأ!", f"🚫 فشل في الحفظ:\n{str(e)}")
    
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
                    self.board = game.board()
                    for move in game.mainline_moves():
                        self.board.push(move)
                    
                    if hasattr(self, 'start_frame'):
                        self.start_frame.destroy()
                    
                    self.game_mode = "1vs1"
                    self.game_started = True
                    self.game_result = None
                    self.create_game_interface()
                    
                    messagebox.showinfo("✅ تم التحميل!", "📂 تم تحميل المباراة بنجاح!")
                else:
                    messagebox.showerror("❌ خطأ!", "🚫 ملف PGN غير صحيح")
                    
            except Exception as e:
                messagebox.showerror("❌ خطأ!", f"🚫 فشل في القراءة:\n{str(e)}")
    
    def return_to_menu(self):
        """العودة للقائمة الرئيسية"""
        if self.board.move_stack and self.game_result is None:
            result = messagebox.askyesno(
                "🏠 تأكيد العودة",
                "هل تريد العودة للقائمة الرئيسية؟\n\n⚠️ ستفقد المباراة الحالية!"
            )
            if not result:
                return
        
        for widget in self.window.winfo_children():
            widget.destroy()
            
        self.game_started = False
        self.board = chess.Board()
        self.selected_square = None
        self.ai_thinking = False
        self.game_result = None
        
        self.create_start_screen()
    
    def run(self):
        """تشغيل اللعبة الاحترافية"""
        self.window.mainloop()

# تشغيل البرنامج
if __name__ == "__main__":
    try:
        game = ProfessionalChessGame()
        game.run()
    except Exception as e:
        print(f"خطأ في بدء التشغيل: {e}")
        messagebox.showerror("خطأ", f"فشل في تشغيل البرنامج:\n{str(e)}")
