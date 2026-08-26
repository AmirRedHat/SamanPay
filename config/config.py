from config.base import BaseConfig
from config.saman import SamanConfig

def get_config(provider: str) -> BaseConfig:
    match provider.lower():
        case "saman": 
            return SamanConfig