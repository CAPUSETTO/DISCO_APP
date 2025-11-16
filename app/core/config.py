from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Disco Entradas & Cajas"
    # Se puede sobreescribir por variable de entorno
    SQLALCHEMY_DATABASE_URI: str = (
        "mysql+pymysql://disco_user:disco_pass@db:3306/disco_db"
    )

    class Config:
        env_file = ".env"

settings = Settings()