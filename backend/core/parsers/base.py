from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

# base class for external data sources (GitHub, LinkedIn, etc.)
# added this so we can plug in new sources without breaking everything.

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
        # convert the raw data into something the system can actually use
        pass

    def process(self, url: str) -> Dict[str, Any]:
        # print(f"DEBUG: Processing {self.name} URL: {url}")
        if not self.validate_url(url):
            raise ValueError(f"Invalid URL for source {self.name}: {url}")
        
        raw_data = self.scrape(url)
        return self.parse(raw_data)
