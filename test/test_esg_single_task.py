from tools import RetrievalTools
from data_models import CompanyInfo 
from agents import get_esg_analyst
from tasks import get_new_esg_review_task
from crewai.tools.tool_usage import ToolUsage
from langchain_core.agents import AgentAction
from crewai.tools.tool_calling import InstructorToolCalling, ToolCalling
from langchain.globals import set_debug
from crewai.utilities import I18N, Converter


# set_debug(True)
company_info = CompanyInfo(name="Chroma")
retrieval_tool = RetrievalTools(
    company_info=company_info, 
    collection_name="dev_esg_collection"
    )
analyst = get_esg_analyst(tools=[retrieval_tool])
task = get_new_esg_review_task(
    company_info=company_info, 
    tools=[retrieval_tool], 
    agent=analyst
    )
converter = Converter(
            text=f"Only tools available:\n###\n{retrieval_tool.name}\n\nReturn a valid schema for the tool, the tool name must be exactly equal one of the options, use this text to inform the valid output schema:\n\n{retrieval_tool.args_schema}```",
            llm=analyst.function_calling_llm,
            model=ToolCalling,
            instructions=
                """\
        The schema should have the following structure, only two keys:
        - tool_name: str
        - arguments: dict (with all arguments being passed)

        Example:
        {"tool_name": "tool name", "arguments": {"arg_name1": "value", "arg_name2": 2}}""",
            max_attempts=1,
        )
# calling = converter.to_pydantic()
# print(calling)
analyst.execute_task(task[0])

# agent_action = AgentAction(
#     tool=retrieval_tool.name,
#     tool_input='{"question": "What is chroma"}',
#     log="I need to try this tool."
# )
# tool_usage = ToolUsage(
#             tools_handler=analyst.agent_executor.tools_handler,  # type: ignore # Argument "tools_handler" to "ToolUsage" has incompatible type "ToolsHandler | None"; expected "ToolsHandler"
#             tools=analyst.tools,  # type: ignore # Argument "tools" to "ToolUsage" has incompatible type "Sequence[BaseTool]"; expected "list[BaseTool]"
#             original_tools=analyst.tools,
#             tools_description=analyst.agent_executor.tools_description,
#             tools_names=analyst.agent_executor.tools_names,
#             function_calling_llm=analyst.agent_executor.function_calling_llm,
#             task=task,
#             agent=analyst,
#             action=agent_action,
#         )
# tool_usage.parse("I need to try this tool.")