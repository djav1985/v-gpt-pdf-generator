from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BASE_URL: str = ""
    ROOT_PATH: str = ""
    API_KEY: str | None = None


settings = Settings()
