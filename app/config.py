from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_key: str
    fmcsa_api_key: str
    fmcsa_base_url: str = "https://mobile.fmcsa.dot.gov/qc/services/carriers"
    database_url: str = "sqlite+aiosqlite:///./calls.db"
    loads_file: str = "data/loads.json"
    fmcsa_mock_fallback: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
