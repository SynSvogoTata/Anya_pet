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
            "idle": [get_asset_path("sprites/idle/0.jpg")],
            "walk_right": [get_asset_path(f"sprites/walk_right/{i}.jpg") for i in range(2)],
            "walk_left": [get_asset_path(f"sprites/walk_left/{i}.jpg") for i in range(2)]
        }

        self.current_state = "idle"
        self.current_frame = 0
        self.speed = 12
        self.is_dragging = False
        self.drag_offset = QPoint()

        screen = QApplication.primaryScreen().geometry()
        self.x = screen.width() // 2
        self.y = screen.height() - 150
        self.move(self.x, self.y)

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
        
        # Завантажуємо оригінальну картинку
        orig_pixmap = QPixmap(frames[self.current_frame])
        
        # Вираховуємо нові розміри (ділимо ширину та висоту на 10)
        new_width = orig_pixmap.width() // 10
        new_height = orig_pixmap.height() // 10
        
        # Масштабуємо з урахуванням пропорцій та якісним згладжуванням
        scaled_pixmap = orig_pixmap.scaled(
            new_width, 
            new_height, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.label.setPixmap(scaled_pixmap)
        self.resize(scaled_pixmap.width(), scaled_pixmap.height())

    def animate(self):
        if not self.is_dragging:
            if self.current_state == "walk_right":
                self.x += self.speed
            elif self.current_state == "walk_left":
                self.x -= self.speed

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

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.current_state = "idle"
            self.drag_offset = event.pos()
        
        if event.button() == Qt.MouseButton.RightButton:
            QApplication.quit()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            new_pos = event.globalPosition().toPoint() - self.drag_offset
            self.move(new_pos)
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
