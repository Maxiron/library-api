from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class UtilSettingsMixin(BaseSettings):
    class Config:
        # Load from environment variables
        env_file = ".env"
        extra = "allow"
    


class DatabaseSettings(UtilSettingsMixin):
    db_url: str

class RedisSettings(UtilSettingsMixin):
    redis_host: str
    redis_port: int
    redis_db: int


db_settings = DatabaseSettings()
redis_settings = RedisSettings()
