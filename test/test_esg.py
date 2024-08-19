import unittest
from argparse import ArgumentParser
from services import analyze_esg
from data_models import CompanyInfo
import concurrent.futures
import atexit
from langchain.globals import set_debug


executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

def cleanup():
    executor.shutdown(wait=True)

atexit.register(cleanup) 


def test_esg_governance(companyinfo: CompanyInfo, async_exec: bool=False):
    res = analyze_esg(companyinfo, async_exec=async_exec)
    return res

if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument("--isin")
    argparser.add_argument("--sedol")
    argparser.add_argument("--name")
    argparser.add_argument("--async", dest="async_exec", action="store_true")
    argparser.add_argument("--debug", dest="debug", action="store_true")
    args = argparser.parse_args()
    companyinfo = CompanyInfo(**vars(args))
    if args.debug:
        set_debug(True)
    test_esg_governance(companyinfo, async_exec=args.async_exec)