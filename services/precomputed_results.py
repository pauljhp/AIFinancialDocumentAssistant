"""read and write precomputed results to SQL DB"""

from utils import SQLDatabase
from data_models import CompanyInfo, ESGPillar, ComputedResults
import os
import sqlalchemy
import json
from typing import Dict, List, Any



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

def read_from_sql(company_info: CompanyInfo, esg_pillar: ESGPillar) -> List[Dict[str, Any]]:
    query = (
        f"SELECT * FROM {result_table_name} "
        f"WHERE (ISIN = '{str(company_info.ISIN or '')}' or SEDOL = '{str(company_info.SEDOL or '')}' or composite_figi = '{str(company_info.composite_figi or '')}') "
        f"AND (esg_pillar = '{esg_pillar}') "
    )
    connection = engine.connect()
    res = connection.execute(sqlalchemy.text(query)).fetchall()
    results = [dict(zip(columns, r)) for r in res]
    return results