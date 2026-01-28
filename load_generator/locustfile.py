from locust import HttpUser, task, between, events
import gevent
import random
import time
import os

class GlossaryUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:80"
    @task
    def get_glossary(self):
        self.client.get("/glossaries/")

# динамическая рандомная нагрузка
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    def random_load_cycle():
        while True:
            # создаются случайные параметры для цикла
            max_users = random.randint(20, 50)   
            step = random.randint(3, 8)         
            ramp_up_time = random.randint(120, 300) 
            hold_time = random.randint(60, 300)     
            ramp_down_time = random.randint(120, 300) 

            user_count = 0

            gevent.sleep(random.randint(10, 30))  

            while user_count < max_users:
                user_count += step
                if user_count > max_users:
                    user_count = max_users
                if environment.runner:
                    environment.runner.start(user_count, spawn_rate=step)
                gevent.sleep(ramp_up_time / ((max_users + step - 1) // step)) 

            gevent.sleep(hold_time)

            while user_count > 0:
                user_count -= step
                if user_count < 0:
                    user_count = 0
                if environment.runner:
                    environment.runner.start(user_count, spawn_rate=step)
                gevent.sleep(ramp_down_time / ((max_users + step - 1) // step))

            gevent.sleep(120)

    gevent.spawn(random_load_cycle)
