import zmq
import json
from datetime import datetime
import os


class ZmqServer:
    def __init__(self, host='*', port=5555):
        self.host = host
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.data_file = 'android_messages.json'
        self.counter = 0

        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f)

    def start(self):
        address = f"tcp://{self.host}:{self.port}"
        self.socket.bind(address)
        print(f"ZMQ сервер запущен на {address}")
        print("Ожидание подключений от Android...")

        while True:
            try:
                message = self.socket.recv_string()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Получено: {message}")
                self.counter += 1
                self.save_message(message)
                response = f"Hello from Server! (Получено сообщений: {self.counter})"
                self.socket.send_string(response)
                print(f"Отправлен ответ: {response}")

            except KeyboardInterrupt:
                print("\nСервер остановлен")
                break
            except Exception as e:
                print(f"Ошибка: {e}")
                break

    def save_message(self, message):
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)

            new_entry = {
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'counter': self.counter
            }
            data.append(new_entry)

            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Ошибка при сохранении: {e}")

    def print_all_data(self):
        """Вывод всех сохраненных данных в консоль"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)

            print("\n" + "=" * 50)
            print("ВСЕ СОХРАНЕННЫЕ ДАННЫЕ:")
            print("=" * 50)

            for entry in data:
                print(f"[{entry['timestamp']}] №{entry['counter']}: {entry['message']}")

            print(f"\nВсего сообщений: {self.counter}")
            print("=" * 50 + "\n")

        except Exception as e:
            print(f"Ошибка при чтении данных: {e}")

    def close(self):
        self.socket.close()
        self.context.term()


if __name__ == "__main__":
    server = ZmqServer()

    try:
        server.start()
    except KeyboardInterrupt:
        server.print_all_data()
        server.close()