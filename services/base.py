from config.base import BaseConfig
from services.saman import SamanService


def get_service(config: BaseConfig):
    match config.provider_name:
        case "saman": 
            return SamanService(config)