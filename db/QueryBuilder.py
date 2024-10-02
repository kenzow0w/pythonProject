# Паттерн Строитель для построения SQL-запросов
class QueryBuilder:

    def __init__(self):
        # Инициализация словаря для хранения частей запроса и списка параметров
        self.__query_parts = {}
        self.__params = []

    # Method to create the INSERT INTO part of the query
    def insert_into(self, table: str, columns: list):
        cols = ','.join(columns)  # ["id", "name"] -> "id,name"
        question_marks = ','.join(['?'] * len(columns))  # ["?", "?", "?"]
        self.__query_parts["INSERT INTO"] = f"INSERT INTO {table} ({cols}) VALUES ({question_marks})"
        return self

    # Method to add values for INSERT INTO
    def values(self, *columns: list):
        self.__params.extend(columns)
        print(self.get_params())
        return self

    # Method to retrieve the list of parameters
    def get_params(self):
        return self.__params

    # Method to create the SELECT part of the query
    def select(self, table: str, columns="*"):
        self.__query_parts["SELECT"] = f"SELECT {columns}"
        self.__query_parts["FROM"] = f"FROM {table}"
        return self

    # Method to add WHERE condition
    def where(self, condition: str, params=None):
        self.__query_parts["WHERE"] = f"WHERE {condition}"
        if params:
            self.__params.extend(params)
        return self

    # Method to create the UPDATE part of the query
    def update(self, table: str):
        self.__query_parts["UPDATE"] = f"UPDATE {table} SET"
        return self

    # Method to set the columns and their new values for the UPDATE statement
    def set(self, columns: dict):
        set_clause = ', '.join([f" {column} = ?" for column in columns.keys()])
        self.__query_parts["SET"] = set_clause
        self.__params.extend(columns.values())  # Add the values in the same order
        return self

    # Method to assemble the final SQL query
    def build(self):
        query = ""
        if "UPDATE" in self.__query_parts:
            query = self.__query_parts["UPDATE"]
        if "SET" in self.__query_parts:
            query += self.__query_parts["SET"]
        if "INSERT INTO" in self.__query_parts:
            query = self.__query_parts["INSERT INTO"]
        if "SELECT" in self.__query_parts:
            query = f'{self.__query_parts["SELECT"]} {self.__query_parts["FROM"]} '
        if "WHERE" in self.__query_parts:
            query += self.__query_parts["WHERE"]
        return query
