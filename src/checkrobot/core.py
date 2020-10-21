# coding: utf-8

# Copyright (c) 2019-2020 Latona. All rights reserved.

import json
import subprocess
import time

import aion.mysql as mysql
from aion.logger import lprint

GET_SIZE = 10
RETURNCODE_SUCCESS = 0
INTERVAL = 5
DBNAME = 'Robot'
SERVICE_NAME = 'check-yaskawa-robot-connection'
config_path = './config/robot.json'


def read_config_json(json_path):
    try:
        data = None
        with open(json_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError as e:
        # lprint_exception(e)
        print(e)
        return None
    except json.JSONDecodeError as e:
        # lprint_exception(e)
        print(e)
        return None
    return data.get('robots', None)


class RobotConnectionSql(mysql.BaseMysqlAccess):

    def __init__(self):
        super().__init__(DBNAME)

    def update_connection_state(self, result):

        query = f"""
                INSERT INTO(name, ip, state)
                    VALUES (%(name)s, %(ip)s, %(state)s)
                ON DUPLICATE KEY UPDATE
                    name = values(name),
                    ip = values(ip),
                    state = values(state),
                    timestamp = CURRENT_TIMESTAMP();
                """
        args = {'name': result.get('name', 'no name'), 'ip': result['ip'],
                'state': result['connection']}
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


class ConnectionChecker():

    def __init__(self, targets):
        # FIXME:read config
        self.targets = targets

    def check_connection(self):
        checked = []
        for target in self.targets:
            target['connection'] = 0
            if target.get('ip'):
                p = subprocess.run(["ping", target['ip'], '-c', '1', '-w', '1'],
                                   stdout=subprocess.PIPE)
                print(p)
                if p.returncode == RETURNCODE_SUCCESS:
                    target['connection'] = 1
            checked.append(target)
        return checked


def main():

    with RobotConnectionSql() as sql:
        sql.reset_connection()
        sql.commit_query()

    targets = read_config_json(config_path)
    if targets is None:
        print('No target robots. exit.')
        import sys
        sys.exit()

    print('target robots :', targets)
    checker = ConnectionChecker(targets)

    while True:
        connections = checker.check_connection()
        print(connections)
        with RobotConnectionSql(DBNAME) as sql:
            for con in connections:
                sql.update_connection_state(con)

            sql.commit_query()

        old = connections
        time.sleep(INTERVAL)


if __name__ == '__main__':

    targets = [{'name': 'roboA', 'ip': '192.168.128.80'},
               {'name': 'roboB', 'ip': '192.168.128.189'},
               {'name': 'roboNot', 'ip': '192.168.111.111'}]
    checker = ConnectionChecker(targets)

    result = checker.check_connection()
    print(result)

    with RobotConnectionSql() as sql:
        for t in result:
            sql.update_connection_state(t)
            sql.commit_query()
