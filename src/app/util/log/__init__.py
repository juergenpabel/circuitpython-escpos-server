import adafruit_logging as logging

from .syslog import SyslogHandler
from .printer import PrinterHandler


class Log(object):
    app_settings: toml.Dotty
    root_logger: logging.Logger

    def __new__(cls):
        if hasattr(cls, 'singleton') is False:
            cls.singleton = super(Log, cls).__new__(cls)
            cls.singleton.root_logger = logging.getLogger("root")
            cls.singleton.root_logger.setLevel(logging.INFO)
            cls.singleton.root_logger.addHandler(logging.StreamHandler())
            cls.singleton.root_logger.critical("circuitpython-escpos-server")
        return cls.singleton

    def setup(self, server, app_settings: toml.Dotty) -> bool:
        self.server = server
        self.app_settings = app_settings
        if 'LOG_LEVEL' in self.app_settings['SYSTEM']:
            level_int = logging.INFO
            level_str = self.app_settings['SYSTEM']['LOG_LEVEL'].upper()
            for value, name in logging.LEVELS:
                if name == level_str:
                    level_int = value
            self.root_logger.setLevel(level_int)
        if 'LOG_SERVER' in self.app_settings['SYSTEM']:
            self.root_logger.addHandler(SyslogHandler(self.app_settings['SYSTEM']['LOG_SERVER']))
            self.root_logger.info(f"Added SyslogHandler('{self.app_settings['SYSTEM']['LOG_SERVER']}') to Logger('root')")
        if 'LOG_PRINTER' in self.app_settings['SYSTEM']:
            self.root_logger.addHandler(PrinterHandler(self.server, self.app_settings['SYSTEM']['LOG_PRINTER']))
            self.root_logger.info(f"Added PrinterHandler('{self.app_settings['SYSTEM']['LOG_PRINTER']}') to Logger('root')")
        return True

    def getLogger(self, name: str) ->  logging.Logger:
        if name not in logging.logger_cache:
            logger = logging.getLogger(name)
            logger.setLevel(self.root_logger.getEffectiveLevel())
            if name in self.app_settings:
                if 'LOG_LEVEL' in self.app_settings[name]:
                    level_int = self.root_logger.getEffectiveLevel()
                    level_str = self.app_settings[name]['LOG_LEVEL'].upper()
                    for value, name in logging.LEVELS:
                        if name == level_str:
                            level_int = value
                    logger.setLevel(level_int)
            logger._handlers = self.root_logger._handlers
        return logging.getLogger(name)

