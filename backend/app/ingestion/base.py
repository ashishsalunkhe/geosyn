from abc import ABC, abstractmethod
from typing import List, Any, Dict

class BaseProvider(ABC):
    @abstractmethod
    def fetch_raw_docs(self) -> List[Dict[str, Any]]:
        """
        Fetches raw data from the provider.
        Returns a list of dictionaries representing the raw documents.
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def source_type(self) -> str:
        """e.g. news, youtube, social"""
        pass
