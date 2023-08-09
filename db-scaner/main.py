from database_scanner import DataBaseScanner
import os

remote_host = os.environ["REMOTE_HOST"]
remote_port = int(os.environ["REMOTE_HOST_PORT"])

scanner = DataBaseScanner("fpy-watchdog-db", "root", "sramsram-admin", 27017, remote_host, remote_port)
scanner.scan()