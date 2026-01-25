from locust import HttpUser, task, between

class GlossaryUser(HttpUser):
    wait_time = between(0.01, 0.05)

    @task
    def get_glossaries(self):
        self.client.get("/glossaries/")