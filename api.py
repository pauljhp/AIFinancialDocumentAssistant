from fastapi import FastAPI
from pydantic import BaseModel
from data_models import (
    CompanyInfo,
    ESGPillar,
    ESGSection,
    GetComputedResultsRequest
    )
from services import (
    acompute_pillar_result,
    read_from_sql,
    write_to_sql
)

app = FastAPI(
    debug=True,
    title="Investment AI Assistant API",
    summary="API for AI powered investment assistant",
)

@app.get("/")
def get_root():
    return {"Introduction": "Investment AI Assistant API"}

@app.get("/v0/esg/pre-computed/results/")
def get_results(items: GetComputedResultsRequest):
    company = CompanyInfo(
        composite_figi=items.composite_figi,
        SEDOL=items.SEDOL,
        ISIN=items.ISIN,
        short_name=items.short_name,
        name=items.name,
        report_year=items.report_year,
        aliases=items.aliases,
        identifier_fields=items.identifier_fields,
    )
    res = read_from_sql(
        company_info=company,
        esg_pillar=items.subsection
    )
    return res

@app.post("/v0/esg/compute-results/")
async def get_results(items: GetComputedResultsRequest):
    company = CompanyInfo(
        composite_figi=items.composite_figi,
        SEDOL=items.SEDOL,
        ISIN=items.ISIN,
        short_name=items.short_name,
        name=items.name,
        report_year=items.report_year,
        aliases=items.aliases,
        identifier_fields=items.identifier_fields,
    )
    res = await acompute_pillar_result(
        company=company,
        section=items.section,
        subsection=items.subsection,
        similarity_top_k=items.similarity_top_k
    )
    return res