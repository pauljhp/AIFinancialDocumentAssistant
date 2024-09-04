import requests
import os
from typing import List, Set
import itertools


crawlee_endpoint = os.getenv("CRAWLEE_ENDPOINT")
DEFAULT_KEYWORDS = ["esg", "results", "investors", "ir", "sustainability", "sustainable", "investor"]

def search_pdf_urls(
        urls: List[str],
        keywords: List[str]) -> Set[str]:
    res = requests.get(
        crawlee_endpoint + "v0/scrape-urls/", 
        json=dict(
            urls=urls, 
            keywords=keywords
        )
    )
    if res.status_code == 200:
        return set(itertools.chain(*[d.get("pdf_links") for d in res.json()["extracted_data"]]))

