from pydantic_settings import BaseSettings, SettingsConfigDict
from box import Box
import yaml

class Settings(BaseSettings):
    TOKEN: str
    ADMIN_ID: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

with open('config.yml') as f:
    config = Box(yaml.safe_load(f))