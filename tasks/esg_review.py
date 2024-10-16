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
    instruction = eval("f" + "'''" + task_description_template +
                       "'''" + ".format(company)")
    return instruction


class NewESGReview:
    def __init__(
            self,
            company_info: CompanyInfo,
            task_descriptions: Dict[str, str],
            agent: Optional[Agent] = None,
            async_exec: bool = False,
    ):
        self.company = company_info
        self.task_descriptions = task_descriptions
        self.intermediate_expected_output = (
            "Collection detailed information about each point, and structure "
            "them in bullet point formats so your teammates can use your outputs. "
            "clearly quote your sources, as well as give detailed "
            "justification. Do no just give one answer, provide details to the answer. "
            "It's ok if you can't get all the information neccessary. "
            "Try to list all the evidence supporting the point. "
        )
        self.expected_output = (
            "Detailed analysis of each point (including subpoints), together with your scoring "
            "and justification. Justification is more important than scoreing. "
            "If you can't come with a total score it's fine. "
            "You should write your answers in bullet point "
            "format, and clearly quote your sources, as well as give detailed "
            "justification. Do no just give one answer, provide details to the answer "
            "and your through process. If the template asks for multiple aspects, "
            "try to cover all aspects in bullet points. "
            "It's ok if you can't get all the information neccessary. "
            "Try to list all the evidence supporting the point you can find without giving a score. "
        )
        self.async_exec = async_exec
        self.agent = agent  # TODO - bind tools with agents

    def __get_task(
            self,
            section: str,
            sub_section: str,
            expected_output: str,
            tools: List[BaseTool],
            output_file: Optional[str] = None
    ) -> Task:
        task = Task(
            description=populate_company_name(
                self.task_descriptions[section][sub_section],
                company_info=self.company),
            async_execution=self.async_exec,
            tools=tools,
            agent=self.agent,
            expected_output=expected_output,
            output_file=output_file if output_file else f"workdir/{section}_{sub_section}_data.md"
        )
        return task

    def _corp_governance_data(
            self,
            tools: Optional[List[BaseTool]],
    ) -> List[Task]:
        section = "corporate_governance"
        board_structure = self.__get_task(
            section=section,
            sub_section="board_structure",
            expected_output=self.intermediate_expected_output,
            tools=tools
        )

        executive_comp = self.__get_task(
            section=section,
            sub_section="exec_compensation",
            expected_output=self.intermediate_expected_output,
            tools=tools
        )

        shareholder_rights = self.__get_task(
            section=section,
            sub_section="shareholder_rights",
            expected_output=self.intermediate_expected_output,
            tools=tools
        )

        internal_controls = self.__get_task(
            section=section,
            sub_section="internal_controls",
            expected_output=self.intermediate_expected_output,
            tools=tools
        )

        governance_of_sustainability = self.__get_task(
            section=section,
            sub_section="governance_of_sustainability",
            expected_output=self.intermediate_expected_output,
            tools=tools
        )

        return [
            board_structure,
            executive_comp,
            shareholder_rights,
            internal_controls,
            governance_of_sustainability
        ]

    def corp_governance(
            self,
            tools: Optional[List[BaseTool]],
    ) -> List[BaseTool]:
        section = "corporate_governance"

        board_structure = self.__get_task(
            section=section,
            sub_section="board_structure",
            expected_output=self.expected_output,
            tools=tools,
            output_file=f"workdir/{section}_board_structure"
        )

        executive_comp = self.__get_task(
            section=section,
            sub_section="exec_compensation",
            expected_output=self.expected_output,
            tools=tools,
            output_file=f"workdir/{section}_executive_compensation"
        )

        shareholder_rights = self.__get_task(
            section=section,
            sub_section="shareholder_rights",
            expected_output=self.expected_output,
            tools=tools,
            output_file=f"workdir/{section}_shareholder_rights"
        )

        internal_controls = self.__get_task(
            section=section,
            sub_section="internal_controls",
            expected_output=self.expected_output,
            tools=tools,
            output_file=f"workdir/{section}_internal_controls"
        )

        governance_of_sustainability = self.__get_task(
            section=section,
            sub_section="governance_of_sustainability",
            expected_output=self.expected_output,
            tools=tools,
            output_file=f"workdir/{section}_governance_of_sustainability"
        )
        return [
            board_structure,
            executive_comp,
            shareholder_rights,
            internal_controls,
            governance_of_sustainability
        ]

    def _edi_hcm(
            self,
            tools: Optional[List[BaseTool]],
    ) -> List[BaseTool]:
        section = "edi_hcm"
        diversity = self.__get_task(
            section=section,
            sub_section="diversity_in_leadership",
            expected_output=self.intermediate_expected_output,
            tools=tools,
        )
        wpe = self.__get_task(
            section=section,
            sub_section="workplace_equity",
            expected_output=self.intermediate_expected_output,
            tools=tools,
        )
        hcm = self.__get_task(
            section=section,
            sub_section="human_capital_management",
            expected_output=self.intermediate_expected_output,
            tools=tools,
        )
        return [
            diversity,
            wpe,
            hcm
        ]
    
    def _climate_change(
            self,
            tools: Optional[List[BaseTool]],
    ) -> List[BaseTool]:
        section = "climate_change"
        transition = self.__get_task(
            section=section,
            sub_section="transition_risk",
            expected_output=self.intermediate_expected_output,
            tools=tools,
        )
        pcr = self.__get_task(
            section=section,
            sub_section="physical_climate_risk",
            expected_output=self.intermediate_expected_output,
            tools=tools,
        )
        return [
            transition,
            pcr
        ]
