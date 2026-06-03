import requests
import subprocess
import time
import threading

# Функция для масштабирования backend
def scale_backend(replica_count):
    subprocess.run(["docker-compose", "up", "--scale", f"web-backend={replica_count}"])

# Порог для создания реплики
threshold = 18

def check_and_scale():
    while True:
        try:
            print("Запрос отправлен в ml-service")
            response = requests.get('http://ml-service/current_prediction')
            print(f"Ответ от ml-service: {response.status_code}")
            predicted_load = response.json().get('predicted_load')
            if isinstance(predicted_load, list):
                predicted_load = predicted_load[0] if predicted_load else None

            if predicted_load is not None:
                predicted_float = float(predicted_load)

            if predicted_float is not None and predicted_float >= threshold:
                print(f"Нагрузка {predicted_float} превышает порог {threshold}. Создаю новую реплику...")
                scale_backend(2)  # Это создаст 2 реплики (1 начальная + 1 дополнительная)
            else:
                print(f"Нагрузка {predicted_float} ниже порога. Реплика не будет создана.")
            
        except Exception as e:
            print(f"Ошибка при получении предсказания или масштабировании: {e}")
        
        time.sleep(10)

scaling_thread = threading.Thread(target=check_and_scale)
scaling_thread.start()