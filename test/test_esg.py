import unittest
from argparse import ArgumentParser
from services import analyze_esg
from tasks import get_new_esg_review_task
from agents import get_esg_analyst
from tools import RetrievalTools
from data_models import CompanyInfo
import concurrent.futures
import atexit
from langchain.globals import set_debug
from viztracer import VizTracer
import time


executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)


def cleanup():
    executor.shutdown(wait=True)


atexit.register(cleanup)


def test_esg_governance(companyinfo: CompanyInfo, async_exec: bool = False):
    res = analyze_esg(companyinfo, async_exec=async_exec)
    return res

def test_single_task(companyinfo: CompanyInfo, async_exec: bool = False):
    tools = [RetrievalTools(companyinfo=companyinfo, collection_names=["esg_reports", "annual_reports"])]
    agent = get_esg_analyst(tools=tools)
    task = get_new_esg_review_task(company_info=companyinfo, tools=tools, agent=agent)
    res = agent.execute_task(task=task[0])
    return res


if __name__ == '__main__':
    start_time = time.time()
    print("starting")
    argparser = ArgumentParser()
    argparser.add_argument("--isin", default="")
    argparser.add_argument("--sedol", default="")
    argparser.add_argument("--name", default="")
    argparser.add_argument("--async", dest="async_exec", action="store_true")
    argparser.add_argument("--debug", dest="debug", action="store_true")
    argparser.add_argument("--trace", "-T", dest="trace", action="store_true")
    argparser.add_argument("--report-year", dest="report_year", default=2023)
    argparser.add_argument("--mode", dest="mode", default="full", help="two modes are availalbe, `single` and `full`.") # taks full or single
    args = argparser.parse_args()
    companyinfo = CompanyInfo(ISIN=args.isin, name=args.name, SEDOL=args.sedol, report_year=args.report_year)
    match args.mode:
        case "full": func = test_esg_governance
        case "single": func = test_single_task
        case _: raise ValueError(f"{args.mode} not supported! only `single` and `full` supported. ")
    if args.debug:
        set_debug(True)
    if args.trace:
        with VizTracer(
            output_file="test/trace.json",  
            tracer_entries=100000,
            # log_func_retval=True,
            # log_func_args=True,
            # log_sparse=True,
            log_print=True
            ) as tracer:
            func(companyinfo, async_exec=args.async_exec)
    else:
        # tracer = VizTracer(output_file="/c/users/p.peng/aifinancialdocumentassistant/test/crewpydanticparser.json")
        func(companyinfo, async_exec=args.async_exec)
