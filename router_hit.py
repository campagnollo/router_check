"""
This script is used to connect to multiple routers using SSH, perform some operations, and log the results.
"""
import paramiko
import socket
from getpass import getpass
import sys,os

class routers():
    """
    This class represents a router with methods to connect, disconnect and get the device id.
    """

    def __init__(self, router_name, user, password):
        try:
            self.user=user
            self.password=password
            self.router_name=router_name
            self.ip=socket.gethostbyname(router_name.strip())

        except socket.error:
            print("Device name %s unresolved" %router_name)
            self.user = "Null"
            self.password = "Null"
            self.ip = "0.0.0.0"

        finally:
            self.remote = paramiko.SSHClient()
            self.remote.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def conn_request(self):
        self.remote.connect(hostname=self.ip, port=22,username=self.user,password=self.password, timeout=4)

    def router_close(self):
        self.remote.close()

    def device_id(self):
        return self.router_name


class cabinet():
    """
    This class represents a file cabinet with methods to handle success and failure logs.
    """
    def __init__(self):
        if os.path.isfile("failure.txt"):
             os.remove("failure.txt")
        if os.path.isfile("success.txt"):
             os.remove("success.txt")
        self.success=open('success.txt', 'a')
        self.failure=open('failure.txt', 'a')

    def pingable(self, router_name):
            self.success.write(router_name + '\r')

    def unpingable(self, router_name):
            self.failure.write(router_name + '\r')

    def closure(self):
        self.success.close()
        self.failure.close()


def main():

    filing=cabinet()
    user = raw_input("Enter Username: ")
    password = getpass('Enter Password: ')
    devices = []
    with open('IP-List.txt', 'r') as ip_list:
        nameaddr = ip_list.readlines()
        for router_name in nameaddr:
            devices.insert(-1,routers(router_name,user,password))

    devices.reverse()
    for i in range (0,len(devices)):
        try:
            devices[i].conn_request()
        except socket.gaierror:
            print('Could not connect to %s \n' % devices[i].device_id())
            filing.unpingable(devices[i].device_id())
        except paramiko.AuthenticationException:
            print('Could not authenticate to %s \n' % devices[i].device_id())
            filing.unpingable(devices[i].device_id())
        except socket.error:
            print('Connection Timed out: %s \n' % devices[i].device_id())
            filing.unpingable(devices[i].device_id())
        except paramiko.SSHException:
            print('Incompatible ssh peer: %s \n' % devices[i].device_id())
            filing.unpingable(devices[i].device_id())
        except Exception:
            print("Unexpected error")
            filing.unpingable(devices[i].device_id())
        else:
            print("Router hit")
            filing.pingable(devices[i].device_id())
        finally:
            devices[i].router_close()
    filing.closure()


if __name__ == '__main__':
    """Python interpreter check"""
    try:
        assert sys.version_info[0]<3
    except AssertionError:
        print("Incorrect interpreter being run. Please use Python 2.x")
        exit()
    main()


