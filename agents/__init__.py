from .agent import (
    get_editor,
    get_esg_analyst
)
from settings import (
    llm, 
    function_llm, 
    langfuse_callback_handler
)
from crewai import Agent
from crewai_tools import Tool
from typing import List
# from tools import RetrievalTools


def get_supervisor(
        # tools: List[Tool]
        coworkers: List[str]
        ):
    supervisor = Agent(
        role="supervisor",
        goal=("Your goal is to understand the task, plan its execution, "
        "and delegate it to your members according to their strengths."
        f"You have the following coworkers: {','.join(coworkers)}"),
        backstory=("You are an exprienced manager in the investment management  "
                "industry. "),
        llm=llm,
        # function_calling_llm=function_llm,
        # tools=tools
        # callbacks=[langfuse_callback_handler]
    )
    return supervisor