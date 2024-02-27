import sys
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
            cls.singleton.root_logger.addHandler(logging.StreamHandler(sys.stderr))
            cls.singleton.root_logger.critical("circuitpython-escpos-server")
            cls.singleton.root_logger.info(f"Added StreamHandler(sys.stderr) to Logger('root')")
        return cls.singleton

    def setup(self, server, app_settings: toml.Dotty) -> bool:
        self.server = server
        self.app_settings = app_settings
        if 'LOG_LEVEL' in self.app_settings['SYSTEM']:
            level_str = self.app_settings['SYSTEM']['LOG_LEVEL']
            self.root_logger.setLevel(self.getLevelNo(level_str))
            self.root_logger.info(f"Using LOG_LEVEL='{level_str.upper()}' from table/section SYSTEM (settings.toml) for Logger('root')")
        if 'LOG_SERVER' in self.app_settings['SYSTEM']:
            self.root_logger.addHandler(SyslogHandler(self.app_settings['SYSTEM']['LOG_SERVER']))
            self.root_logger.info(f"Added SyslogHandler('{self.app_settings['SYSTEM']['LOG_SERVER']}') to Logger('root')")
        if 'LOG_PRINTER' in self.app_settings['SYSTEM']:
            self.root_logger.addHandler(PrinterHandler(self.server, self.app_settings['SYSTEM']['LOG_PRINTER']))
            self.root_logger.info(f"Added PrinterHandler('{self.app_settings['SYSTEM']['LOG_PRINTER']}') to Logger('root')")
        return True

    def getLevelNo(self, level_name: str) ->  int:
        level_name = level_name.upper()
        for value, name in logging.LEVELS:
            if name == level_name:
                return value
        return self.root_logger.getEffectiveLevel()

    def getLogger(self, name: str) ->  logging.Logger:
        if name not in logging.logger_cache:
            logger = logging.getLogger(name)
            logger.setLevel(self.root_logger.getEffectiveLevel())
            if name in self.app_settings:
                if 'LOG_LEVEL' in self.app_settings[name]:
                    logger.setLevel(self.getLevelNo(self.app_settings[name]['LOG_LEVEL']))
            logger._handlers = self.root_logger._handlers
        return logging.getLogger(name)

