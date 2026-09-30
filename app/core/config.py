from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Healthcare Appointment & Queue Management System"
    debug: bool = True

    database_url: str = "postgresql://postgres.gmcaykcrzwanwwcypmhm:vishnuvardhan@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"
    mongo_url: str = "mongodb+srv://vishnuvardhangopathi_db_user:vishnuvardhan@hospitalqueue.1mvykhp.mongodb.net/?appName=hospitalqueue"
    mongo_db: str = "healthcare_audit"

    jwt_secret_key: str = "83100323-0264-450a-903c-7253736e6370"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5174,http://127.0.0.1:5174"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
