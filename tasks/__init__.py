import toml
from .esg_review import NewESGReview
from pathlib import Path


curr_dir_path = Path(__file__).parent.resolve()
task_descriptions = toml.load(curr_dir_path.joinpath("task_descs.toml").as_posix())

def get_new_esg_review_task(company_info, tools):
    review_cls = NewESGReview(
        company_info=company_info, 
        task_descriptions=task_descriptions["esg_tasks"]
        )
    return review_cls.corp_governance(tools=tools) # TODO - complete whole thing