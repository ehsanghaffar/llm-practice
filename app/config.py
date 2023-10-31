from enum import Enum
from functools import lru_cache
from pydantic_settings import BaseSettings

class LogLevel(str, Enum):
    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"

class Settings(BaseSettings):

  # Logger top level
  log_level: LogLevel = LogLevel.DEBUG
  class Config:
        env_file = '.env'


@lru_cache
def get_settings():
    return Settings()