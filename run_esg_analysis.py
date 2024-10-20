from typing import Tuple, Any, get_args, Literal
from qdrant_client.http import models
from argparse import ArgumentParser
import asyncio
import sqlalchemy
import datetime
import pandas as pd

from dbs import qdrantclient
from tasks import task_descriptions
from data_models import existing_companies_column_names, CompanyInfo, ESGSection
from services.precomputed_results import acompute_pillar_result, write_to_sql
from utils import SQLDatabase


engine = SQLDatabase().engine

def _get_existing_companies(
        collection_name: str, 
        filter: models.Filter,
        chunk_size: int=100,
        offset: int=0
        ) -> Tuple[Tuple[Any], str]:
    res, offset = qdrantclient.scroll(
        collection_name=collection_name,
        scroll_filter=filter,
        limit=chunk_size,
        with_payload=True,
        with_vectors=False,
        offset=offset,
        timeout=150
    )
    
    res = {
            (
            "'" + str(r.payload.get("composite_figi", "") or "") + "'",
            "'" + str(r.payload.get("ISIN", "") or "") + "'",
            "'" + str(r.payload.get("SEDOL", "") or "") + "'", 
            str(r.payload.get("report_year", 0) or ""),
            "1", # `exists_in_collection``
            "'" + datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S") + "'",
            "'" + collection_name + "'",
            "'" + str(r.payload.get("company name", "") or "") + "'",
        ) 
        for r in res
        }
    # res = [dict(zip(get_args(existing_companies_column_names), r)) for r in res]
    return res, offset # TODO update aget_existing_companies

def write_result_to_sql(results: Tuple[Any]):
    """when a new record is written or confirmed to exist, only a new row will
    be added. At retrieval time just query the latest record date for each
    unique name.

    When deleting a record, set the `exists_in_collection` to 0 and update
     the `update_date` column
    """
    for res in results:
        query= (
            "INSERT INTO existing_companies "
            f"({', '.join(get_args(existing_companies_column_names))}) "
            f"""VALUES ({', '.join(res)})"""
        )
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text(query))
            conn.commit()


def update_existing_companies(
        collection_name: str, 
        report_year: int=2023,
        chunk_size: int=100,
        write_to_sql: bool=False
    ):
    filter = models.Filter(
            must = [
                models.FieldCondition(
                    key="report_year",
                    match=models.MatchValue(
                        value=report_year, 
                    )
                ),
            ]
        )
    n = qdrantclient.count(
        collection_name=collection_name, 
        count_filter=filter
        ).count
    results = []
    offset = 0
    for _ in range(0, n, chunk_size):
        res, offset = _get_existing_companies(
            collection_name=collection_name,
            filter=filter,
            chunk_size=chunk_size,
            offset=offset
        )
        if write_to_sql:
            write_result_to_sql(res)
        results += res
    return results

# Mode = Literal[
#     "update_existence_list",
#     "analyze_company"
# ]

def get_existing_companies(collection_name="esg_reports"):
    # TODO - handle existence in more than one collection
    """get list of companeis already in the collection"""
    query = (
        "SELECT name, composite_figi, ISIN, SEDOL, report_year, collection_name, update_date  FROM "
        "(SELECT composite_figi, ISIN, SEDOL, report_year, collection_name, update_date, name, "
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
    return res



if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--mode", "-m", dest="mode", default="update_existence_list")
    parser.add_argument("--year", "-y", dest="year", type=int, default=2023)
    parser.add_argument("--collection-name", "-cn", dest="collection_name", default="esg_reports")
    args = parser.parse_args()

    match args.mode:
        case "update_existence_list" :
            update_existing_companies(
                collection_name=args.collection_name, 
                report_year=args.year, 
                write_to_sql=True
                )
        case "analyze_company":
            existing_companies = get_existing_companies()
            for _, row in existing_companies.iterrows():
                print(row["name"])
                company = CompanyInfo(
                    composite_figi=row.composite_figi,
                    ISIN=row.ISIN,
                    SEDOL=row.SEDOL,
                    short_name=row["name"],
                    name=row["name"],
                    report_year=row.report_year,
                )
                for section in get_args(ESGSection):
                    print(section)
                    for subsection in task_descriptions["esg_datafields"]["corporate_governance"].keys():
                        res = asyncio.run(
                            acompute_pillar_result(
                                company=company,
                                section=section,
                                subsection=subsection,
                                similarity_top_k=50,
                                num_queries=10
                            )
                        )
                        write_to_sql(res)
                    print("----\n")
                print("\n=====\n")