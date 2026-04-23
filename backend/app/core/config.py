from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "GeoSyn"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    AUTO_CREATE_TABLES: bool = False

    DB_DRIVER: str = "postgresql+psycopg2"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "geosyn"
    SQLALCHEMY_DATABASE_URI: str | None = None
    SQLALCHEMY_POOL_SIZE: int = 10
    SQLALCHEMY_MAX_OVERFLOW: int = 20
    SQLALCHEMY_POOL_RECYCLE: int = 1800

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_USERNAME: str | None = None
    REDIS_PASSWORD: str | None = None
    REDIS_URL: str | None = None

    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None
    CELERY_TASK_ALWAYS_EAGER: bool = False

    OBJECT_STORAGE_PROVIDER: str = "local"
    OBJECT_STORAGE_BUCKET: str = "geosyn-raw"
    OBJECT_STORAGE_REGION: str = "us-east-1"
    OBJECT_STORAGE_ENDPOINT_URL: str | None = None
    OBJECT_STORAGE_ACCESS_KEY_ID: str | None = None
    OBJECT_STORAGE_SECRET_ACCESS_KEY: str | None = None
    OBJECT_STORAGE_USE_SSL: bool = False
    OBJECT_STORAGE_LOCAL_PATH: str = "data"

    PROMETHEUS_ENABLED: bool = True
    OTEL_ENABLED: bool = False
    OTEL_SERVICE_NAME: str = "geosyn-api"
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = None
    OTEL_EXPORTER_OTLP_HEADERS: str | None = None

    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    FRED_API_KEY: str | None = None
    EVENT_REGISTRY_API_KEY: str | None = None
    TAVILY_API_KEY: str | None = None

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

    def get_db_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return (
            f"{self.DB_DRIVER}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def get_redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        auth = ""
        if self.REDIS_USERNAME and self.REDIS_PASSWORD:
            auth = f"{self.REDIS_USERNAME}:{self.REDIS_PASSWORD}@"
        elif self.REDIS_PASSWORD:
            auth = f":{self.REDIS_PASSWORD}@"
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def get_celery_broker_url(self) -> str:
        return self.CELERY_BROKER_URL or self.get_redis_url()

    def get_celery_result_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.get_redis_url()

    def is_local_object_storage(self) -> bool:
        return self.OBJECT_STORAGE_PROVIDER.lower() == "local"


settings = Settings()
