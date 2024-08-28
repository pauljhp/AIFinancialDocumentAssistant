from agents import (
    get_esg_analyst,
    get_editor,
    get_supervisor
)
from settings import function_llm, llm
from tasks import get_new_esg_review_task
from tools import (
    get_query_engine_tool,
    RetrievalTools,
    # SearchTools
)
from crewai_tools import DirectoryReadTool, FileReadTool, FileWriterTool
from tempfile import TemporaryDirectory
from crewai import Crew, Agent, Task, Process
from settings import (
    set_global_configs,  # TODO - change to a decorator
    langfuse_callback_handler,
    langfuse_handler,
    callback_manager
)
import os


temp_dir = TemporaryDirectory()
editor_tool = DirectoryReadTool(directory="workdir")


def analyze_esg(company_info, async_exec: bool = False):
    set_global_configs()  # TODO - change to a decorator
    retrieval_tool = RetrievalTools(
        company_info=company_info,
        collection_name="dev_esg_collection")

    # get_query_engine_tool(
    #         company_info=company_info,
    #         collection_name="dev_esg_collection"
    #     )

    tools = [retrieval_tool] + [
        # DirectoryReadTool("workdir"), 
        # FileReadTool(), 
        FileWriterTool()
        ]
    supervisor = get_supervisor(coworkers=["editor", "esg_analyst"])
    esg_agent = get_esg_analyst(
        tools=tools
    )
    editor = get_editor(tools=[editor_tool])
    tasks = get_new_esg_review_task(
        company_info,
        tools=tools,
        async_exec=async_exec,
        agent=esg_agent
    )
    # run_id = langfuse_handler.session_id
    crew = Crew(
        agents=[esg_agent],
        tasks=tasks,
        # process=Process.hierarchical,
        process=Process.sequential,
        verbose=True,
        # manager_llm=function_llm,
        # manager_agent=supervisor,
        memory=True,
        planning=False,
        planning_llm=function_llm,
        function_calling_llm=function_llm,
        output_log_file="outputs/outputlog.log",
        # step_callback=lambda x: langfuse_handler.on_tool_start(x, run_id=run_id, input_str="tool_call"),
        # task_callback=langfuse_handler.on_agent_finish,
        # config={"callbacks": callback_manager},
        embedder={
            "provider": "azure_openai",
            "config": {
                "model": 'text-embedding-ada-002',
                "api_base": os.getenv("AZURE_OPENAI_ENDPOINT"),
                "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
                "deployment_name": os.getenv("DEFAULT_EMBEDDING_MODEL")
            }
        },
    )
    result = crew.kickoff()
    return result
