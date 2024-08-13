from crewai import Task
from crewai_tools import BaseTool
from data_models import CompanyInfo
from typing import Optional, List, Dict
import toml




class NewESGReview:
    def __init__(
            self, 
            company_info: CompanyInfo, 
            task_descriptions: Dict[str, str]
            ):
        self.company = company_info
        self.task_descriptions = task_descriptions
        self.expected_output = ("Detailed analysis of each point, together with your scoring "
                "and justification. You should write your answers in bullet point "
                "format, and clearly quote your sources, as well as give detailed "
                "justification. "                
                )

    def corp_governance(self, tools: Optional[List[BaseTool]]):
        board_structure = Task(
            description=self.task_descriptions["corporate_governance"]["board_structure"],
            async_execution=True,
            tools=tools,
            expected_output=self.expected_output
        )
        executive_comp = Task(
            description=self.task_descriptions["corporate_governance"]["exec_compensation"],
            async_execution=True,
            tools=tools,
            expected_output=self.expected_output
        )
        shareholder_rights = Task(
            description=self.task_descriptions["corporate_governance"]["shareholder_rights"],
            async_execution=True,
            tools=tools,
            expected_output=self.expected_output
        )
        internal_controls = Task(
            description=self.task_descriptions["corporate_governance"]["internal_controls"],
            async_execution=True,
            tools=tools,
            expected_output=self.expected_output
        )
        governance_of_sustainability = Task(
            description=self.task_descriptions["corporate_governance"]["governance_of_sustainability"],
            async_execution=True,
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