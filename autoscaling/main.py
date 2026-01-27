import requests
import subprocess
import time

# Функция для масштабирования backend
def scale_backend(replica_count):
    subprocess.run(["docker-compose", "up", "--scale", f"web-backend={replica_count}"])

# Порог для создания реплики
threshold = 18

while True:
    try:
        # Запросим предсказание нагрузки с ml-service
        response = requests.get('http://localhost:9000/current_prediction')
        predicted_load = response.json().get('predicted_load')

        if predicted_load and predicted_load[0] >= threshold:
            print(f"Нагрузка {predicted_load[0]} превышает порог {threshold}. Создаю новую реплику...")
            scale_backend(2)  # Это создаст 2 реплики (1 начальная + 1 дополнительная)
        else:
            print(f"Нагрузка {predicted_load[0]} ниже порога. Реплика не будет создана.")
        
    except Exception as e:
        print(f"Ошибка при получении предсказания или масштабировании: {e}")
    
    time.sleep(10)