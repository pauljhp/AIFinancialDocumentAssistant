from urllib.parse import urlparse, urljoin
import time
import requests
import os

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