"""Модуль отдельного лепестка восточной лилии (Oriental Stargazer Lily)."""

import math
import random
import pygame


class Petal:
    """Класс лепестка лилии: хранит геометрию, текстуру и динамическую физику падения."""

    def __init__(
        self,
        index: int,
        angle_deg: float,
        length: float = 195.0,
        width: float = 84.0,
        curl: float = 0.0,
        layer: str = "outer",
    ) -> None:
        self.index = index
        self.angle_deg = angle_deg
        self.length = length
        self.width = width
        self.curl = curl
        self.layer = layer

        # Состояние отрыва и физики падения
        self.detached = False
        self.landed = False
        self.fall_time = 0.0

        # Позиция и смещения
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.rotation_offset = 0.0

        # Физические параметры динамичного падения
        self.vx = 0.0
        self.vy = 0.0
        self.gravity = 1250.0        # Увеличенная динамичная гравитация для времени падения ~0.65-0.75с
        self.max_fall_speed = 780.0  # Предельная скорость
        self.rot_speed = 0.0         # Скорость вращения
        self.drift_freq = 0.0        # Частота покачивания
        self.drift_amp = 0.0         # Амплитуда покачивания
        self.drift_phase = 0.0

        self.surface: pygame.Surface | None = None
        self.pivot: tuple[int, int] = (0, 0)
        self._build_surface()

    def _build_surface(self) -> None:
        """Создает спрайт лепестка Oriental Stargazer Lily с градиентом, жилкой и крапинками."""
        pivot_depth = 28.0
        surf_w = int(self.length + pivot_depth + 40)
        surf_h = int(self.width * 2.3 + 40)
        raw_surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        center_y = surf_h // 2
        base_x = 10.0

        num_segments = 44
        top_points: list[tuple[float, float]] = []
        bot_points: list[tuple[float, float]] = []

        rand = random.Random(400 + self.index * 53)
        total_len = self.length + pivot_depth

        for i in range(num_segments + 1):
            t = i / num_segments
            x = base_x + t * total_len

            w_norm = math.sin((t ** 0.65) * math.pi) * (1.0 - 0.14 * t)
            base_w = (self.width * 0.5) * w_norm

            wave = math.sin(t * 13.5 + self.index * 1.6) * (2.8 * (1.0 - t * 0.45))
            curled_y = center_y + (t * t * self.curl)

            top_points.append((x, curled_y - base_w - wave))
            bot_points.append((x, curled_y + base_w + wave))

        # 1. Многослойный градиент
        layers_data = [
            (1.00, 1.00, (255, 248, 252), 255),  # Внешний кант: белоснежно-розовый
            (0.92, 0.98, (255, 218, 235), 255),  # Нежно-розовая кайма
            (0.81, 0.95, (250, 142, 185), 255),  # Яркий розовый
            (0.66, 0.91, (235, 62, 130), 255),   # Насыщенная малина
            (0.48, 0.85, (205, 20, 88), 255),    # Глубокий малиновый
            (0.32, 0.76, (170, 10, 68), 255),    # Пурпурно-рубиновый
            (0.18, 0.64, (135, 6, 52), 255),     # Тёмное ядро
        ]

        for scale_w, scale_l, col, a in layers_data:
            layer_pts: list[tuple[float, float]] = []
            for pt in top_points:
                dx = pt[0] - base_x
                dy = pt[1] - center_y
                layer_pts.append((base_x + dx * scale_l, center_y + dy * scale_w))
            layer_pts.append((base_x + total_len * scale_l, center_y + self.curl * scale_l))
            for pt in reversed(bot_points):
                dx = pt[0] - base_x
                dy = pt[1] - center_y
                layer_pts.append((base_x + dx * scale_l, center_y + dy * scale_w))
            layer_pts.append((base_x, center_y))

            pygame.draw.polygon(raw_surf, (*col, a), layer_pts)

        # 2. Нежный салатово-желтый нектарный желобок
        throat_len = pivot_depth + self.length * 0.16
        green_throat_pts = [
            (base_x, center_y),
            (base_x + throat_len * 0.45, center_y - self.width * 0.13),
            (base_x + throat_len, center_y),
            (base_x + throat_len * 0.45, center_y + self.width * 0.13),
        ]
        pygame.draw.polygon(raw_surf, (155, 218, 80, 230), green_throat_pts)
        throat_core = [
            (base_x, center_y),
            (base_x + throat_len * 0.6, center_y - self.width * 0.07),
            (base_x + throat_len * 0.9, center_y),
            (base_x + throat_len * 0.6, center_y + self.width * 0.07),
        ]
        pygame.draw.polygon(raw_surf, (198, 248, 105, 245), throat_core)

        # 3. Рельефная центральная жилка
        rib_points = []
        for i in range(30):
            t = i / 29.0
            rx = base_x + t * (total_len * 0.94)
            ry = center_y + (t * t * self.curl)
            rib_points.append((rx, ry))
        pygame.draw.lines(raw_surf, (115, 5, 42, 175), False, rib_points, 3)
        pygame.draw.lines(raw_surf, (255, 195, 225, 185), False, rib_points, 1)

        # 4. Выпуклые темные папиллы (spots)
        spot_count = 60
        for _ in range(spot_count):
            t_len = rand.uniform(0.18, 0.78)
            sx = base_x + t_len * total_len

            max_w_at_t = (self.width * 0.44) * math.sin((t_len ** 0.65) * math.pi)
            spread = rand.gauss(0, max_w_at_t * 0.38)
            spread = max(-max_w_at_t, min(max_w_at_t, spread))
            sy = center_y + (t_len * t_len * self.curl) + spread

            spot_radius = rand.uniform(1.2, 2.6)
            spot_color = (rand.randint(90, 120), rand.randint(5, 15), rand.randint(28, 48))
            pygame.draw.circle(raw_surf, spot_color, (int(sx), int(sy)), int(spot_radius))
            if spot_radius > 1.8:
                pygame.draw.circle(raw_surf, (230, 125, 165), (int(sx), int(sy - 0.6)), 1)

        self.surface = raw_surf
        self.pivot = (int(base_x + pivot_depth), int(center_y))

    def detach(self) -> None:
        """Мгновенно запускает отрыв лепестка с энергичным импульсом."""
        if self.detached:
            return

        self.detached = True
        self.landed = False
        self.fall_time = 0.0

        rad = math.radians(self.angle_deg)
        base_dir_x = -1.0 if math.cos(rad) < 0 else 1.0

        # Энергичный начальный импульс отрыва
        self.vx = base_dir_x * random.uniform(70.0, 120.0)
        # Начальная скорость направлена слегка вниз в сочетании с ориентацией
        self.vy = -math.sin(rad) * 45.0 + random.uniform(25.0, 55.0)

        # Динамичное естественное вращение в сторону падения
        self.rot_speed = base_dir_x * random.uniform(85.0, 145.0)
        self.drift_freq = random.uniform(3.0, 5.0)
        self.drift_amp = random.uniform(70.0, 110.0)
        self.drift_phase = random.uniform(0.0, math.tau)

    def reset(self) -> None:
        """Сброс лепестка в исходное закрепленное состояние на цветке."""
        self.detached = False
        self.landed = False
        self.fall_time = 0.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.rotation_offset = 0.0
        self.vx = 0.0
        self.vy = 0.0

    def update(self, dt: float, ground_y: float = 620.0, center_y: float = 268.0) -> None:
        """Обновление физики движения падающего лепестка с учетом delta time."""
        if not self.detached or self.landed:
            return

        self.fall_time += dt

        # 1. Гравитационное ускорение
        self.vy = min(self.max_fall_speed, self.vy + self.gravity * dt)

        # 2. Волнообразное горизонтальное покачивание в воздухе
        sway_speed = math.sin(self.fall_time * self.drift_freq + self.drift_phase) * self.drift_amp

        # 3. Интегрирование координат
        self.offset_x += (self.vx + sway_speed) * dt
        self.offset_y += self.vy * dt

        # 4. Вращение в воздухе с органичным раскачиванием
        wobble = math.cos(self.fall_time * self.drift_freq + self.drift_phase) * 25.0
        self.rotation_offset += (self.rot_speed * dt) + (wobble * dt)

        # 5. Мягкое оседание в траву у нижнего края экрана
        current_y = center_y + self.offset_y
        if current_y >= ground_y:
            self.landed = True
            self.offset_y = ground_y - center_y
            self.vx = 0.0
            self.vy = 0.0

    def draw(self, target_surface: pygame.Surface, center_pos: tuple[float, float]) -> None:
        """Отрисовывает лепесток с точным вращением вокруг пивота в центре цветка."""
        if self.surface is None:
            return

        total_angle = self.angle_deg + self.rotation_offset
        rotated_surf = pygame.transform.rotate(self.surface, total_angle)

        center_pt = pygame.math.Vector2(center_pos[0] + self.offset_x, center_pos[1] + self.offset_y)

        orig_rect = self.surface.get_rect(
            topleft=(center_pt.x - self.pivot[0], center_pt.y - self.pivot[1])
        )

        offset = pygame.math.Vector2(orig_rect.center) - center_pt
        rotated_offset = offset.rotate(-total_angle)

        new_rect_center = center_pt + rotated_offset
        rot_rect = rotated_surf.get_rect(center=(int(new_rect_center.x), int(new_rect_center.y)))

        target_surface.blit(rotated_surf, rot_rect.topleft)
