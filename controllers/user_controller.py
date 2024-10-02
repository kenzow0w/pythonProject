from db.Database import SQLiteDBFactory
from db.QueryBuilder import QueryBuilder
from dto.user_dto import UserDto


class UserController:

    @staticmethod
    def add(user: UserDto):
        queryBuilder = QueryBuilder()
        queryBuilder.insert_into("tbl_users", list(vars(user).values())).build()
        print('add user')

    @staticmethod
    def get_all():
        queryBuilder = QueryBuilder()
        cursor = SQLiteDBFactory.get_db().cursor()
        users = cursor.execute(queryBuilder.select("tbl_users").build()).fetchall()
        cursor.close()
        return users

    @staticmethod
    def remove(user: UserDto):
        print('remove user')
