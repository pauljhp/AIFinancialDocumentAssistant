from agents import (
    get_esg_analyst,
    get_editor,
    supervisor
)
from settings import function_llm
from tasks import get_new_esg_review_task
from tools import RetrievalTools
from crewai import Crew, Agent, Task, Process
from settings import set_global_configs # TODO - change to a decorator


def analyze_esg(company_info):
    set_global_configs()
    tools=[
            RetrievalTools(
                company_info=company_info, 
                collection_name="dev_esg_collection" # FIXME - change to production collection
                )
            ]
    esg_agent = get_esg_analyst(
        tools=tools
        )
    tasks = get_new_esg_review_task(company_info, tools=tools)
    crew = Crew(
        agents=[esg_agent],
        tasks=tasks,
        process=Process.hierarchical,
        verbose=True,
        manager_llm=function_llm
    )
    crew.kickoff()