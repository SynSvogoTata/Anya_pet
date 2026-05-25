import tkinter as tk
import random
from PIL import Image, ImageTk, ImageDraw

class DesktopPet:
    def __init__(self, image_path):
        self.root = tk.Tk()
        
        # Налаштування прозорості та відображення поверх усіх вікон
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.wm_attributes('-transparentcolor', 'black') # Чорний колір стане прозорим (для Windows)
        
        # Завантаження спрайт-листа
        self.img = Image.open(image_path)
        self.img_w, self.img_h = self.img.size
        
        # Наше зображення має сітку: 2 рядки та 10 колонок
import tkinter as tk
import random
import os
import sys
from PIL import Image, ImageTk, ImageDraw

# Функція, яка дозволяє вшити картинку всередину .exe файла
def resource_path(relative_path):
    try:
        # PyInstaller створює тимчасову папку _MEIPASS при запуску .exe
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DesktopPet:
    def __init__(self, image_name):
        self.root = tk.Tk()
        
        # Налаштування вікна (поверх усіх вікон, без рамок, прозоре тло)
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.wm_attributes('-transparentcolor', 'black')
        
        # Завантажуємо картинку через наш магічний шлях resource_path
        image_path = resource_path(image_name)
        self.img = Image.open(image_path)
        self.img_w, self.img_h = self.img.size
        
        self.cols = 10
        self.rows = 2
        self.frame_w = self.img_w // self.cols
        self.frame_h = self.img_h // self.rows
        
        # Затираємо текст зверху
        draw = ImageDraw.Draw(self.img)
        draw.rectangle([0, 0, self.img_w, int(self.frame_h * 0.22)], fill="black")
        
        self.sprites = {"idle": [], "walk_right": [], "walk_left": []}
        self.load_sprites()
        
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.x = random.randint(0, self.screen_w - self.frame_w)
        self.y = self.screen_h - self.frame_h - 60 
        
        self.label = tk.Label(self.root, bd=0, bg='black')
        self.label.pack()
        
        self.state = "idle"
        self.frame_idx = 0
        self.action_timer = 0
        
        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.drag)
        
        self.update()
        self.root.mainloop()
        
    def load_sprites(self):
        def get_frame(r, c):
import sys
import os
import random
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow

# Функція для пошуку спрайтів (працює і в коді, і в .exe)
def get_asset_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class AnyaPet(QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. Налаштування вікна
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label = QLabel(self)
        self.setCentralWidget(self.label)

        # 2. Спрайти (твої 5 кадрів)
        self.anim_sprites = {
            "idle": [get_asset_path("sprites/idle/0.png")],
            "walk_right": [get_asset_path(f"sprites/walk_right/{i}.png") for i in range(2)],
            "walk_left": [get_asset_path(f"sprites/walk_left/{i}.png") for i in range(2)]
        }

        # 3. Стан програми
        self.current_state = "idle"
        self.current_frame = 0
        self.speed = 3
        self.is_dragging = False
        self.drag_offset = QPoint()

        # Початкова позиція
        screen = QApplication.primaryScreen().geometry()
        self.x = screen.width() // 2
        self.y = screen.height() - 150
        self.move(self.x, self.y)

        # 4. Таймери
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(200)

        self.behavior_timer = QTimer()
        self.behavior_timer.timeout.connect(self.change_behavior)
        self.behavior_timer.start(5000)

        self.update_appearance()

    def update_appearance(self):
        frames = self.anim_sprites[self.current_state]
        if self.current_frame >= len(frames):
            self.current_frame = 0
        
        pixmap = QPixmap(frames[self.current_frame])
        self.label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

    def animate(self):
        # Автоматичний рух працює тільки якщо ми не тягнемо Аню
        if not self.is_dragging:
            if self.current_state == "walk_right":
                self.x += self.speed
            elif self.current_state == "walk_left":
                self.x -= self.speed

            # Межі екрана
            screen_geo = QApplication.primaryScreen().geometry()
            if self.x < 0: self.x = 0
            if self.x > screen_geo.width() - self.width(): self.x = screen_geo.width() - self.width()
            
            self.move(self.x, self.y)

        self.current_frame += 1
        self.update_appearance()

    def change_behavior(self):
        if not self.is_dragging:
            self.current_state = random.choice(["idle", "walk_left", "walk_right"])
            self.current_frame = 0
        self.behavior_timer.setInterval(random.randint(3000, 7000))

    # --- ЛОГІКА ПЕРЕТЯГУВАННЯ ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.current_state = "idle" # Припиняємо бігти, коли нас схопили
            self.drag_offset = event.pos() # Де саме всередині Ані ми клікнули
        
        # Вихід з програми на праву кнопку миші
        if event.button() == Qt.MouseButton.RightButton:
            QApplication.quit()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            # Переміщуємо вікно за курсором
            new_pos = event.globalPosition().toPoint() - self.drag_offset
            self.move(new_pos)
            
            # Оновлюємо внутрішні координати x та y, щоб після того, 
            # як відпустимо, Аня продовжила бігти з нового місця
            self.x = new_pos.x()
            self.y = new_pos.y()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = AnyaPet()
    pet.show()
    sys.exit(app.exec())