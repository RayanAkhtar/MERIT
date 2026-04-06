from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

# data sources that are used in candidate info
# this is so that we can easily add new data sources in the future
# without having to change the rest of the codebase

class BaseDataSource(ABC):
    """
    Abstract base class for all data sources (GitHub, LinkedIn, etc.)
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """the unique name of the data source"""
        pass

    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """check if the URL is valid for this data source"""
        pass

    @abstractmethod
    def scrape(self, url: str) -> Any:
        """fetch raw data from the data source URL"""
        pass

    @abstractmethod
    def parse(self, raw_data: Any) -> Dict[str, Any]:
        """transform raw data into a structured candidate profile fragment"""
        pass

    def process(self, url: str) -> Dict[str, Any]:
        """validate, scrape and parse a URL"""
        if not self.validate_url(url):
            raise ValueError(f"Invalid URL for source {self.name}: {url}")
        
        raw_data = self.scrape(url)
        return self.parse(raw_data)
