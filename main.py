import sys
import os
import random
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import QPixmap, QAction, QCursor
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QMenu

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
            "walk_left": [get_asset_path(f"sprites/walk_left/{i}.png") for i in range(2)],
            "walk_forward": [get_asset_path(f"sprites/walk_forward/{i}.png") for i in range(2)],   
            "walk_backward": [get_asset_path(f"sprites/walk_backward/{i}.png") for i in range(2)],
            "hang": [get_asset_path(f"sprites/hang/{i}.png") for i in range(2) if os.path.exists(get_asset_path(f"sprites/hang/{i}.png"))] or [get_asset_path("sprites/idle/0.png")],
            "sit": [get_asset_path("sprites/sit/0.png")] if os.path.exists(get_asset_path("sprites/sit/0.png")) else [get_asset_path("sprites/idle/0.png")]
        }

        self.current_state = "idle"
        self.current_frame = 0
        self.normal_speed = 12
        self.hunt_speed = 24  # Подвійна швидкість для полювання!
        
        self.is_dragging = False
        self.drag_offset = QPoint()
        self.last_mouse_pos = QPoint()
        
        self.current_mode = "physics" 
        
        self.mouse_hunt_allowed = False
        self.is_hunting = False
        self.is_hanging = False
        self.is_dropping = False
        self.drop_target_y = 0.0
        self.shake_count = 0
        self.last_shake_pos = QPoint()
        self.sit_timer_counter = 0

        self.vx = 0.0  
        self.vy = 0.0  
        self.gravity = 0.8  
        self.friction = 0.98  
        self.is_falling = False 

        self.resize(125, 125)

        screen = QApplication.primaryScreen().geometry()
        self.x = float(screen.width() // 2)
        self.y = float(screen.height() - 200) 
        self.move(int(self.x), int(self.y))

        self.start_timer = QTimer()
        self.start_timer.setSingleShot(True)
        self.start_timer.timeout.connect(self.init_timers)
        self.start_timer.start(150)

    def init_timers(self):
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
        try:
            frames = self.anim_sprites.get(self.current_state, self.anim_sprites["idle"])
            if self.current_frame >= len(frames):
                self.current_frame = 0
            
            orig_pixmap = QPixmap(frames[self.current_frame])
            if orig_pixmap.isNull():
                self.label.setText("Помилка")
                self.label.setStyleSheet("color: red; font-size: 10px;")
                return

            scaled_pixmap = orig_pixmap.scaled(
                125, 
                125, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.label.setPixmap(scaled_pixmap)
            self.resize(125, 125)
        except Exception as e:
            print(f"Помилка вигляду: {e}")

    def apply_physics(self):
        if self.is_hanging:
            mouse_pos = QCursor.pos()
            self.x = float(mouse_pos.x() - self.width() // 2)
            self.y = float(mouse_pos.y())
            self.move(int(self.x), int(self.y))
            
            if self.last_shake_pos != QPoint():
                dist = (mouse_pos - self.last_shake_pos).manhattanLength()
                if dist > 40:
                    self.shake_count += 1
            self.last_shake_pos = mouse_pos

            if self.shake_count > 15:
                self.is_hanging = False
                self.is_dropping = True
                self.current_state = "hang"
                self.drop_target_y = self.y + (self.height() * 2)
                self.shake_count = 0
            return

        if self.is_dropping:
            self.y += 8.0
            screen_geo = QApplication.primaryScreen().geometry()
            floor_y = screen_geo.height() - self.height()
            
            if self.y >= self.drop_target_y or self.y >= floor_y:
                if self.y > floor_y: self.y = floor_y
                self.is_dropping = False
                self.current_state = "sit"
                self.sit_timer_counter = 15
            self.move(int(self.x), int(self.y))
            return

        if self.current_mode != "physics" or self.is_dragging or not self.is_falling:
            return

        screen_geo = QApplication.primaryScreen().geometry()
        floor_y = screen_geo.height() - self.height()

        self.vy += self.gravity
        self.vx *= self.friction
        self.vy *= self.friction

        self.x += self.vx
        self.y += self.vy

        if self.x < 0:
            self.x = 0
            self.vx = 0  
        elif self.x > screen_geo.width() - self.width():
            self.x = screen_geo.width() - self.width()
            self.vx = 0  

        if self.y >= floor_y:
            self.y = floor_y
            if self.vy > 2.0:  
                self.vy = -self.vy * 0.15  
            else:
                self.vy = 0
                self.vx = 0
                self.is_falling = False 

        self.move(int(self.x), int(self.y))

    def animate(self):
        if self.is_dragging or self.is_hanging or self.is_dropping:
            self.current_frame += 1
            self.update_appearance()
            return

        if self.current_state == "sit":
            self.sit_timer_counter -= 1
            if self.sit_timer_counter <= 0:
                self.current_state = "idle"
            self.current_frame += 1
            self.update_appearance()
            return

        screen_geo = QApplication.primaryScreen().geometry()
        floor_y = screen_geo.height() - self.height()

        # ЛОГІКА ПОЛЮВАННЯ НА МИШУ (В РЕАЛЬНОМУ ЧАСІ, БЕЗ ДІАГОНАЛЕЙ, ШВИДКО)
        if self.is_hunting and self.current_mode != "physics":
            mouse_pos = QCursor.pos()
            target_x = mouse_pos.x() - self.width() // 2
            target_y = mouse_pos.y() - self.height() // 2

            # Крок 1: Спочатку йдемо строго по горизонталі (вліво / вправо)
            if abs(self.x - target_x) > self.hunt_speed:
                if self.x < target_x:
                    self.x += self.hunt_speed
                    self.current_state = "walk_right"
                else:
                    self.x -= self.hunt_speed
                    self.current_state = "walk_left"
            # Крок 2: Коли вирівнялися по Х, йдемо по вертикалі (вгору / вниз), якщо режим дозволяє
            elif self.current_mode == "free_all" and abs(self.y - target_y) > self.hunt_speed:
                if self.y < target_y:
                    self.y += self.hunt_speed
                    self.current_state = "walk_backward"
                else:
                    self.y -= self.hunt_speed
                    self.current_state = "walk_forward"
            else:
                # Фінальне точне підтягування координат
                self.x = target_x
                if self.current_mode == "free_all":
                    self.y = target_y

            # Перевірка на упіймання курсора
            if abs(self.x - target_x) <= self.hunt_speed and (self.current_mode == "free_horiz" or abs(self.y - target_y) <= self.hunt_speed):
                self.is_hunting = False
                self.is_hanging = True
                self.current_state = "hang"
                self.shake_count = 0
                self.last_shake_pos = QCursor.pos()

        # ЗВИЧАЙНА ПРОГУЛЯНКА (З нормальною швидкістю)
        elif not self.is_falling:
            if self.current_state == "walk_right":
                self.x += self.normal_speed
            elif self.current_state == "walk_left":
                self.x -= self.normal_speed
            elif self.current_state == "walk_forward" and self.current_mode == "free_all":
                self.y -= self.normal_speed
            elif self.current_state == "walk_backward" and self.current_mode == "free_all":
                self.y += self.normal_speed

            if self.x < 0: 
                self.x = 0
                self.current_state = "idle"
            elif self.x > screen_geo.width() - self.width(): 
                self.x = screen_geo.width() - self.width()
                self.current_state = "idle"

            if self.y < 0:
                self.y = 0
                self.current_state = "idle"
            elif self.y > floor_y:
                self.y = floor_y
                self.current_state = "idle"

            if self.current_mode == "physics":
                self.y = floor_y
            
        self.move(int(self.x), int(self.y))
        self.current_frame += 1
        self.update_appearance()

    def change_behavior(self):
        if self.is_dragging or self.is_hanging or self.is_dropping or self.current_state == "sit":
            return
        
        if self.mouse_hunt_allowed and self.current_mode != "physics" and random.random() < 0.35:
            self.is_hunting = True
            self.behavior_timer.setInterval(random.randint(4000, 8000))
            return

        self.is_hunting = False
        if self.current_mode == "free_all":
            self.current_state = random.choice(["idle", "walk_left", "walk_right", "walk_forward", "walk_backward"])
        else:
            self.current_state = random.choice(["idle", "walk_left", "walk_right"])
        
        self.current_frame = 0
        self.behavior_timer.setInterval(random.randint(3000, 7000))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.is_falling = False
            self.is_hunting = False
            self.is_hanging = False
            self.is_dropping = False
            self.current_state = "idle"
            self.drag_offset = event.pos()
            self.last_mouse_pos = event.globalPosition().toPoint()
            self.vx = 0
            self.vy = 0
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.pos())

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
            if self.current_mode == "physics":
                screen_geo = QApplication.primaryScreen().geometry()
                if self.y < screen_geo.height() - self.height() - 5:
                    self.is_falling = True
                    self.vx = max(-15.0, min(15.0, self.vx))
                    self.vy = max(-20.0, min(15.0, self.vy))
            else:
                self.is_falling = False
                self.vx = 0
                self.vy = 0

    def show_context_menu(self, position):
        menu = QMenu(self)
        
        physics_action = QAction("Фізика та гравітація", self)
        physics_action.setCheckable(True)
        physics_action.setChecked(self.current_mode == "physics")
        physics_action.triggered.connect(lambda: self.set_mode("physics"))
        
        free_horiz_action = QAction("Вільна прогулянка (горизонтальна)", self)
        free_horiz_action.setCheckable(True)
        free_horiz_action.setChecked(self.current_mode == "free_horiz")
        free_horiz_action.triggered.connect(lambda: self.set_mode("free_horiz"))

        free_all_action = QAction("Прогулянка всюди", self)
        free_all_action.setCheckable(True)
        free_all_action.setChecked(self.current_mode == "free_all")
        free_all_action.triggered.connect(lambda: self.set_mode("free_all"))

        hunt_action = QAction("Дозволити ловити мишу", self)
        hunt_action.setCheckable(True)
        hunt_action.setChecked(self.mouse_hunt_allowed)
        hunt_action.triggered.connect(self.toggle_mouse_hunt)
        
        exit_action = QAction("Закрити програму", self)
        exit_action.triggered.connect(QApplication.quit)
        
        menu.addAction(physics_action)
        menu.addAction(free_horiz_action)
        menu.addAction(free_all_action)
        menu.addSeparator()
        menu.addAction(hunt_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        
        menu.exec(self.mapToGlobal(position))

    def set_mode(self, mode):
        self.current_mode = mode
        self.is_falling = False
        self.is_hunting = False
        self.is_hanging = False
        self.is_dropping = False
        self.current_state = "idle"
        self.current_frame = 0

    def toggle_mouse_hunt(self):
        self.mouse_hunt_allowed = not self.mouse_hunt_allowed
        if not self.mouse_hunt_allowed:
            self.is_hunting = False
            self.is_hanging = False
            self.is_dropping = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = AnyaPet()
    pet.show()
    sys.exit(app.exec())
