"""read and write precomputed results to SQL DB"""

from utils import SQLDatabase
from data_models import CompanyInfo, ESGPillar, ESGSection, ComputedResults
from dbs import arun_esg_pillar
from tasks import get_pillar_template, get_pillar_datafields
from settings import set_global_configs
import datetime
from llama_index.core import get_response_synthesizer
from llama_index.core.response_synthesizers import(
    ResponseMode,
    TreeSummarize
) 
import os
import sqlalchemy
import json
from typing import Dict, List, Any
from settings import li_llm_4o


set_global_configs()
engine = SQLDatabase().engine

result_table_name = os.getenv("RESULT_SQL_TABLE")
columns = [
    "composite_figi",
	"ISIN",
	"SEDOL",
	"short_name",
	"report_year",
	"esg_pillar",
	"results",
	"result_source",
	"update_date",
]

def write_to_sql(results: ComputedResults):
    """write result to SQL"""
    res = [
        str(results.company_info.composite_figi or ""),
        str(results.company_info.ISIN or ""),
        str(results.company_info.SEDOL or ""),
        str(results.company_info.short_name or ""),
        str(results.company_info.report_year),
        str(results.esg_pillar),
        str(results.results),
        json.dumps(results.result_source),
        results.update_date.strftime("%Y-%m-%d %H:%M:%S")
    ]
    query = (
        f"INSERT INTO {result_table_name} "
        f"({', '.join(columns)}) "
        f"""VALUES ({', '.join([f"'{i}'" for i in res])}) """
        )
    with engine.connect() as connection:
        connection.execute(sqlalchemy.text(query))
        connection.commit()

def read_from_sql(company_info: CompanyInfo, esg_pillar: ESGPillar) -> List[ComputedResults]:
    query = (
        f"WITH temp AS "
        f"(SELECT * FROM {result_table_name} "
        f"WHERE (ISIN = '{str(company_info.ISIN or '')}' or SEDOL = '{str(company_info.SEDOL or '')}' or composite_figi = '{str(company_info.composite_figi or '')}') "
        f"AND (esg_pillar = '{esg_pillar}') )"
        f"SELECT * FROM temp WHERE update_date = ( SELECT MAX(update_date) FROM temp)"
    )
    connection = engine.connect()
    res = connection.execute(sqlalchemy.text(query)).fetchall()
    results = [dict(zip(columns, r)) for r in res]
    results = [ComputedResults(
        company_info=company_info,
        esg_pillar=esg_pillar,
        results=res.get("results"),
        result_source=json.loads(res.get("result_source")),
        update_date=json.loads(datetime.datetime.strptime(res.get("update_date"), "%Y-%m-%d %H:%M:%S"))
        )
        ]
    return results

async def acompute_pillar_result(
        company: CompanyInfo,
        section: ESGSection,
        subsection: ESGPillar,
        similarity_top_k: int=10,
        num_queries: int=10
    ):
    synthesizer = get_response_synthesizer(
        structured_answer_filtering=True,
        llm=li_llm_4o,
        response_mode=ResponseMode.REFINE,
        use_async=True,
    )
    nodes = await arun_esg_pillar(
        company_info=company,
        section=section,
        subsection=subsection,
        similarity_top_k=similarity_top_k,
        num_queries=num_queries,
        recursive=True # TODO - look into search time out issue with non-recursive
    )
    query = get_pillar_template(
        company=company,
        section=section,
        subsection=subsection
    )
    res = await synthesizer.asynthesize(query=query, nodes=nodes)
    
    source_files = {(node.metadata.get("source"), node.metadata.get("page_number"))
                    for node in nodes}
    sources = {source_file: [] for source_file in source_files}
    for node in res.source_nodes:
        sources[(node.metadata.get("source"), node.metadata.get("page_number"))].append(node.metadata.get("page_number"))
    sources = {sf: set(pages) for sf, pages in sources.items()}
    
    res = ComputedResults(
        company_info=company,
        esg_pillar=subsection,
        results=res.response,
        result_source=sources,
        update_date=datetime.datetime.today()
    )
    return res