from langchain.tools import tool
import requests
from typing import List, Dict
from pydantic.v1 import BaseModel
import os

crawlee_endpoint = os.getenv("CRAWLEE_ENDPOINT")


class BrowserToolSchema(BaseModel):
    urls: List[str]
    keywords: List[str]


class BrowserTools:
    
    @tool(
        "Get Urls",
        args_schema=BrowserToolSchema
        )
    def get_urls(
        **kwargs: BrowserToolSchema
        ) -> Dict[str, Dict[str, str]]:
        """Get the content of outgoing urls, as well as outbound urls that 
        are PDFs.
        """
        ses = requests.Session()
        res = ses.get(
            crawlee_endpoint + "v0/scrape-urls/",
            params=kwargs
            )
        return res