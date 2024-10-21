from fastapi import FastAPI
from pydantic import BaseModel
from data_models import (
    CompanyInfo,
    ESGPillar,
    ESGSection,
    GetComputedResultsRequest,
    ChatRequest
    )
from services import (
    acompute_pillar_result,
    read_from_sql,
    write_to_sql,
    get_chat_engine,
    get_existing_companies,
    get_computed_company_list
)
from utils import get_random_uuid
from services.chat import chat_store


app = FastAPI(
    debug=True,
    title="Investment AI Assistant API",
    summary="API for AI powered investment assistant",
)

results = {}
chat_engines = {}
chat_engine_map = {}

@app.get("/")
def get_root():
    return {"Introduction": "Investment AI Assistant API"}

@app.get("/v0/esg/computed-companies")
def get_computed_companies():
    return get_computed_company_list()

@app.get("/v0/esg/collected-companies")
def get_collected_companies():
    return get_existing_companies()

@app.post("/v0/esg/pre-computed/results/")
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

@app.post("/v0/esg/chat/start-chat/")
def start_chat(company: CompanyInfo):
    session_id = str(get_random_uuid())
    engine = get_chat_engine(
        session_id=session_id,
        company_info=company
    )
    chat_engines[session_id] = engine
    chat_engine_map[session_id] = company
    return {"session_id": session_id}

@app.post("/v0/esg/chat/{session_id}")
def chat(items: ChatRequest):
    engine = chat_engines[items.session_id]
    res = engine.chat(items.question)
    return res # TODO - clean up sources

@app.get("/v0/esg/chat/get-chat-history/{session_id}")
def get_chat_history(session_id: str):
    return chat_store.get_messages(key=session_id)

@app.put("/v0/esg/chat/clear-chat/{session_id}")
def clear_chat(session_id: str):
    chat_engines.pop(session_id)
    chat_store.delete_messages(key=session_id)

@app.get("/v0/esg/chat/active-chat-sessions/")
def get_active_sessions():
    return chat_engine_map