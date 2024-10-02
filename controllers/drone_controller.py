import logging

from db.Database import SQLiteDBFactory
from db.QueryBuilder import QueryBuilder
from dto.drone_dto import DroneDto


class DroneController:

    @staticmethod
    def add(drone: DroneDto):
        queryBuilder = QueryBuilder()
        conn = SQLiteDBFactory.get_db()
        query = queryBuilder.insert_into("tbl_drones", [
            "port",
            "serial_number",
            "mission",
            "created_at"
        ]).values(
            drone.port,
            drone.serial_number,
            drone.mission,
            drone.created_at
        ).build()
        conn.execute(query, queryBuilder.get_params())
        conn.commit()
        conn.close()
        logging.info(f"Дрон {drone.serial_number} сохранен в БД")

    @staticmethod
    def get_all():
        queryBuilder = QueryBuilder()
        cursor = SQLiteDBFactory.get_db().cursor()
        drones = cursor.execute(queryBuilder.select("tbl_drones").build()).fetchall()
        cursor.close()
        return drones

    @staticmethod
    def get_one(id):
        queryBuilder = QueryBuilder()
        cursor = SQLiteDBFactory.get_db().cursor()
        select = queryBuilder.select("tbl_drones").where("id = ?", [id]).build()
        drones = cursor.execute(select, queryBuilder.get_params()).fetchall()
        cursor.close()
        return drones

    @staticmethod
    def update(drone: DroneDto):
        update_data = {
            'mission': drone.mission
        }
        queryBuilder = QueryBuilder()
        conn = SQLiteDBFactory.get_db()
        print(update_data)
        query = queryBuilder.update('tbl_drones').set(update_data).where("id = ?", [drone.id]).build()
        print(query)
        print(queryBuilder.get_params())
        drones = conn.cursor().execute(query, queryBuilder.get_params())
        conn.commit()
        conn.close()
        return drones


@staticmethod
def remove(user: DroneDto):
    print('remove drone')
