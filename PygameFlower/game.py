"""Основной класс Game: управление жизненным циклом приложения, отдачей, тряской экрана, UI и эффектами."""

import math
import sys
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE, FPS
from scene import Scene
from lily import Lily
from ui import UI
from effects import EffectsManager


class Game:
    """Управляет игровым циклом, сценой, цветком, тряской экрана, физикой падения, текстом и сердечками."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.running = False
        self.dt = 0.0

        # Внутренний холст для отрисовки мира перед применением экранной тряски
        self.world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Модули окружения, цветка, интерфейса и спецэффектов
        self.scene = Scene()
        self.lily = Lily()
        self.ui = UI()
        self.effects = EffectsManager()

        # Параметры очередности падения лепестков по клику
        self.petal_sequence = [0, 4, 2, 5, 1, 3]
        self.current_petal_step = 0

        # Количество успешно оторванных лепестков
        self.detached_count = 0

        # Состояние запуска финальной анимации
        self.final_animation_triggered = False

        # Система сочной кинематографичной тряски сцены (screenshake)
        self.shake_active = False
        self.shake_timer = 0.0
        self.shake_duration = 0.28   # Длительность импульса тряски
        self.shake_amplitude_x = 7.0 # Максимальное горизонтальное смещение
        self.shake_amplitude_y = 5.0 # Максимальное вертикальное смещение
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0

    def trigger_screenshake(self) -> None:
        """Запускает быстрый кратковременный импульс тряски экрана с экспоненциальным затуханием."""
        self.shake_active = True
        self.shake_timer = 0.0

    def reset_animation(self) -> None:
        """Сбрасывает проект в исходное состояние для повторного запуска."""
        self.lily.reset()
        self.ui.reset()
        self.effects.reset()
        self.current_petal_step = 0
        self.detached_count = 0
        self.final_animation_triggered = False
        self.shake_active = False
        self.shake_timer = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0

    def on_flower_click(self) -> None:
        """Обрабатывает клик/касание:
        1. Отрывает ровно 1 лепесток
        2. Запускает отдачу цветка и тряску экрана
        3. МГНОВЕННО и синхронно запускает переключение текста LOVE ME / LOVE ME NOT
        """
        if self.current_petal_step < len(self.petal_sequence):
            petal_idx = self.petal_sequence[self.current_petal_step]
            if self.lily.detach_petal(petal_idx):
                self.current_petal_step += 1
                self.detached_count += 1

                # Синхронный импульс тряски сцены
                self.trigger_screenshake()

                # Мгновенная синхронная смена надписи в момент отрыва:
                # 1-й клик: LOVE ME
                # 2-й клик: LOVE ME NOT
                # 3-й клик: LOVE ME
                # 4-й клик: LOVE ME NOT
                # 5-й клик: LOVE ME
                # 6-й клик: LOVE ME NOT (или LOVE ME по завершении цикла)
                # Чередование:
                # 1 оторван -> LOVE ME
                # 2 оторвано -> LOVE ME NOT
                # 3 оторвано -> LOVE ME
                # 4 оторвано -> LOVE ME NOT
                # 5 оторвано -> LOVE ME
                # 6 оторвано -> LOVE ME NOT
                if self.detached_count % 2 == 1:
                    self.ui.set_text("LOVE ME")
                else:
                    self.ui.set_text("LOVE ME NOT")

    def handle_events(self) -> None:
        """Обработка пользовательского ввода и системных событий."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r or event.key == pygame.K_SPACE:
                    self.reset_animation()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    self.on_flower_click()
            elif event.type == pygame.FINGERDOWN:
                # Поддержка сенсорных экранов на мобильных устройствах
                self.on_flower_click()

    def update(self) -> None:
        """Обновление сцены, тряски экрана, физики цветка, UI и сердечек."""
        # 1. Ночное окружение
        self.scene.update(self.dt)

        # 2. Физика цветка, отдача и полет лепестков
        self.lily.update(self.dt)

        # 3. Обновление затухающей тряски экрана
        if self.shake_active:
            self.shake_timer += self.dt
            progress = self.shake_timer / self.shake_duration
            if progress >= 1.0:
                self.shake_active = False
                self.shake_offset_x = 0.0
                self.shake_offset_y = 0.0
            else:
                decay = math.exp(-7.0 * progress)
                self.shake_offset_x = math.sin(self.shake_timer * 45.0) * self.shake_amplitude_x * decay
                self.shake_offset_y = math.cos(self.shake_timer * 52.0) * self.shake_amplitude_y * decay
        else:
            self.shake_offset_x = 0.0
            self.shake_offset_y = 0.0

        # 4. Триггер финальной анимации сердечек:
        # Запускается только когда все 6 лепестков оторваны и завершили падение
        if (
            not self.final_animation_triggered
            and self.detached_count == 6
            and all(p.landed for p in self.lily.petals if p.detached)
        ):
            self.final_animation_triggered = True
            # При завершении падения всех лепестков фиксируем финал LOVE ME
            self.ui.set_text("LOVE ME")
            self.effects.start(self.lily.base_center_pos)

        # 5. Обновление текстовой анимации и эффектов
        self.ui.update(self.dt)
        self.effects.update(self.dt)

    def render(self) -> None:
        """Отрисовка всех слоев на холст мира с последующим применением экранной отдачи."""
        # 1. Рендеринг всех игровых слоев в world_surface
        self.scene.draw(self.world_surface)
        self.lily.draw(self.world_surface)
        self.effects.draw(self.world_surface)
        self.ui.draw(self.world_surface)

        # 2. Вывод на экран с учетом смещения тряски (screenshake)
        self.screen.fill((10, 14, 26))
        self.screen.blit(
            self.world_surface,
            (int(self.shake_offset_x), int(self.shake_offset_y)),
        )

        pygame.display.flip()

    def run(self) -> None:
        """Главный игровой цикл."""
        self.running = True
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update()
            self.render()

        self.cleanup()

    def cleanup(self) -> None:
        """Корректное завершение работы Pygame и освобождение ресурсов."""
        pygame.quit()
        sys.exit()
