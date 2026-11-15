"""Модуль розовой восточной лилии (Oriental Stargazer Lily)."""

import math
import random
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from petal import Petal


class Lily:
    """Класс лилии: управляет стеблем, листьями, 6 лепестками, органичным цветоложем,
    живым покачиванием от ветра и физической отдачей при клике.
    """

    def __init__(self, center_pos: tuple[float, float] | None = None) -> None:
        if center_pos is None:
            self.base_center_pos = (SCREEN_WIDTH * 0.52, SCREEN_HEIGHT * 0.42)
        else:
            self.base_center_pos = center_pos

        self.center_pos = self.base_center_pos

        # Физическая отдача цветка при отрывании лепестка
        self.recoil_offset_x = 0.0
        self.recoil_offset_y = 0.0
        self.recoil_angle = 0.0
        self.recoil_timer = 0.0
        self.recoil_duration = 0.32
        self.recoil_active = False
        self.recoil_impulse_x = 0.0
        self.recoil_impulse_y = 0.0

        # Фоновое органичное покачивание от ветра (Sway wind animation)
        self.wind_offset_x = 0.0
        self.wind_offset_y = 0.0
        self.wind_angle = 0.0
        self.wind_speed_mult = 1.0

        self.stem_points: list[tuple[float, float]] = []
        self.leaves: list[dict] = []
        self.petals: list[Petal] = []
        self.stamens: list[dict] = []
        self.pistil: dict = {}

        self.total_time = 0.0

        self._init_stem_and_leaves()
        self._init_petals()
        self._init_center_organs()

    def _init_stem_and_leaves(self) -> None:
        """Создает точки плавного изгиба стебля и ланцетовидных листьев."""
        cx, cy = self.base_center_pos
        base_ground_y = SCREEN_HEIGHT - 16
        self.stem_points = []
        steps = 42
        for i in range(steps + 1):
            t = i / steps
            sy = cy + t * (base_ground_y - cy)
            sx = cx - 20.0 * math.sin(t * math.pi * 0.92) - (t * 6.0)
            self.stem_points.append((sx, sy))

        # Листья Oriental Lily с индивидуальными параметрами податливости ветру
        self.leaves.append({
            "start": self.stem_points[13],
            "ctrl": (self.stem_points[13][0] - 110, self.stem_points[13][1] - 30),
            "end": (self.stem_points[13][0] - 180, self.stem_points[13][1] + 35),
            "width": 20.0,
            "color_base": (45, 95, 52),
            "color_mid": (62, 132, 72),
            "color_high": (95, 175, 105),
            "wind_phase": 0.4,
            "wind_flex": 6.5,
        })

        self.leaves.append({
            "start": self.stem_points[20],
            "ctrl": (self.stem_points[20][0] + 115, self.stem_points[20][1] - 22),
            "end": (self.stem_points[20][0] + 180, self.stem_points[20][1] + 45),
            "width": 22.0,
            "color_base": (38, 85, 46),
            "color_mid": (55, 120, 65),
            "color_high": (85, 160, 95),
            "wind_phase": 1.8,
            "wind_flex": 5.0,
        })

        self.leaves.append({
            "start": self.stem_points[29],
            "ctrl": (self.stem_points[29][0] - 100, self.stem_points[29][1] + 12),
            "end": (self.stem_points[29][0] - 165, self.stem_points[29][1] + 78),
            "width": 19.0,
            "color_base": (32, 72, 40),
            "color_mid": (48, 108, 58),
            "color_high": (75, 145, 85),
            "wind_phase": 3.1,
            "wind_flex": 3.5,
        })

    def _init_petals(self) -> None:
        """Создает 6 отдельных лепестков лилии:
        - 3 внешних: индексы 0, 2, 4 под углами 30°, 150°, 270°
        - 3 внутренних: индексы 1, 3, 5 под углами 90°, 210°, 330°
        """
        configs = [
            (0, 30.0, 190.0, 75.0, 4.0, "outer"),    # Вверх-вправо
            (1, 90.0, 198.0, 88.0, -3.0, "inner"),   # Ровно вверх
            (2, 150.0, 190.0, 75.0, -5.0, "outer"),  # Вверх-влево
            (3, 210.0, 188.0, 86.0, 4.0, "inner"),   # Вниз-влево
            (4, 270.0, 182.0, 74.0, 4.0, "outer"),   # Ровно вниз
            (5, 330.0, 192.0, 88.0, -4.0, "inner"),  # Вниз-вправо
        ]

        self.petals = [
            Petal(
                index=cfg[0],
                angle_deg=cfg[1],
                length=cfg[2],
                width=cfg[3],
                curl=cfg[4],
                layer=cfg[5],
            )
            for cfg in configs
        ]

    def _init_center_organs(self) -> None:
        """Создает компактные, изящные тычинки и центральный пестик."""
        stamen_angles = [0.0, 60.0, 120.0, 180.0, 240.0, 300.0]
        self.stamens = []
        for i, ang in enumerate(stamen_angles):
            rad = math.radians(ang)
            filament_len = random.uniform(34.0, 42.0)
            bend_rad = math.radians(ang + random.uniform(-10.0, 10.0))
            ctrl_dist = filament_len * 0.55

            ctrl_x = math.cos(bend_rad) * ctrl_dist
            ctrl_y = -math.sin(bend_rad) * ctrl_dist

            tip_x = math.cos(rad) * filament_len
            tip_y = -math.sin(rad) * filament_len

            self.stamens.append({
                "tip": (tip_x, tip_y),
                "ctrl": (ctrl_x, ctrl_y),
                "angle": ang + 90.0,
                "radius": 4.5,
                "length": 8.0,
            })

        pistil_rad = math.radians(80.0)
        pistil_len = 36.0
        self.pistil = {
            "tip": (math.cos(pistil_rad) * pistil_len, -math.sin(pistil_rad) * pistil_len),
            "ctrl": (math.cos(math.radians(65.0)) * 20.0, -math.sin(math.radians(65.0)) * 20.0),
        }

    def trigger_recoil(self, petal_angle_deg: float) -> None:
        """Запускает упругую реакцию отдачи цветка в направлении, противоположном отрыву лепестка."""
        rad = math.radians(petal_angle_deg)
        impulse = 14.0
        self.recoil_impulse_x = -math.cos(rad) * impulse
        self.recoil_impulse_y = math.sin(rad) * impulse * 0.7 + 5.0
        self.recoil_timer = 0.0
        self.recoil_active = True

    def detach_petal(self, index: int) -> bool:
        """Отсоединяет лепесток по индексу, запуская его физику падения и отдачу цветка."""
        if 0 <= index < len(self.petals):
            petal = self.petals[index]
            if not petal.detached:
                petal.detach()
                self.trigger_recoil(petal.angle_deg)
                return True
        return False

    def reset(self) -> None:
        """Сбрасывает все лепестки и состояние цветка в исходное положение."""
        for petal in self.petals:
            petal.reset()
        self.recoil_active = False
        self.recoil_timer = 0.0
        self.recoil_offset_x = 0.0
        self.recoil_offset_y = 0.0
        self.wind_offset_x = 0.0
        self.wind_offset_y = 0.0
        self.center_pos = self.base_center_pos

    def get_attached_petals_count(self) -> int:
        """Возвращает количество оставшихся на цветке лепестков."""
        return sum(1 for p in self.petals if not p.detached)

    def update(self, dt: float) -> None:
        """Обновление ветра, затухающей отдачи и физики лепестков."""
        self.total_time += dt

        # 1. Живое органичное покачивание от ветра (комбинация гармоник разной частоты)
        t = self.total_time
        # Основная плавная волна + вторичный дыхательный ветерок
        wind_sway = math.sin(t * 1.1) * 7.5 + math.sin(t * 1.85 + 0.6) * 3.2
        wind_bob = math.cos(t * 2.2) * 1.4  # легкое вертикальное дыхание цветка

        self.wind_offset_x = wind_sway
        self.wind_offset_y = wind_bob

        # 2. Упругая отдача при клике с затуханием (damped oscillation)
        if self.recoil_active:
            self.recoil_timer += dt
            progress = self.recoil_timer / self.recoil_duration
            if progress >= 1.0:
                self.recoil_active = False
                self.recoil_offset_x = 0.0
                self.recoil_offset_y = 0.0
            else:
                decay = math.exp(-7.0 * progress)
                osc = math.cos(progress * math.pi * 3.5)
                self.recoil_offset_x = self.recoil_impulse_x * osc * decay
                self.recoil_offset_y = self.recoil_impulse_y * osc * decay

        # Итоговая позиция цветка: базовая + ветер + отдача при клике
        self.center_pos = (
            self.base_center_pos[0] + self.wind_offset_x + self.recoil_offset_x,
            self.base_center_pos[1] + self.wind_offset_y + self.recoil_offset_y,
        )

        ground_limit = SCREEN_HEIGHT - 35.0
        for petal in self.petals:
            petal.update(dt, ground_y=ground_limit, center_y=self.base_center_pos[1])

    def _draw_stem_and_leaves(self, surface: pygame.Surface) -> None:
        """Отрисовывает стебель и листья с градиентным объемом.
        Стебель плавно изгибается от неподвижного корня в земле до плавно покачивающейся верхушки.
        """
        current_stem = []
        total_head_x = self.wind_offset_x + self.recoil_offset_x
        total_head_y = self.wind_offset_y + self.recoil_offset_y

        num_pts = len(self.stem_points)
        for i, pt in enumerate(self.stem_points):
            # Изгиб стебля: внизу (земля, i=num_pts-1) смещение = 0, вверху (i=0) смещение = 100%
            bend_ratio = (1.0 - (i / (num_pts - 1))) ** 1.6
            dx = total_head_x * bend_ratio
            dy = total_head_y * bend_ratio
            current_stem.append((pt[0] + dx, pt[1] + dy))

        # Отрисовка листьев с согласованным движением вслед за стеблем и ветром
        for leaf in self.leaves:
            # Находим текущую позицию точки крепления на изогнутом стебле
            p_start_orig = leaf["start"]
            # Ищем ближайший индекс стебля для синхронизации смещения
            start_bend = 0.55
            for i, spt in enumerate(self.stem_points):
                if math.hypot(spt[0] - p_start_orig[0], spt[1] - p_start_orig[1]) < 2.0:
                    start_bend = (1.0 - (i / (num_pts - 1))) ** 1.6
                    break

            base_dx = total_head_x * start_bend
            base_dy = total_head_y * start_bend

            # Дополнительное свободное трепетание кончика листа на ветру
            leaf_sway = math.sin(self.total_time * 1.7 + leaf["wind_phase"]) * leaf["wind_flex"]

            p_start = (leaf["start"][0] + base_dx, leaf["start"][1] + base_dy)
            p_ctrl = (leaf["ctrl"][0] + base_dx + leaf_sway * 0.5, leaf["ctrl"][1] + base_dy)
            p_end = (leaf["end"][0] + base_dx + leaf_sway, leaf["end"][1] + base_dy + leaf_sway * 0.25)
            w = leaf["width"]

            poly_top = []
            poly_bot = []
            steps = 22
            for i in range(steps + 1):
                t = i / steps
                inv = 1.0 - t
                bx = inv * inv * p_start[0] + 2.0 * inv * t * p_ctrl[0] + t * t * p_end[0]
                by = inv * inv * p_start[1] + 2.0 * inv * t * p_ctrl[1] + t * t * p_end[1]

                dx = 2.0 * inv * (p_ctrl[0] - p_start[0]) + 2.0 * t * (p_end[0] - p_ctrl[0])
                dy = 2.0 * inv * (p_ctrl[1] - p_start[1]) + 2.0 * t * (p_end[1] - p_ctrl[1])
                length = math.hypot(dx, dy) or 1.0
                nx = -dy / length
                ny = dx / length

                curr_w = math.sin(t * math.pi) * (w * 0.5)
                poly_top.append((bx + nx * curr_w, by + ny * curr_w))
                poly_bot.append((bx - nx * curr_w, by - ny * curr_w))

            leaf_poly = poly_top + list(reversed(poly_bot))
            pygame.draw.polygon(surface, leaf["color_base"], leaf_poly)
            inner_poly = [
                (
                    (pt[0] - p_start[0]) * 0.85 + p_start[0],
                    (pt[1] - p_start[1]) * 0.85 + p_start[1],
                )
                for pt in leaf_poly
            ]
            pygame.draw.polygon(surface, leaf["color_mid"], inner_poly)

            mid_pts = [((pt1[0] + pt2[0]) * 0.5, (pt1[1] + pt2[1]) * 0.5) for pt1, pt2 in zip(poly_top, poly_bot)]
            pygame.draw.lines(surface, leaf["color_high"], False, mid_pts, 2)

        # Стебель
        pygame.draw.lines(surface, (20, 48, 25), False, current_stem, 11)
        pygame.draw.lines(surface, (45, 105, 50), False, current_stem, 9)
        highlight_pts = [(pt[0] - 1.5, pt[1]) for pt in current_stem]
        pygame.draw.lines(surface, (88, 175, 95), False, highlight_pts, 3)

    def _draw_receptacle_and_scars(self, surface: pygame.Surface) -> None:
        """Отрисовывает органичное природное цветоложе (receptacle) и аккуратные округлые
        основания в местах, откуда оторвались лепестки.
        """
        cx, cy = self.center_pos

        # Зелёные чашелистики цветоложа
        for petal in self.petals:
            rad = math.radians(petal.angle_deg)
            base_dist = 22.0
            bx = cx + math.cos(rad) * base_dist
            by = cy - math.sin(rad) * base_dist

            if petal.detached:
                pygame.draw.circle(surface, (38, 75, 42), (int(bx), int(by)), 9)
                pygame.draw.circle(surface, (140, 195, 90), (int(bx), int(by)), 6)
                pygame.draw.circle(surface, (220, 240, 160), (int(bx), int(by)), 3)

        # Центральный зеленый купол цветоложа
        pygame.draw.circle(surface, (28, 62, 32), (int(cx), int(cy)), 24)
        pygame.draw.circle(surface, (55, 125, 58), (int(cx), int(cy)), 20)
        pygame.draw.circle(surface, (115, 185, 80), (int(cx), int(cy)), 15)
        pygame.draw.circle(surface, (175, 230, 110), (int(cx), int(cy)), 9)
        pygame.draw.circle(surface, (230, 255, 165), (int(cx), int(cy)), 4)

    def _draw_stamens_and_pistil(self, surface: pygame.Surface) -> None:
        """Отрисовывает аккуратные нежные тычинки и пестик лилии с природными округлыми пыльниками."""
        cx, cy = self.center_pos

        # Центральный пестик
        stigma_x = cx + self.pistil["tip"][0]
        stigma_y = cy + self.pistil["tip"][1]
        ctrl_x = cx + self.pistil["ctrl"][0]
        ctrl_y = cy + self.pistil["ctrl"][1]

        pistil_pts = []
        for i in range(12):
            t = i / 11.0
            inv = 1.0 - t
            px = inv * inv * cx + 2.0 * inv * t * ctrl_x + t * t * stigma_x
            py = inv * inv * cy + 2.0 * inv * t * ctrl_y + t * t * stigma_y
            pistil_pts.append((px, py))
        pygame.draw.lines(surface, (45, 105, 45), False, pistil_pts, 3)
        pygame.draw.lines(surface, (135, 210, 95), False, pistil_pts, 2)

        pygame.draw.circle(surface, (55, 115, 50), (int(stigma_x), int(stigma_y)), 4)
        pygame.draw.circle(surface, (110, 180, 85), (int(stigma_x), int(stigma_y)), 2)

        # 6 тычинок
        for stamen in self.stamens:
            tx = cx + stamen["tip"][0]
            ty = cy + stamen["tip"][1]
            kx = cx + stamen["ctrl"][0]
            ky = cy + stamen["ctrl"][1]

            fil_pts = []
            for i in range(10):
                t = i / 9.0
                inv = 1.0 - t
                fx = inv * inv * cx + 2.0 * inv * t * kx + t * t * tx
                fy = inv * inv * cy + 2.0 * inv * t * ky + t * t * ty
                fil_pts.append((fx, fy))

            pygame.draw.lines(surface, (95, 165, 85), False, fil_pts, 2)
            pygame.draw.lines(surface, (185, 235, 145), False, fil_pts, 1)

            # Натуральный округлый пыльник
            pollen_color_base = (145, 65, 25)
            pollen_color_bright = (215, 130, 45)
            pollen_color_glow = (255, 195, 85)

            pygame.draw.circle(surface, pollen_color_base, (int(tx), int(ty)), 4)
            pygame.draw.circle(surface, pollen_color_bright, (int(tx), int(ty)), 3)
            pygame.draw.circle(surface, pollen_color_glow, (int(tx - 0.5), int(ty - 0.5)), 1)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовка цветка:
        1. Стебель и листья с учетом изгиба от ветра
        2. Органичное цветоложе
        3. Закрепленные лепестки (движутся вместе с головкой цветка)
        4. Нежные тычинки и пестик
        5. Падающие лепестки
        """
        # 1. Стебель и листья
        self._draw_stem_and_leaves(surface)

        # 2. Органичное основание чашечки (цветоложе)
        self._draw_receptacle_and_scars(surface)

        # 3. Закрепленные лепестки на цветке (следуют за покачиванием чашечки)
        for petal in self.petals:
            if not petal.detached and petal.layer == "outer":
                petal.draw(surface, self.center_pos)

        for petal in self.petals:
            if not petal.detached and petal.layer == "inner":
                petal.draw(surface, self.center_pos)

        # 4. Центр цветка: изящные тычинки и пестик
        self._draw_stamens_and_pistil(surface)

        # 5. Падающие лепестки
        for petal in self.petals:
            if petal.detached:
                petal.draw(surface, self.base_center_pos)
