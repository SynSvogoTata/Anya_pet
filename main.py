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

        self.anim_sprites = {
            "idle": [get_asset_path("sprites/idle/0.png")],
            "walk_right": [get_asset_path(f"sprites/walk_right/{i}.png") for i in range(2)],
            "walk_left": [get_asset_path(f"sprites/walk_left/{i}.png") for i in range(2)]
        }

        self.current_state = "idle"
        self.current_frame = 0
        
        # Швидка ходьба без ефекту ковзання
        self.speed = 12
        
        self.is_dragging = False
        self.drag_offset = QPoint()
        self.last_mouse_pos = QPoint()
        
        self.vx = 0.0  
        self.vy = 0.0  
        self.gravity = 0.8  
        self.friction = 0.98  
        self.bounce = 0.3  

        screen = QApplication.primaryScreen().geometry()
        self.x = float(screen.width() // 2)
        self.y = float(screen.height() - 150)
        self.move(int(self.x), int(self.y))

        # Швидкість кадрів залишаємо стандартною (200 мс)
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(200)

        self.physics_timer = QTimer()
        self.physics_timer.timeout.connect(self.apply_physics)
        self.physics_timer.start(16)

        self.behavior_timer = QTimer()
        self.behavior_timer.timeout.connect(self.change_behavior)
        self.behavior_timer.start(5000)

        self.update_appearance()

    def update_appearance(self):
        frames = self.anim_sprites[self.current_state]
        if self.current_frame >= len(frames):
            self.current_frame = 0
        
        orig_pixmap = QPixmap(frames[self.current_frame])
        
        # Задаємо чіткий середній розмір: ширина 250 пікселів.
        # Висота (ось цей мінус 1) підлаштується автоматично, щоб зберегти пропорції Ані.
        scaled_pixmap = orig_pixmap.scaled(
            250, 
            -1, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.label.setPixmap(scaled_pixmap)
        self.resize(scaled_pixmap.width(), scaled_pixmap.height())

    def apply_physics(self):
        if self.is_dragging:
            return

        screen_geo = QApplication.primaryScreen().geometry()
        floor_y = screen_geo.height() - self.height()

        if self.y >= floor_y:
            self.vy = 0
            self.y = floor_y
            self.vx *= 0.8  
            if abs(self.vx) < 0.1:
                self.vx = 0
        else:
            self.vy += self.gravity
            self.vx *= self.friction
            self.vy *= self.friction

        self.x += self.vx
        self.y += self.vy

        if self.x < 0:
            self.x = 0
            self.vx = -self.vx * self.bounce
        elif self.x > screen_geo.width() - self.width():
            self.x = screen_geo.width() - self.width()
            self.vx = -self.vx * self.bounce

        if self.y > floor_y:
            self.y = floor_y
            if self.vy > 2.0:  
                self.vy = -self.vy * self.bounce
            else:
                self.vy = 0

        self.move(int(self.x), int(self.y))

    def animate(self):
        screen_geo = QApplication.primaryScreen().geometry()
        if not self.is_dragging and self.y < screen_geo.height() - self.height() - 5:
            self.current_state = "idle"

        if not self.is_dragging and self.y >= screen_geo.height() - self.height() - 5:
            if self.current_state == "walk_right":
                self.x += self.speed
            elif self.current_state == "walk_left":
                self.x -= self.speed

            if self.x < 0: self.x = 0
            if self.x > screen_geo.width() - self.width(): self.x = screen_geo.width() - self.width()
            
            self.move(int(self.x), int(self.y))

        self.current_frame += 1
        self.update_appearance()

    def change_behavior(self):
        screen_geo = QApplication.primaryScreen().geometry()
        if not self.is_dragging and self.y >= screen_geo.height() - self.height() - 5:
            self.current_state = random.choice(["idle", "walk_left", "walk_right"])
            self.current_frame = 0
        self.behavior_timer.setInterval(random.randint(3000, 7000))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
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
            self.vx = max(-15.0, min(15.0, self.vx))
            self.vy = max(-20.0, min(15.0, self.vy))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = AnyaPet()
    pet.show()
    sys.exit(app.exec())
