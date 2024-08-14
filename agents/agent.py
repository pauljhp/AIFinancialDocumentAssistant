from crewai import Agent
from settings import (
    llm,
    function_llm,
    langfuse_callback_handler
)
from tools import RetrievalTools

def get_editor(tools):
    editor = Agent(
        role="Editor",
        goal=("Edit the raw text your team members created into succinct, "
        "precise and professional texts."),
        backstory=("You are an exprienced editor in the financial services and "
                "investment management industry. "),
        llm=llm,
        function_calling_llm=function_llm,
        tools=tools
        # callbacks=[langfuse_callback_handler]
    )
    return editor

def get_esg_analyst(tools):
    esg_report_analyst = Agent(
        role="esg_analyst",
        goal="Find relevant information related to the ESG tasks prescribed.",
        backstory=("You are an experienced ESG analyst. You have access to "
                "the relevant ESG and annual reports. Your task is to find the "
                "relevant information. Use only the information provided to you."
                ),
        llm=llm,
        tools=tools
    )
    return esg_report_analyst