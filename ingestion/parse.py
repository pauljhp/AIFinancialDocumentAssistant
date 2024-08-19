from urllib.parse import urlparse, urljoin
import time
import requests
import os
from typing import Dict, Any, Tuple


api_root = os.getenv("PDFPARSER_ENDPOINT")
url_pdf_endpoint = "/v1/pdf/extract-pdf-from-url/"
task_status_endpoint = "/v1/tasks/status/"
task_results_endpoint = "/v1/tasks/get-results/"
get_all_task_endpoint = "/v1/tasks/get-all-tasks/"


def submit_request(pdf_url, max_workers: int=64, chunk_size: int=8):
    endpoint = urljoin(api_root, url_pdf_endpoint)
    res = requests.post(endpoint, json=dict(url=pdf_url, max_workers=max_workers, chunk_size=chunk_size))
    return res

def get_task_status(task_id: str):
    endpoint = urljoin(api_root, task_status_endpoint) + task_id
    return requests.get(endpoint)

async def get_task_results(task_id: str, timeout: int=480):
    start_time = time.time()
    status = get_task_status(task_id)
    endpoint = urljoin(api_root, task_results_endpoint) + task_id
    while time.time() - start_time <= timeout:
        if status.status_code != 200:
            time.sleep(1)
        else:
            result = requests.get(endpoint)
            return result
    raise TimeoutError("request timed out")

def get_all_tasks():
    endpoint = urljoin(api_root, get_all_task_endpoint)
    return requests.get(endpoint).json()

async def get_all_url_contents(
    url_dict: Dict[str, Any]
    ) -> Tuple[Dict[str, Dict[str, str]], Dict[str, str]]:
    results = {}
    task_ids = {}

    for url_key, urls in url_dict.items():
        if isinstance(urls, list):
            for url in urls:
                task = submit_request(url)
                if task.status_code == 200:
                    task_id = task.json()["task_id"]
                    task_ids[url_key] = task_id
                    
        elif isinstance(urls, str):
            url = urls
            task = submit_request(url)
            if task.status_code == 200:
                task_id = task.json()["task_id"]
                task_ids[url_key] = task_id
    for url_key, task_id in task_ids.items():
        results[url_key] = await get_task_results(task_id)
    return task_ids, results

async def aget_all_task_results(tasks: Dict[str, Dict[str, str]]):
    results = {}
    for task_id, status in tasks.items():
        if status["status"] == "completed":
            results[task_id] = await get_task_results(task_id)
    return results