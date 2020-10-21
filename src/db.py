# Copyright (c) 2019-2020 Latona. All rights reserved.

from aion.mysql import BaseMysqlAccess

GET_SIZE = 10


class RobotConnectionSql(BaseMysqlAccess):

    def __init__(self, database):
        super().__init__(database)

    def update_connection_state(self, result):

        query = f"""
                INSERT INTO(name, ip, connection)
                    VALUES (%(name)s, %(ip)s, %(connection)s)
                ON DUPLICATE KEY UPDATE
                    name = values(name),
                    ip = values(ip),
                    connection = values(connection),
                    timestamp = CURRENT_TIMESTAMP();
                """
        args = {'name': result.get('name', 'no name'), 'ip': result['ip'],
                'connection': result['connection']}
        self.set_query(query, args)

    def reset_connections(self):
        query = """
                truncate table connections;
                """
        self.set_query(query)
        self.commit_query()

    def get_connected_robots(self):
        query = """
                SELECT * FROM connections
                WHERE connection = 1;
                """
        return self.get_query_list(GET_SIZE, query)
