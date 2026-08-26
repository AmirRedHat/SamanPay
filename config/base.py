from abc import ABC, abstractmethod


class BaseConfig(ABC):
    provider_name: str
    
    @abstractmethod
    def load_env_values(cls):
        ...