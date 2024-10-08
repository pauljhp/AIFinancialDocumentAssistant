import toml
from .esg_review import NewESGReview
from pathlib import Path
from data_models import CompanyInfo
from typing import List, Optional
from crewai import Agent
from crewai_tools import Tool


curr_dir_path = Path(__file__).parent.resolve()
task_descriptions = toml.load(
    curr_dir_path.joinpath("task_descs.toml").as_posix())


def get_new_esg_data_collection_task(
        company_info: CompanyInfo,
        tools: List[Tool],
        agent: Optional[Agent],
        async_exec: bool = False,
):
    review_cls = NewESGReview(
        company_info=company_info,
        task_descriptions=task_descriptions["esg_tasks"],
        async_exec=async_exec,
        agent=agent
    )
    return review_cls._corp_governance_data(
        tools=tools,
    )


def get_new_esg_review_task(
        company_info: CompanyInfo,
        tools: List[Tool],
        agent: Optional[Agent],
        async_exec: bool = False,
):
    review_cls = NewESGReview(
        company_info=company_info,
        task_descriptions=task_descriptions["esg_tasks"],
        async_exec=async_exec,
        agent=agent
    )
    return review_cls.corp_governance(
        tools=tools,
    )  # TODO - complete whole thing
