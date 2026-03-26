from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    url: str
    JWT_KEY: str
    algorithm: str
    redis_host: str
    redis_port: str
    groq_api_key: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()