"""Модуль пользовательского интерфейса (UI) и текстовой анимации."""

import math
import pygame
from settings import SCREEN_WIDTH


class UI:
    """Управляет отображением и отзывчивой кинетической анимацией надписи LOVE ME / LOVE ME NOT.
    
    Поддерживает:
    - Начальное скрытое состояние до первого действия пользователя
    - Мгновенный запуск перехода строго при отрыве лепестка (без задержки)
    - Элегантный плавный кросс-фейд (0.28 сек)
    - Свечение в тонах Stargazer Lily и эффект легкого импульса при смене
    """

    def __init__(self, pos: tuple[float, float] | None = None) -> None:
        pygame.font.init()

        # Размещение над цветком
        if pos is None:
            self.pos = (SCREEN_WIDTH * 0.52, 62.0)
        else:
            self.pos = pos

        font_candidates = ["georgia", "garamond", "palatino", "timesnewroman", "segoeui"]
        self.font = pygame.font.SysFont(font_candidates, 34, bold=True)

        # Текстовые состояния
        # Изначально надписи скрыты! Появляются только при первом отрыве лепестка
        self.visible = False
        self.current_text = "LOVE ME"
        self.target_text = "LOVE ME"
        self.prev_text = ""

        # Параметры быстрой и плавной анимации перехода
        self.alpha_current = 0.0
        self.alpha_prev = 0.0
        self.transition_time = 0.0
        self.transition_duration = 0.28  # динамичный и плавный переход без задержки
        self.is_transitioning = False
        self.scale_pulse = 1.0

        # Цветовая гамма (палитра Stargazer Lily)
        self.color_core = (255, 238, 246)      # нежно-розовый светящийся центр
        self.color_glow = (245, 95, 160)       # мягкий маджента-розовый ореол
        self.color_deep_glow = (180, 25, 100)  # глубокое фоновое свечение

        # Кэш отрендеренных поверхностей
        self.rendered_surfaces: dict[str, pygame.Surface] = {}
        self._prerender_text("LOVE ME")
        self._prerender_text("LOVE ME NOT")

        self.total_time = 0.0

    def _render_glowing_text(self, text: str) -> pygame.Surface:
        """Создает высококачественную поверхность с мягким ореолом свечения вокруг текста."""
        base_text = self.font.render(text, True, self.color_core)
        glow_text = self.font.render(text, True, self.color_glow)
        deep_glow_text = self.font.render(text, True, self.color_deep_glow)

        padding = 24
        w = base_text.get_width() + padding * 2
        h = base_text.get_height() + padding * 2

        glow_surf = pygame.Surface((w, h), pygame.SRCALPHA)

        offsets_deep = [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, -2), (-2, 2), (2, 2)]
        for dx, dy in offsets_deep:
            deep_copy = deep_glow_text.copy()
            deep_copy.set_alpha(45)
            glow_surf.blit(deep_copy, (padding + dx, padding + dy))

        offsets_glow = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
        for dx, dy in offsets_glow:
            glow_copy = glow_text.copy()
            glow_copy.set_alpha(110)
            glow_surf.blit(glow_copy, (padding + dx, padding + dy))

        glow_surf.blit(base_text, (padding, padding))
        return glow_surf

    def _prerender_text(self, text: str) -> None:
        """Кэширует отрендеренный текст со свечением."""
        if text not in self.rendered_surfaces:
            self.rendered_surfaces[text] = self._render_glowing_text(text)

    def set_text(self, new_text: str) -> None:
        """Мгновенно запускает появление или смену текста без малейшей задержки."""
        self._prerender_text(new_text)

        # Если текст еще не был видим (первый клик), делаем плавное появление
        if not self.visible:
            self.visible = True
            self.current_text = new_text
            self.target_text = new_text
            self.prev_text = ""
            self.alpha_current = 0.0
            self.alpha_prev = 0.0
            self.transition_time = 0.0
            self.is_transitioning = True
            self.scale_pulse = 1.15
            return

        # Если новый текст уже является целевым и переход идет, не сбиваем
        if new_text == self.target_text and self.is_transitioning:
            return

        # Если новый клик произошел во время активного предыдущего перехода,
        # текущее видимое состояние плавно передается как prev_text
        self.prev_text = self.target_text if self.is_transitioning else self.current_text
        self.alpha_prev = max(self.alpha_current, self.alpha_prev)
        self.alpha_current = 0.0

        self.target_text = new_text
        self.transition_time = 0.0
        self.is_transitioning = True
        self.scale_pulse = 1.15

    def reset(self) -> None:
        """Сброс интерфейса в начальное скрытое состояние до действий пользователя."""
        self.visible = False
        self.current_text = "LOVE ME"
        self.target_text = "LOVE ME"
        self.prev_text = ""
        self.alpha_current = 0.0
        self.alpha_prev = 0.0
        self.transition_time = 0.0
        self.is_transitioning = False
        self.scale_pulse = 1.0
        self.total_time = 0.0

    def update(self, dt: float) -> None:
        """Обновление анимации текста с учетом delta time."""
        if not self.visible:
            return

        self.total_time += dt

        if self.scale_pulse > 1.0:
            self.scale_pulse = max(1.0, self.scale_pulse - 0.5 * dt)

        # Обработка плавного перехода
        if self.is_transitioning:
            self.transition_time += dt
            progress = min(1.0, self.transition_time / self.transition_duration)
            smooth_t = (1.0 - math.cos(progress * math.pi)) * 0.5

            self.alpha_current = 255.0 * smooth_t
            self.alpha_prev = 255.0 * (1.0 - smooth_t)

            if progress >= 1.0:
                self.alpha_current = 255.0
                self.alpha_prev = 0.0
                self.current_text = self.target_text
                self.prev_text = ""
                self.is_transitioning = False

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовка текста только когда он активирован действием пользователя."""
        if not self.visible:
            return

        breath = 1.0 + 0.02 * math.sin(self.total_time * 2.2)
        total_scale = self.scale_pulse * breath

        # 1. Исчезающий предыдущий текст
        if self.is_transitioning and self.prev_text and self.alpha_prev > 1:
            prev_surf = self.rendered_surfaces.get(self.prev_text)
            if prev_surf is not None:
                surf_copy = prev_surf.copy()
                surf_copy.set_alpha(int(self.alpha_prev))
                if abs(total_scale - 1.0) > 0.01:
                    new_w = int(surf_copy.get_width() * total_scale)
                    new_h = int(surf_copy.get_height() * total_scale)
                    surf_copy = pygame.transform.smoothscale(surf_copy, (new_w, new_h))
                rect = surf_copy.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
                surface.blit(surf_copy, rect.topleft)

        # 2. Появляющийся / активный текст
        active_key = self.target_text if self.is_transitioning else self.current_text
        curr_surf = self.rendered_surfaces.get(active_key)
        if curr_surf is not None and self.alpha_current > 1:
            surf_copy = curr_surf.copy()
            surf_copy.set_alpha(int(self.alpha_current))
            if abs(total_scale - 1.0) > 0.01:
                new_w = int(surf_copy.get_width() * total_scale)
                new_h = int(surf_copy.get_height() * total_scale)
                surf_copy = pygame.transform.smoothscale(surf_copy, (new_w, new_h))
            rect = surf_copy.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
            surface.blit(surf_copy, rect.topleft)
