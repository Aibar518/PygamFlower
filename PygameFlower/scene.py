"""Модуль атмосферной ночной сцены: небо, луна, звезды, холмы и светлячки."""

import math
import random
import pygame
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_SKY_TOP,
    COLOR_SKY_BOTTOM,
    COLOR_MOON,
    COLOR_MOON_CRATER,
    COLOR_MOON_GLOW,
    COLOR_HILL_DISTANT,
    COLOR_HILL_MID,
    COLOR_HILL_NEAR,
    COLOR_GRASS_BASE,
    COLOR_GRASS_TIP,
    COLOR_FIREFLY_CORE,
    COLOR_FIREFLY_GLOW,
)


class Star:
    """Мерцающая и плавно дрейфующая звезда на ночном небе."""

    def __init__(self, x: float, y: float, size: float, period: float, phase: float, speed_layer: float) -> None:
        self.base_x = x
        self.base_y = y
        self.x = x
        self.y = y
        self.size = size
        self.period = period
        self.phase = phase
        self.brightness = 0.5
        # Скорость горизонтального дрейфа звезд (параллакс глубины: далекие медленнее, крупные чуть быстрее)
        self.drift_speed = speed_layer
        self.wobble_amp = random.uniform(2.0, 4.5)
        self.wobble_freq = random.uniform(0.4, 0.9)

    def update(self, dt: float, total_time: float) -> None:
        # Плавное мерцание от 0.35 до 1.0
        val = math.sin((total_time / self.period) * math.tau + self.phase)
        self.brightness = 0.35 + 0.65 * ((val + 1.0) / 2.0)

        # Непрерывный плавный дрейф звезд по небу
        self.base_x += self.drift_speed * dt
        if self.base_x > SCREEN_WIDTH + 15:
            self.base_x = -15

        # Микро-плавание в вертикальной плоскости (ощущение живого ночного воздуха)
        self.x = self.base_x
        self.y = self.base_y + math.sin(total_time * self.wobble_freq + self.phase) * self.wobble_amp


class Firefly:
    """Парящая пыльца/светлячок с органичным волнообразным движением и дыханием света."""

    def __init__(self, bounds_x: tuple[float, float], bounds_y: tuple[float, float]) -> None:
        self.bounds_x = bounds_x
        self.bounds_y = bounds_y
        self.x = random.uniform(*bounds_x)
        self.y = random.uniform(*bounds_y)
        self.vx = random.uniform(-8.0, 8.0)
        self.vy = random.uniform(-10.0, -2.0)
        self.base_glow_radius = random.uniform(4.0, 7.5)
        self.pulse_phase = random.uniform(0.0, math.tau)
        self.pulse_speed = random.uniform(1.2, 2.4)
        self.alpha_scale = random.uniform(0.55, 0.9)

    def update(self, dt: float, total_time: float) -> None:
        self.x += (self.vx + 12.0 * math.sin(total_time * 0.7 + self.pulse_phase)) * dt
        self.y += (self.vy + 6.0 * math.cos(total_time * 1.0 + self.pulse_phase)) * dt

        # Мягкий возврат в границы
        if self.x < self.bounds_x[0] - 20:
            self.x = self.bounds_x[1] + 10
        elif self.x > self.bounds_x[1] + 20:
            self.x = self.bounds_x[0] - 10

        if self.y < self.bounds_y[0] - 20:
            self.y = self.bounds_y[1] + 10
        elif self.y > self.bounds_y[1] + 20:
            self.y = self.bounds_y[0] - 10


