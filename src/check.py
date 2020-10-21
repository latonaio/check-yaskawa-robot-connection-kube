
import subprocess

RETURNCODE_SUCCESS = 0


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


if __name__ == '__main__':

    targets = [{'name': 'roboA', 'ip': '192.168.128.80'},
               {'name': 'roboB', 'ip': '192.168.128.189'},
               {'name': 'roboNot', 'ip': '192.168.111.111'}]
    checker = ConnectionChecker(targets)

    result = checker.check_connection()
    print(result)
