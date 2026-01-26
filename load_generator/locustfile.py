from locust import HttpUser, task, between, events
import gevent
import random
import time

class GlossaryUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_glossary(self):
        self.client.get("/glossaries/")

# # динамическая рандомная нагрузка
# @events.test_start.add_listener
# def on_test_start(environment, **kwargs):
#     def random_load_cycle():
#         while True:
#             # создаём случайные параметры для цикла
#             max_users = random.randint(20, 50)   # максимум пользователей
#             step = random.randint(3, 8)          # шаг изменения пользователей
#             ramp_up_time = random.randint(120, 300)  # время на подъем в секундах
#             hold_time = random.randint(60, 300)      # время удержания пика
#             ramp_down_time = random.randint(120, 300) # время на спад

#             user_count = 0

#             # --- 1. Тишина в начале 10-минутного цикла ---
#             gevent.sleep(random.randint(10, 30))  # пауза 10-30 секунд

#             # --- 2. Подъём нагрузки ---
#             while user_count < max_users:
#                 user_count += step
#                 if user_count > max_users:
#                     user_count = max_users
#                 if environment.runner:
#                     environment.runner.start(user_count, spawn_rate=step)
#                 gevent.sleep(ramp_up_time / ((max_users + step - 1) // step))  # равномерный рост

#             # --- 3. Удержание пика ---
#             gevent.sleep(hold_time)

#             # --- 4. Спад нагрузки ---
#             while user_count > 0:
#                 user_count -= step
#                 if user_count < 0:
#                     user_count = 0
#                 if environment.runner:
#                     environment.runner.start(user_count, spawn_rate=step)
#                 gevent.sleep(ramp_down_time / ((max_users + step - 1) // step))

#             # --- 5. Тишина 2 минуты перед следующим циклом ---
#             gevent.sleep(120)

#     gevent.spawn(random_load_cycle)