class Scene:
    """Отвечает за фон, ночное небо, луну, холмы, траву, дрейфующие звезды и светлячков."""

    def __init__(self) -> None:
        self.total_time = 0.0

        # Кэшированные поверхности для высокой производительности (60+ FPS)
        self.static_backdrop = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.foreground_grass_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Луна: элегантный диск в верхнем левом секторе
        self.moon_center = (175, 130)
        self.moon_radius = 34

        # Предварительно сгенерированные кэш-спрайты для светлячков
        self.firefly_cache: dict[int, pygame.Surface] = {}

        # Динамические сущности
        self.stars: list[Star] = []
        self.fireflies: list[Firefly] = []

        self._init_stars()
        self._init_fireflies()
        self._bake_static_backdrop()
        self._bake_foreground_grass()
        self._bake_firefly_sprites()

    def _bake_static_backdrop(self) -> None:
        """Генерирует статичные слои: градиентное небо, ореолы, луну и силуэты холмов."""
        # 1. Плавный вертикальный градиент ночного неба
        for y in range(SCREEN_HEIGHT):
            t = y / (SCREEN_HEIGHT - 1)
            curve = t * t * (3.0 - 2.0 * t)
            r = int(COLOR_SKY_TOP[0] + (COLOR_SKY_BOTTOM[0] - COLOR_SKY_TOP[0]) * curve)
            g = int(COLOR_SKY_TOP[1] + (COLOR_SKY_BOTTOM[1] - COLOR_SKY_TOP[1]) * curve)
            b = int(COLOR_SKY_TOP[2] + (COLOR_SKY_BOTTOM[2] - COLOR_SKY_TOP[2]) * curve)
            pygame.draw.line(self.static_backdrop, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # 2. Мягкие рассеянные ореолы свечения луны
        mx, my = self.moon_center
        glow_steps = [
            (115, 0.03),
            (90, 0.06),
            (70, 0.10),
            (54, 0.16),
            (42, 0.28),
        ]
        glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        gr, gg, gb = COLOR_MOON_GLOW
        for radius, intensity in glow_steps:
            alpha = int(255 * intensity)
            pygame.draw.circle(glow_surf, (gr, gg, gb, alpha), (mx, my), radius)
        self.static_backdrop.blit(glow_surf, (0, 0))

        # 3. Тело луны
        pygame.draw.circle(self.static_backdrop, COLOR_MOON, (mx, my), self.moon_radius)

        # Детализированные мягкие кратеры
        craters = [
            (mx - 9, my - 8, 6),
            (mx + 8, my + 11, 7),
            (mx - 6, my + 10, 4),
            (mx + 11, my - 5, 5),
            (mx + 1, my + 1, 3),
        ]
        for cx, cy, cr in craters:
            pygame.draw.circle(self.static_backdrop, COLOR_MOON_CRATER, (cx, cy), cr)

        # 4. Многослойные холмы на заднем плане
        self._draw_hill_layer(
            self.static_backdrop,
            COLOR_HILL_DISTANT,
            base_y=425,
            amplitude=40,
            freq=0.004,
            phase=0.8,
        )
        self._draw_hill_layer(
            self.static_backdrop,
            COLOR_HILL_MID,
            base_y=475,
            amplitude=32,
            freq=0.0055,
            phase=2.4,
        )
        self._draw_hill_layer(
            self.static_backdrop,
            COLOR_HILL_NEAR,
            base_y=535,
            amplitude=22,
            freq=0.007,
            phase=4.1,
        )

    def _draw_hill_layer(
        self, surface: pygame.Surface, color: tuple[int, int, int], base_y: float, amplitude: float, freq: float, phase: float
    ) -> None:
        """Рисует плавную кривую холма с углублением в центре для будущего цветка."""
        points = [(0, SCREEN_HEIGHT)]
        step = 6
        for x in range(0, SCREEN_WIDTH + step, step):
            curve = (
                math.sin(x * freq + phase) * amplitude
                + math.sin(x * freq * 2.1 + phase * 1.4) * (amplitude * 0.28)
            )
            center_dist = abs(x - SCREEN_WIDTH / 2) / (SCREEN_WIDTH / 2)
            elevation = (center_dist - 0.5) * 14.0
            y = base_y + curve + elevation
            points.append((x, int(y)))
        points.append((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.draw.polygon(surface, color, points)

    def _bake_foreground_grass(self) -> None:
        """Кэширует силуэты травинок на переднем крае поля."""
        random.seed(1337)
        pygame.draw.rect(
            self.foreground_grass_surface,
            COLOR_GRASS_BASE,
            (0, SCREEN_HEIGHT - 32, SCREEN_WIDTH, 32),
        )

        for x in range(4, SCREEN_WIDTH - 4, 3):
            dist_to_center = abs(x - SCREEN_WIDTH / 2)
            max_h = 16.0 if dist_to_center < 170 else 32.0
            h = random.uniform(8.0, max_h)
            bend = random.uniform(-5.0, 5.0)
            base_y = SCREEN_HEIGHT - random.uniform(20.0, 28.0)

            p1 = (x - 2, base_y + 12)
            p2 = (x + 2, base_y + 12)
            p3 = (x + bend, base_y - h)

            grass_shade = (
                int(COLOR_GRASS_TIP[0] + random.uniform(-2, 3)),
                int(COLOR_GRASS_TIP[1] + random.uniform(-2, 5)),
                int(COLOR_GRASS_TIP[2] + random.uniform(-2, 4)),
            )
            pygame.draw.polygon(self.foreground_grass_surface, grass_shade, [p1, p2, p3])
        random.seed()

    def _bake_firefly_sprites(self) -> None:
        """Предварительно кэширует спрайты частиц разного радиуса для максимального FPS."""
        for r_int in range(3, 11):
            dim = r_int * 2 + 4
            surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
            c = dim // 2

            for step in range(r_int, 0, -1):
                ratio = step / r_int
                alpha = int(45 * (1.0 - ratio))
                pygame.draw.circle(surf, (*COLOR_FIREFLY_GLOW, alpha), (c, c), step)

            core_r = max(1, int(r_int * 0.35))
            pygame.draw.circle(surf, (*COLOR_FIREFLY_CORE, 210), (c, c), core_r)
            self.firefly_cache[r_int] = surf

    def _init_stars(self) -> None:
        """Создает распределенные звезды с многослойной скоростью дрейфа (эффект параллакса)."""
        random.seed(42)
        count = 75
        for _ in range(count):
            x = random.uniform(12, SCREEN_WIDTH - 12)
            y = random.uniform(12, 360)

            dist_moon = math.hypot(x - self.moon_center[0], y - self.moon_center[1])
            if dist_moon < self.moon_radius + 18:
                continue

            size = random.choice([1.0, 1.0, 1.0, 1.5, 2.0])
            period = random.uniform(1.8, 4.0)
            phase = random.uniform(0.0, math.tau)
            # Различные скорости медленного космического дрейфа: 1.5 до 4.5 px/sec
            speed_layer = random.uniform(1.8, 4.8) if size > 1.2 else random.uniform(0.8, 2.2)
            self.stars.append(Star(x, y, size, period, phase, speed_layer))
        random.seed()

    def _init_fireflies(self) -> None:
        """Создает парящие светящиеся споры/светлячки в воздухе вокруг сцены."""
        count = 20
        bounds_x = (30.0, float(SCREEN_WIDTH - 30))
        bounds_y = (310.0, float(SCREEN_HEIGHT - 40))
        for _ in range(count):
            self.fireflies.append(Firefly(bounds_x, bounds_y))

    def update(self, dt: float) -> None:
        """Обновление анимации мерцания и непрерывного дрейфа звезд, а также светлячков."""
        self.total_time += dt

        for star in self.stars:
            star.update(dt, self.total_time)

        for firefly in self.fireflies:
            firefly.update(dt, self.total_time)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовка всех слоев окружения на целевую поверхность."""
        # 1. Фоновый статичный слой: градиентное небо, луна, ореолы, холмы
        surface.blit(self.static_backdrop, (0, 0))

        # 2. Дрейфующие и мерцающие звезды
        for star in self.stars:
            alpha = int(star.brightness * 240)
            color = (alpha, alpha, min(255, int(alpha * 1.12)))
            if star.size <= 1.0:
                surface.set_at((int(star.x), int(star.y)), color)
            else:
                s_rad = int(star.size)
                pygame.draw.circle(surface, color, (int(star.x), int(star.y)), s_rad)

        # 3. Трава на переднем плане
        surface.blit(self.foreground_grass_surface, (0, 0))

        # 4. Светлячки / магические частицы
        for ff in self.fireflies:
            pulse = (math.sin(self.total_time * ff.pulse_speed + ff.pulse_phase) + 1.0) / 2.0
            r_int = int(ff.base_glow_radius * (0.8 + 0.35 * pulse))
            r_clamped = max(3, min(10, r_int))

            sprite = self.firefly_cache.get(r_clamped)
            if sprite is not None:
                sx = int(ff.x) - sprite.get_width() // 2
                sy = int(ff.y) - sprite.get_height() // 2
                surface.blit(sprite, (sx, sy), special_flags=pygame.BLEND_ADD)
