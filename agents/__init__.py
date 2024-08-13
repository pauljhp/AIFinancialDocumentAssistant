from .agent import (
    get_editor,
    get_esg_analyst
)
from settings import llm, function_llm, langfuse_callback_handler
from crewai import Agent

supervisor = Agent(
    role="supervisor",
    goal=("Your goal is to understand the task, plan its execution, "
    "and delegate it to your members according to their strengths."),
    backstory=("You are an exprienced manager in the investment management  "
            "industry. "),
    llm=llm,
    function_calling_llm=function_llm,
    # callbacks=[langfuse_callback_handler]
)