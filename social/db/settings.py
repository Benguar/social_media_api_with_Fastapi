from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    URL: str
    JWT_KEY: str
    ALGORITHM: str
    REDIS_HOST: str
    REDIS_PORT: str
    GROQ_API_KEY: str
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()