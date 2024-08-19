from crewai import Task, Agent
from crewai_tools import BaseTool
from data_models import CompanyInfo
from typing import Optional, List, Dict
import toml
import utils


def populate_company_name(
        task_description_template: str, 
        company_info: CompanyInfo
        ) -> str:
    """populate the task description with company name
    :param task_description_template: The template to use. Should be formatted 
    like this:
    `instruction`
    <rubrics>
    `rubrics`
    </rubrics>
    `according to this, access {company}'s performance`
    """
    company = utils.coalesce(company_info.short_name, company_info.name)
    instruction = eval("f" + "'''" + task_description_template + \
                       "'''" + ".format(company)" )
    return instruction

class NewESGReview:
    def __init__(
            self, 
            company_info: CompanyInfo,
            task_descriptions: Dict[str, str],
            agent: Optional[Agent]=None,
            async_exec: bool=False,
            ):
        self.company = company_info
        self.task_descriptions = task_descriptions
        self.expected_output = ("Detailed analysis of each point, together with your scoring "
                "and justification. You should write your answers in bullet point "
                "format, and clearly quote your sources, as well as give detailed "
                "justification. " 
                )
        self.async_exec = async_exec
        self.agent = agent # TODO - bind tools with agents

    def corp_governance(
            self, 
            tools: Optional[List[BaseTool]],
            ):
        board_structure = Task(
            description=populate_company_name(
                self.task_descriptions["corporate_governance"]["board_structure"],
                company_info=self.company),
            async_execution=self.async_exec,
            tools=tools,
            agent=self.agent,
            expected_output=self.expected_output
        )
        executive_comp = Task(
            description=populate_company_name(
                self.task_descriptions["corporate_governance"]["exec_compensation"],
                company_info=self.company),
            async_execution=self.async_exec,
            tools=tools,
            agent=self.agent,
            expected_output=self.expected_output
        )
        shareholder_rights = Task(
            description=populate_company_name(
                self.task_descriptions["corporate_governance"]["shareholder_rights"],
                company_info=self.company),
            async_execution=self.async_exec,
            agent=self.agent,
            tools=tools,
            expected_output=self.expected_output
        )
        internal_controls = Task(
            description=populate_company_name(
                self.task_descriptions["corporate_governance"]["internal_controls"],
                company_info=self.company),
            async_execution=self.async_exec,
            agent=self.agent,
            tools=tools,
            expected_output=self.expected_output
        )
        governance_of_sustainability = Task(
            description=populate_company_name(
                self.task_descriptions["corporate_governance"]["governance_of_sustainability"],
                company_info=self.company),
            async_execution=self.async_exec,
            agent=self.agent,
            tools=tools,
            expected_output=self.expected_output
        )
        return [
            board_structure,
            executive_comp,
            shareholder_rights,
            internal_controls,
            governance_of_sustainability
        ]

    # def edi_hcm()