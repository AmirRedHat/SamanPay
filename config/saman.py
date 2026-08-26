from decouple import config

from config.base import BaseConfig

class SamanConfig(BaseConfig):
    provider_name = "saman"
    terminal_id: str 
    password: str
    redirect_url: str
    
    @classmethod
    def load_env_values(cls):
        cls.terminal_id  = config("TERMINAL_ID")
        cls.password     = config("PASSWORD")
        cls.redirect_url = config("DOMAIN")
        if not cls.terminal_id or not cls.password or not cls.redirect_url:
            raise ValueError("invalid credentials")