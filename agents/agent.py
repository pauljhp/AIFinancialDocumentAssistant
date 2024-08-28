from crewai import Agent
from settings import (
    llm,
    function_llm,
    # langfuse_callback_handler
)
# from tools import RetrievalTools

def get_editor(tools):
    editor = Agent(
        role="editor",
        goal=("Edit the raw text your team members created into succinct, "
        "precise and professional texts."),
        backstory=("You are an exprienced editor in the financial services and "
                "investment management industry. "),
        llm=llm,
        max_iter=10, # FIXME - either pass to config or set global constant
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
                "If you use the `Vector DB Retrieval Tool` tool, you must "
                "pass in a question."
                ),
        llm=llm,
        allow_delegation=False,
        # function_calling_llm=function_llm,
        max_iter=5, # FIXME - either pass to config or set global constant
        tools=tools,
        verbose=True
    )
    return esg_report_analyst