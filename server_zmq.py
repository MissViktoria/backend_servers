import zmq
import json
from datetime import datetime
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ZmqServer:
    def __init__(self, host='*', port=5555):
        self.host = host
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.data_file = 'android_data.json'
        self.counter = 0

        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f)

    def start(self):
        address = f"tcp://{self.host}:{self.port}"
        self.socket.bind(address)
        logger.info(f"ZMQ сервер запущен на {address}")
        logger.info("Ожидание данных от Android...")
        print("\n" + "=" * 80)
        print("СЕРВЕР ДАННЫХ МЕСТОПОЛОЖЕНИЯ (PUSH/PULL режим)")
        print(f"Порт: {self.port}")
        print("Статус: Ожидание данных...")
        print("=" * 80 + "\n")

        try:
            while True:
                try:
                    message = self.socket.recv_string()
                    logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] Получены данные №{self.counter + 1}")

                    data = json.loads(message)

                    self.counter += 1
                    self.save_data(data)

                    self.print_data(data)

                except json.JSONDecodeError as e:
                    logger.error(f"Ошибка декодирования JSON: {e}")
                except Exception as e:
                    logger.error(f"Ошибка: {e}")

        except KeyboardInterrupt:
            logger.info("\nСервер остановлен")
            print("\n" + "=" * 80)
            print("ВСЕ СОХРАНЕННЫЕ ДАННЫЕ:")
            print("=" * 80)
            try:
                with open('android_data.json', 'r') as f:
                    data = json.load(f)
                    print(f"Всего записей: {len(data)}")
                    for entry in data[-5:]:
                        print(f"\n[{entry['timestamp']}] Устройство: {entry['data'].get('deviceId', 'unknown')}")
            except Exception as e:
                print(f"Ошибка чтения файла: {e}")

    def save_data(self, data):
        try:
            with open(self.data_file, 'r') as f:
                all_data = json.load(f)

            data_entry = {
                'timestamp': datetime.now().isoformat(),
                'data': data,
                'counter': self.counter
            }

            all_data.append(data_entry)

            with open(self.data_file, 'w') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"Данные сохранены в файл (всего записей: {self.counter})")

        except Exception as e:
            logger.error(f"Ошибка при сохранении: {e}")

    def print_data(self, data):
        try:
            print("\n" + "=" * 80)
            print(f" ДАННЫЕ ОТ УСТРОЙСТВА: {data.get('deviceId', 'unknown')}")
            print("=" * 80)

            location = data.get('location', {})
            print(f"МЕСТОПОЛОЖЕНИЕ:")
            print(f"   Широта: {location.get('latitude', 0):.6f}")
            print(f"   Долгота: {location.get('longitude', 0):.6f}")
            print(f"   Высота: {location.get('altitude', 0):.2f} м")

            timestamp = location.get('timestamp', 0)
            if timestamp > 0:
                dt = datetime.fromtimestamp(timestamp / 1000)
                print(f"   Время: {dt.strftime('%H:%M:%S')}")

            cell_info = data.get('cellInfo', {})
            print(f"ИНФОРМАЦИЯ О СОТОВОЙ СЕТИ:")

            network_type = cell_info.get('networkType', 'UNKNOWN')
            print(f"   Тип сети: {network_type}")

            cell_identity = cell_info.get('cellIdentity', {})
            signal_strength = cell_info.get('signalStrength', {})

            if network_type == "LTE":
                print(f"   Cell ID: {cell_identity.get('cellIdentity', 0)}")
                print(f"   MCC: {cell_identity.get('mcc', 0)}, MNC: {cell_identity.get('mnc', 0)}")
                print(f"   Сигнал: RSRP: {signal_strength.get('rsrp', 0)} dBm")

            elif network_type == "GSM":
                print(f"   Cell ID: {cell_identity.get('cellIdentity', 0)}")
                print(f"   MCC: {cell_identity.get('mcc', 0)}, MNC: {cell_identity.get('mnc', 0)}")
                print(f"   Сигнал: DBM: {signal_strength.get('dbm', 0)} dBm")

            elif network_type == "5G_NR":
                print(f"   NCI: {cell_identity.get('nci', 0)}")
                print(f"   MCC: {cell_identity.get('mcc', 0)}, MNC: {cell_identity.get('mnc', 0)}")
                print(f"   Сигнал: SS-RSRP: {signal_strength.get('ssRsrp', 0)} dBm")

            print(f"СТАТИСТИКА: Всего сообщений: {self.counter}")
            print("=" * 80 + "\n")

        except Exception as e:
            logger.error(f" Ошибка при выводе данных: {e}")

    def close(self):
        self.socket.close()
        self.context.term()


if __name__ == "__main__":
    server = ZmqServer()

    try:
        server.start()
    except KeyboardInterrupt:
        print("\nВСЕ СОХРАНЕННЫЕ ДАННЫЕ:")
        print("=" * 80)
        try:
            with open('android_data.json', 'r') as f:
                data = json.load(f)
                print(f"Всего записей: {len(data)}")
                for entry in data[-5:]:
                    print(f"\n[{entry['timestamp']}] Устройство: {entry['data'].get('deviceId', 'unknown')}")
        except Exception as e:
            print(f"Ошибка чтения файла: {e}")
    finally:
        server.close()