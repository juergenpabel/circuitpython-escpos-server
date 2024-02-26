import time

import adafruit_logging as logging


class LogHandler(logging.Handler):
    log_online: bool = True
    log_queue: list = None

    def __init__(self, online: bool):
        logging.Handler.__init__(self)
        if online is True:
            self.setOnline()
        else:
            self.setOffline()
        self.emit(logging.LogRecord("dummy", logging.CRITICAL, 'CRITICAL', 'circuitpython-escpos-server', time.monotonic(), None))

    def isOnline(self) -> bool:
        return self.log_online

    def isOffline(self) -> bool:
        return not(self.log_online)

    def setOnline(self) -> None:
        self.log_online = True
        if self.log_queue is not None:
            for queued_record in self.log_queue:
                self.emit(queued_record)
            self.log_queue = None

    def setOffline(self) -> None:
        self.log_online = False
        if self.log_queue is None:
            self.log_queue = list()

    def emit(self, record: logging._LogRecord) -> None:
        if self.log_online is False:
            self.log_queue.append(record)
    
