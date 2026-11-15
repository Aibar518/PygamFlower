"""Модуль визуальных эффектов: романтичные светящиеся сердечки финальной анимации."""

import math
import random
import pygame


class Heart:
    """Отдельное светящееся сердечко с физикой парения, вращением, покачиванием и затуханием."""

    def __init__(self, x: float, y: float, size: float, color_theme: str) -> None:
        self.x = x
        self.y = y
        self.size = size
        self.color_theme = color_theme  # 'pale_pink', 'magenta', 'rose'
        self.age = 0.0
        self.lifetime = random.uniform(3.6, 5.2)
        self.dead = False

        # Скорость и траектория движения: свободный подъем с мягким боковым разлетом
        self.vy = -random.uniform(42.0, 72.0)
        self.vx = random.uniform(-28.0, 28.0)
        self.sway_freq = random.uniform(1.8, 2.8)
        self.sway_amp = random.uniform(25.0, 50.0)
        self.sway_phase = random.uniform(0.0, math.tau)

        # Вращение
        self.angle = random.uniform(-18.0, 18.0)
        self.rot_speed = random.uniform(-16.0, 16.0)

        # Цвета в гамме Oriental Lily (элегантные, без пересветов)
        if color_theme == "pale_pink":
            self.core_col = (255, 225, 238)
            self.glow_col = (245, 140, 190)
        elif color_theme == "magenta":
            self.core_col = (255, 165, 205)
            self.glow_col = (220, 50, 120)
        else:  # rose
            self.core_col = (248, 125, 175)
            self.glow_col = (185, 25, 90)

        self.base_surface = self._build_heart_surface()

    def _build_heart_surface(self) -> pygame.Surface:
        """Генерирует поверхность сердечка с аккуратным полупрозрачным ореолом свечения."""
        dim = int(self.size * 2.8 + 20)
        surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
        center_x = dim // 2
        center_y = int(dim * 0.48)

        # Параметрическое уравнение формы сердца
        num_pts = 32
        raw_pts = []
        for i in range(num_pts):
            t = (i / num_pts) * math.tau
            hx = 16.0 * (math.sin(t) ** 3)
            hy = -(13.0 * math.cos(t) - 5.0 * math.cos(2.0 * t) - 2.0 * math.cos(3.0 * t) - math.cos(4.0 * t))
            raw_pts.append((hx, hy))

        scale = self.size / 17.0

        # Внешний ореол свечения (деликатная полупрозрачность)
        glow_pts = [(center_x + hx * scale * 1.25, center_y + hy * scale * 1.25) for hx, hy in raw_pts]
        pygame.draw.polygon(surf, (*self.glow_col, 50), glow_pts)

        # Средний мягкий слой
        mid_pts = [(center_x + hx * scale * 1.1, center_y + hy * scale * 1.1) for hx, hy in raw_pts]
        pygame.draw.polygon(surf, (*self.glow_col, 110), mid_pts)

        # Тело сердечка
        core_pts = [(center_x + hx * scale, center_y + hy * scale) for hx, hy in raw_pts]
        pygame.draw.polygon(surf, (*self.core_col, 215), core_pts)

        # Световой блик
        highlight_x = center_x - int(self.size * 0.35)
        highlight_y = center_y - int(self.size * 0.35)
        hl_rad = max(1, int(self.size * 0.15))
        pygame.draw.circle(surf, (255, 255, 255, 170), (highlight_x, highlight_y), hl_rad)

        return surf

    def update(self, dt: float) -> None:
        """Обновление траектории, времени жизни и плавного исчезновения."""
        self.age += dt
        if self.age >= self.lifetime:
            self.dead = True
            return

        sway = math.sin(self.age * self.sway_freq + self.sway_phase) * self.sway_amp
        self.x += (self.vx + sway) * dt
        self.y += self.vy * dt
        self.angle += self.rot_speed * dt

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовка сердечка со стандартным Alpha-blending для сохранения естественных тонов."""
        if self.dead:
            return

        progress = self.age / self.lifetime
        if progress < 0.15:
            alpha = progress / 0.15
            scale_mod = 0.65 + 0.35 * (progress / 0.15)
        elif progress > 0.65:
            alpha = (1.0 - progress) / 0.35
            scale_mod = 1.0 + 0.08 * (progress - 0.65)
        else:
            alpha = 1.0
            scale_mod = 1.0

        alpha_int = max(0, min(255, int(alpha * 230)))
        if alpha_int <= 2:
            return

        scaled_w = int(self.base_surface.get_width() * scale_mod)
        scaled_h = int(self.base_surface.get_height() * scale_mod)
        scaled_surf = pygame.transform.smoothscale(self.base_surface, (scaled_w, scaled_h))
        rotated_surf = pygame.transform.rotate(scaled_surf, self.angle)

        rotated_surf.set_alpha(alpha_int)
        rect = rotated_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_surf, rect.topleft)


class EffectsManager:
    """Управляет созданием, жизненным циклом и рендерингом сердечек финальной сцены."""

    def __init__(self) -> None:
        self.hearts: list[Heart] = []
        self.is_active = False
        self.spawn_timer = 0.0
        self.spawn_interval = 0.28  # умеренная частота появления
        self.total_spawned = 0
        self.max_hearts_to_spawn = 36  # легкий воздушный поток
        self.center_emitter: tuple[float, float] = (500.0, 270.0)

    def start(self, emitter_pos: tuple[float, float]) -> None:
        """Запускает финальную анимацию сердечек от центра цветка."""
        self.center_emitter = emitter_pos
        self.is_active = True
        self.spawn_timer = 0.0
        self.total_spawned = 0
        self.hearts.clear()

        # Стартовый легкий импульс
        for _ in range(4):
            self._spawn_single_heart()

    def reset(self) -> None:
        """Сброс и очистка всех сердечек."""
        self.hearts.clear()
        self.is_active = False
        self.spawn_timer = 0.0
        self.total_spawned = 0

    def _spawn_single_heart(self) -> None:
        """Создает одно уникальное сердечко около цветка."""
        ex, ey = self.center_emitter
        spawn_x = ex + random.uniform(-55.0, 55.0)
        spawn_y = ey + random.uniform(-30.0, 30.0)

        size = random.choice([9.0, 12.0, 15.0, 18.0, 21.0])
        theme = random.choice(["pale_pink", "magenta", "magenta", "rose"])
        self.hearts.append(Heart(spawn_x, spawn_y, size, theme))
        self.total_spawned += 1

    def update(self, dt: float) -> None:
        """Обновление движения частиц и генерация новых сердечек."""
        if self.is_active and self.total_spawned < self.max_hearts_to_spawn:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_timer = 0.0
                self._spawn_single_heart()

        for heart in self.hearts:
            heart.update(dt)

        self.hearts = [h for h in self.hearts if not h.dead]

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовка всех активных сердечек поверх сцены."""
        for heart in self.hearts:
            heart.draw(surface)
