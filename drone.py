from flask import Flask, jsonify, request
import logging
from threading import Thread

app = Flask(__name__)

# Телеметрические данные дрона
drone_telemetry = {
    "latitude": 55.7558,
    "longitude": 37.6173,
    "altitude": 0.0,  # Начальная высота 0
    "battery": 100,
    "speed": 0.0  # Начальная скорость 0
}


# Маршрут для передачи телеметрии дрона
@app.route("/telemetry", methods=["GET"])
def send_telemetry():
    return jsonify(drone_telemetry), 200


# Маршрут для взлета дрона
@app.route("/takeoff", methods=["POST"])
def takeoff():
    altitude = request.json.get('altitude', 100)  # Высота по умолчанию 100 метров
    drone_telemetry["altitude"] = altitude  # Обновляем высоту в телеметрии
    drone_telemetry["speed"] = 10.0  # Изменение скорости при взлете
    logging.info(f"Дрон взлетает на высоту: {altitude} метров")
    return jsonify({"message": f"Взлет на {altitude} метров выполнен", "drone_telemetry": drone_telemetry}), 200


# Маршрут для посадки дрона
@app.route("/land", methods=["POST"])
def land():
    drone_telemetry["altitude"] = 0.0  # При посадке высота 0
    drone_telemetry["speed"] = 0.0  # Пример изменения скорости на 0 при посадке
    logging.info("Дрон приземляется")
    return jsonify({"message": "Посадка выполнена", "drone_telemetry": drone_telemetry}), 200


# Запуск Flask-сервера в отдельном потоке
def start_flask_server():
    app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)


if __name__ == "__main__":
    # Запускаем Flask-сервер в отдельном потоке
    flask_thread = Thread(target=start_flask_server)
    flask_thread.start()
    logging.basicConfig(level=logging.INFO)
