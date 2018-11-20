from socketIO_client import SocketIO, LoggingNamespace
import time

socketIO = SocketIO('localhost', 5000, LoggingNamespace)

time.sleep(5)


socketIO.emit('time_ended')
time.sleep(5)

exit(0)