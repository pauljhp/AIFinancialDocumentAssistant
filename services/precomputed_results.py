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
import pandas as pd
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
    res = dict(zip(columns, 
                   [
        str(results.company_info.composite_figi or ""),
        str(results.company_info.ISIN or ""),
        str(results.company_info.SEDOL or ""),
        str(results.company_info.short_name or ""),
        str(results.company_info.report_year),
        str(results.esg_pillar or ""),
        str(results.results or ""),
        json.dumps(results.result_source),
        results.update_date.strftime("%Y-%m-%d %H:%M:%S")
    ]))
    res = pd.Series(res).to_frame().T
    # query = (
    #     f"INSERT INTO {result_table_name} "
    #     f"({', '.join(columns)}) "
    #     f"""VALUES ({', '.join([f"'{i}'" for i in res])}) """
    #     )
    with engine.connect() as connection:
        res.to_sql(result_table_name, if_exists="append", con=connection, index=False)
        # connection.execute(sqlalchemy.text(query))
        # connection.commit()

def read_from_sql(company_info: CompanyInfo, esg_pillar: ESGPillar) -> List[ComputedResults]:
    query = (
        f"WITH temp AS "
        f"(SELECT * FROM {result_table_name} "
        f"WHERE (ISIN = '{str(company_info.ISIN or '')}' or SEDOL = '{str(company_info.SEDOL or '')}' or composite_figi = '{str(company_info.composite_figi or '')}') "
        f"AND (esg_pillar = '{esg_pillar}') )"
        f"SELECT * FROM temp WHERE update_date = ( SELECT MAX(update_date) FROM temp)"
    )
    connection = engine.connect()
    
    # results = pd.read_sql(query, con=connection)
    # results = results.astype({"update_date": "datetime64[ns]"})
    # results["result_source"] = results["result_source"].apply(json.loads)

    res = connection.execute(sqlalchemy.text(query)).fetchall()
    results = [dict(zip(columns, r)) for r in res]
    results = [ComputedResults(
        company_info=company_info,
        esg_pillar=esg_pillar,
        results=res.get("results"),
        result_source=json.loads(res.get("result_source")),
        update_date=res.get("update_date")#json.loads(datetime.datetime.strptime(res.get("update_date"), "%Y-%m-%d %H:%M:%S"))
        ) for res in results
        ]
    return results

def get_computed_company_list() -> List[CompanyInfo]:
    query = (
        "SELECT composite_figi, ISIN, SEDOL, short_name, report_year "
        f"FROM {result_table_name} "
        "WHERE (composite_figi IS NOT NULL) or (ISIN IS NOT NULL) or (SEDOL IS NOT NULL) "
    )
    with engine.connect() as conn:
        res = pd.read_sql(sql=query, con=conn)
    res.drop_duplicates(subset=["composite_figi", "ISIN", "SEDOL"])
    results = [
        CompanyInfo(
            composite_figi=r.composite_figi,
            ISIN=r.ISIN,
            SEDOL=r.SEDOL,
            name=r.short_name,
            short_name=r.short_name,
            report_year=r.report_year,
            )
        for _, r in res.iterrows()
        ]
    return results

def get_existing_companies(collection_name="esg_reports") -> List[CompanyInfo]:
    # TODO - handle existence in more than one collection
    """get list of companeis already in the collection"""
    query = (
        "SELECT name, composite_figi, ISIN, SEDOL, report_year, collection_name, update_date  FROM "
        "(SELECT name, composite_figi, ISIN, SEDOL, report_year, collection_name, update_date,  "
	    "ROW_NUMBER() OVER(PARTITION BY composite_figi ORDER BY update_date DESC) rn "
	    "FROM existing_companies ) a "
        f"WHERE a.rn = 1 AND collection_name = '{collection_name}'; "
    )
    with engine.connect() as conn:
        res = pd.read_sql(query, con=conn)
    res = res.astype(
        {
            "composite_figi": str,
            "ISIN": str,
            "SEDOL": str,
            "report_year": int,
            "collection_name": str,
            "update_date": "datetime64[ns]",
            "name": str
         }
    )
    results = [
        CompanyInfo(
            composite_figi=str(r.composite_figi or ""),
            ISIN=str(r.ISIN or ""),
            SEDOL=str(r.SEDOL or ""),
            short_name=str(r["name"] or ""),
            name=str(r["name"] or ""),
            report_year=r.report_year
        ) for _, r in res.iterrows()
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
    sources = {}
    for node in res.source_nodes:
        if node.metadata.get("url") not in sources.keys():
            sources[node.metadata.get("url")] = [node.metadata.get("page_number")]
        else:
            sources[node.metadata.get("url")].append(node.metadata.get("page_number"))
    
    res = ComputedResults(
        company_info=company,
        esg_pillar=subsection,
        results=res.response,
        result_source=sources,
        update_date=datetime.datetime.today()
    )
    return res