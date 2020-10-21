
import json
import logging
import os
import time

from . import ConnectionChecker, RobotConnectionSql

# from aion.logger import lprint, lprint_exception


INTERVAL = 5
DBNAME = 'Robot'
SERVICE_NAME = 'check-yaskawa-robot-connection'

logging.basicConfig(level=logging.DEBUG,
                    filename="var/lib/aion/Data/service.log")
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


def main():

    with RobotConnectionSql(DBNAME) as sql:
        sql.reset_connection()
        sql.commit_query()

    logger = logging.getLogger(__name__)

    targets = read_config_json(config_path)
    if targets is None:
        print('No target robots. exit.')
        import sys
        sys.exit()

    print('target robots :', targets)
    checker = check.ConnectionChecker(targets)

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
    main()
