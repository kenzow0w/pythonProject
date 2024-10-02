import json
from time import time

import requests
from flask import Flask, request, jsonify, render_template, Response, g, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
import logging

from pyinstrument import Profiler

from dto.drone_dto import DroneDto
from controllers.drone_controller import DroneController
from controllers.user_controller import UserController
from db.Database import init_db

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, template_folder='templates', static_folder='static')

# Конфигурируем секретный ключ для JWT
app.config['SECRET_KEY'] = 'my_secret_key'
jwt = JWTManager(app)


# Маршрут для отображения web-интерфейса
@app.route("/")
def login_page():
    return render_template("login.html")


@app.route("/home")
def main_page():
    drones_data = DroneController.get_all()
    drones = [
        dict(id=drone_id, port=port, serial_number=serial_number, mission=mission, timestamp=timestamp)
        for drone_id, port, serial_number, mission, timestamp in drones_data
    ]
    return render_template("home.html", drones=drones)


@app.route("/drones/add")
def drones_page():
    return render_template("drones.html")


@app.route("/drones/add", methods=["POST"])
@jwt_required()
def add_drone():
    serial_number = request.json.get("serial_number")
    port = request.json.get("port")
    drone = DroneDto(port=port, serial_number=serial_number)
    DroneController.add(drone)
    return jsonify({"msg": "Drone were added"}), 200


@app.route("/drones/<id>", methods=["GET"])
def get_drone(id: str):
    drones_data = DroneController.get_all()
    drone = None
    for d in drones_data:
        if str(d[0]) == id:
            drone = DroneDto(*d)
            break
    print(drone)
    if drone:
        # Render a new HTML page with the drone's details
        return render_template('drone_detail.html', drone=drone)
    else:
        # If no drone is found, return a 404 error
        return jsonify({"error": "Drone not found"}), 404


# Маршрут для авторизации
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    users = UserController.get_all()
    print(users)
    # Проверка правильности введённых данных
    # Iterate over the users
    for user in users:
        if username in user and user[0] == username and user[1] == password:
            # Генерация JWT токена
            token = create_access_token(identity=username)
            # user_tokens[username] = token  # Сохраняем токен для пользователя
            return jsonify({"token": token}), 200
        else:
            return jsonify({"error": "Неверный логин или пароль"}), 401


# Маршрут для взлета дрона
@app.route("/takeoff", methods=["POST"])
@jwt_required()
def takeoff():
    try:
        id: int = request.json.get("id")
        drone = DroneDto(*DroneController.get_one(id)[0])
        url = f'http://127.0.0.1:{drone.port}/takeoff'
        logging.info(f"Выполняем запрос по url: {url}")
        response = requests.post(url, json={"altitude": 100})
        if response.status_code == 200:
            telemetry_data = response.json()
            return jsonify(telemetry_data), 200
        else:
            return jsonify({"error": "error during taking off"}), response.status_code
    except Exception as e:
        return Response(json.dumps({"error": f"Не удалось подключиться к дрону: {str(e)}"}, ensure_ascii=False),
                        status=500, mimetype='application/json')


# Маршрут для посадки дрона
@app.route("/land", methods=["POST"])
@jwt_required()
def land():
    try:
        id = request.json.get("id")
        drone = DroneDto(*DroneController.get_one(id)[0])
        url = f'http://127.0.0.1:{drone.port}/land'
        response = requests.post(url)
        if response.status_code == 200:
            telemetry_data = response.json()
            return jsonify(telemetry_data), 200
        else:
            return jsonify({"error": "error during landing"}), response.status_code
    except Exception as e:
        return jsonify({"error": f"The attempt to connect to the drone failed: {str(e)}"}), 500


# Маршрут для выполнения миссии патрулирования
@app.route("/mission", methods=["POST"])
@jwt_required()
def set_mission():
    id = request.json.get("id")
    mission = request.json.get("mission")
    drone = DroneDto(*DroneController.get_one(id)[0])
    if drone.mission == mission:
        return jsonify({"message": "Drone has already been completed this mission"}), 400
    drone.mission = mission
    DroneController.update(drone)
    text = f"Drone has been started {mission} mission"
    logging.info(text)
    return jsonify({"id": id, "message": text, "drone_state": drone}), 200


@app.before_request
def before_request():
    g.start_time = time()  # Record start time
    g.is_profiling = "profiler" in request.args
    if g.is_profiling:
        g.profiler = Profiler()
        g.profiler.start()


@app.after_request
def after_request(response):
    if g.is_profiling:
        g.profiler.stop()
        output_html = g.profiler.output_html()
        return make_response(output_html)

    # Log request details
    duration = time() - g.start_time
    logging.info(f"{request.method} {request.path} - Status: {response.status} - Duration: {duration:.2f} seconds")

    return response


# Запрашиваем телеметрию у дрона
@app.route("/get_drone_telemetry/<id>", methods=["GET"])
@jwt_required()
def get_drone_telemetry(id):
    try:
        drone = DroneDto(*DroneController.get_one(id)[0])
        url = f'http://127.0.0.1:{drone.port}/telemetry'
        response = requests.get(url)

        if response.status_code == 200:
            telemetry_data = response.json()
            return jsonify(telemetry_data), 200
        else:
            return jsonify({"error": "Ошибка при получении данных от дрона"}), response.status_code

    except Exception as e:
        return jsonify({"error": f"Не удалось подключиться к дрону: {str(e)}"}), 500


if __name__ == '__main__':
    init_db().close()
    app.run(debug=True)
