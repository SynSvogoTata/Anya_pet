import sys
import os
import random
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow

def get_asset_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class AnyaPet(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label = QLabel(self)
        self.setCentralWidget(self.label)

        # Додаємо твої нові папки для ходьби вгору та вниз
        self.anim_sprites = {
            "idle": [get_asset_path("sprites/idle/0.png")],
            "walk_right": [get_asset_path(f"sprites/walk_right/{i}.png") for i in range(2)],
            "walk_left": [get_asset_path(f"sprites/walk_left/{i}.png") for i in range(2)],
            "walk_backward": [get_asset_path(f"sprites/walk_backward/{i}.png") for i in range(2)], # До нас обличчям (вниз)
            "walk_forward": [get_asset_path(f"sprites/walk_forward/{i}.png") for i in range(2)]    # До нас спиною (вгору)
        }

        self.current_state = "idle"
        self.current_frame = 0
        
        # Швидкість ходьби (залишаємо швидкою та чіткою)
        self.speed = 12
        
        self.is_dragging = False
        self.drag_offset = QPoint()
        self.last_mouse_pos = QPoint()
        
        # Фізика для польоту
        self.vx = 0.0  
        self.vy = 0.0  
        self.gravity = 0.8  
        self.friction = 0.98  
        self.bounce = 0.3  
        self.is_falling = False # Чи летить вона зараз після кидка

        screen = QApplication.primaryScreen().geometry()
        self.x = float(screen.width() // 2)
        # Початкова позиція — на самій підлозі екрана
        self.y = float(screen.height() - 250)
        self.move(int(self.x), int(self.y))

        # Зміна кадрів (200 мс)
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(200)

        # Розрахунок фізики польоту та кидків
        self.physics_timer = QTimer()
        self.physics_timer.timeout.connect(self.apply_physics)
        self.physics_timer.start(16)

        # ШІ вибору куди йти
        self.behavior_timer = QTimer()
        self.behavior_timer.timeout.connect(self.change_behavior)
        self.behavior_timer.start(5000)

        self.update_appearance()

    def update_appearance(self):
        frames = self.anim_sprites[self.current_state]
        if self.current_frame >= len(frames):
            self.current_frame = 0
        
        orig_pixmap = QPixmap(frames[self.current_frame])
        
        # Твій ідеальний середній розмір
        scaled_pixmap = orig_pixmap.scaled(
            250, 
            -1, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.label.setPixmap(scaled_pixmap)
        self.resize(scaled_pixmap.width(), scaled_pixmap.height())

    def apply_physics(self):
        # Якщо тягаємо мишкою або вона просто гуляє по землі — фізику польоту відключаємо
        if self.is_dragging or not self.is_falling:
            return

        screen_geo = QApplication.primaryScreen().geometry()
        floor_y = screen_geo.height() - self.height()

        # Падіння під дією гравітації (тільки коли її кинули)
        self.vy += self.gravity
        self.vx *= self.friction
        self.vy *= self.friction

        self.x += self.vx
        self.y += self.vy

        # Відскоки від стін
        if self.x < 0:
            self.x = 0
            self.vx = -self.vx * self.bounce
        elif self.x > screen_geo.width() - self.width():
            self.x = screen_geo.width() - self.width()
            self.vx = -self.vx * self.bounce

        # Приземлення на підлогу після кидка
        if self.y >= floor_y:
            self.y = floor_y
            if self.vy > 2.0:  
                self.vy = -self.vy * self.bounce
            else:
                self.vy = 0
                self.vx = 0
                self.is_falling = False # Офіційно приземлилася, тепер може гуляти

        self.move(int(self.x), int(self.y))

    def animate(self):
        screen_geo = QApplication.primaryScreen().geometry()
        floor_y = screen_geo.height() - self.height()
        
        # Дозволена зона для прогулянок (наприклад, 200 пікселів від нижнього краю)
        top_boundary = floor_y - 200 

        # Рух під час самостійної прогулянки (коли не в польоті і не в руках)
        if not self.is_dragging and not self.is_falling:
            if self.current_state == "walk_right":
                self.x += self.speed
            elif self.current_state == "walk_left":
                self.x -= self.speed
            elif self.current_state == "walk_forward": # Йде вгору (від нас)
                self.y -= self.speed
            elif self.current_state == "walk_backward": # Йде вниз (до нас)
                self.y += self.speed

            # Обмежуємо пересування екраном, щоб Аня не втекла
            if self.x < 0: self.x = 0
            if self.x > screen_geo.width() - self.width(): self.x = screen_geo.width() - self.width()
            
            if self.y < top_boundary: self.y = top_boundary
            if self.y > floor_y: self.y = floor_y
            
            self.move(int(self.x), int(self.y))

        self.current_frame += 1
        self.update_appearance()

    def change_behavior(self):
        # Змінюємо напрямок, тільки якщо Аня спокійно ходить, а не летить
        if not self.is_dragging and not self.is_falling:
            self.current_state = random.choice(["idle", "walk_left", "walk_right", "walk_forward", "walk_backward"])
            self.current_frame = 0
        self.behavior_timer.setInterval(random.randint(3000, 7000))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.is_falling = False
            self.current_state = "idle"
            self.drag_offset = event.pos()
            self.last_mouse_pos = event.globalPosition().toPoint()
            self.vx = 0
            self.vy = 0

        if event.button() == Qt.MouseButton.RightButton:
            QApplication.quit()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            current_global = event.globalPosition().toPoint()
            new_pos = current_global - self.drag_offset
            self.move(new_pos)
            
            self.vx = current_global.x() - self.last_mouse_pos.x()
            self.vy = current_global.y() - self.last_mouse_pos.y()
            
            self.last_mouse_pos = current_global
            self.x = float(new_pos.x())
            self.y = float(new_pos.y())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            
            # Якщо ми закинули її вище за підлогу — вмикаємо режим падіння
            screen_geo = QApplication.primaryScreen().geometry()
            if self.y < screen_geo.height() - self.height() - 5:
                self.is_falling = True
                self.vx = max(-15.0, min(15.0, self.vx))
                self.vy = max(-20.0, min(15.0, self.vy))
            else:
                self.is_falling = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = AnyaPet()
    pet.show()
    sys.exit(app.exec())
