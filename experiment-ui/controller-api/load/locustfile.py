from locust import HttpUser, task, between, LoadTestShape


class GlossaryUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def get_glossary(self):
        self.client.get("/glossaries/")


class CyclicLoadShape(LoadTestShape):
    """
    Бесконечный циклический профиль нагрузки:
    - плавный рост пользователей
    - удержание нагрузки
    - плавное снижение
    - короткая пауза
    - повтор

    Такой профиль подходит для сбора телеметрии и дальнейшего сравнения
    baseline / reactive / predictive.
    """

    min_users = 30
    max_users = 150

    ramp_up_time = 360      # 6 минуты рост нагрузки
    hold_time = 240         # 4 минуты удержание
    ramp_down_time = 180    # 3 минуты снижение
    pause_time = 600         # 10 минута низкая нагрузка

    spawn_rate = 5

    def tick(self):
        cycle_time = (
            self.ramp_up_time
            + self.hold_time
            + self.ramp_down_time
            + self.pause_time
        )

        run_time = self.get_run_time()
        phase = run_time % cycle_time

        # Фаза 1: рост нагрузки
        if phase < self.ramp_up_time:
            progress = phase / self.ramp_up_time
            users = int(self.min_users + progress * (self.max_users - self.min_users))
            return users, self.spawn_rate

        # Фаза 2: удержание пика
        phase -= self.ramp_up_time
        if phase < self.hold_time:
            return self.max_users, self.spawn_rate

        # Фаза 3: снижение нагрузки
        phase -= self.hold_time
        if phase < self.ramp_down_time:
            progress = phase / self.ramp_down_time
            users = int(self.max_users - progress * (self.max_users - self.min_users))
            return users, self.spawn_rate

        # Фаза 4: пауза / минимальная нагрузка
        return self.min_users, self.spawn_rate