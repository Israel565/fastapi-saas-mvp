from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "dev-secret-change-me"
    ai_provider: str = "ollama"  # "ollama" or "openai"
    openai_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    stripe_secret_key: str = ""
    frontend_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


settings = Settings()
