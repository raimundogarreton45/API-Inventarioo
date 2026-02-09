"""
CONFIGURACIÓN DE LA APLICACIÓN

Lee todas las variables de entorno del archivo .env
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    
    # Nombre de la aplicación
    app_name: str = "API Inventario PYME"
    
    # Base de datos - URL de conexión a PostgreSQL/Supabase
    database_url: str
    
    # Seguridad - Para crear tokens JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 43200  # 30 días
    
    # Resend - Para enviar emails (3,000 gratis/mes)
    resend_api_key: str
    resend_from_email: str
    
    # Entorno
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Obtiene la configuración de la aplicación."""
    return Settings()
