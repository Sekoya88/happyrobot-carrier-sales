from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from typing import Optional

from app.config import settings
from app.dependencies import require_api_key
from app.schemas import (
    LoadOut, CarrierVerificationOut, CallRecordIn, CallRecordOut, MetricsOut
)
from domain.entities import CallRecord
from infrastructure.fmcsa_client import FMCSAClient
from infrastructure.load_repository import LoadRepository
from infrastructure.call_repository import CallRepository
from infrastructure.metrics_service import MetricsService


call_repo = CallRepository()
load_repo = LoadRepository(settings.loads_file)
fmcsa_client = FMCSAClient()
metrics_svc = MetricsService(call_repo)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await call_repo.init_db()
    yield


app = FastAPI(title="HappyRobot Carrier Sales API", lifespan=lifespan)
app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get(
    "/verify-carrier/{mc_number}",
    response_model=CarrierVerificationOut,
    dependencies=[Depends(require_api_key)],
)
async def verify_carrier(mc_number: str):
    result = await fmcsa_client.verify(mc_number)
    return CarrierVerificationOut(**result.__dict__)


@app.get(
    "/loads",
    response_model=list[LoadOut],
    dependencies=[Depends(require_api_key)],
)
async def search_loads(
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    equipment_type: Optional[str] = Query(None),
):
    results = load_repo.search(origin, destination, equipment_type)
    return [LoadOut(**l.__dict__) for l in results]


@app.get(
    "/loads/{load_id}",
    response_model=LoadOut,
    dependencies=[Depends(require_api_key)],
)
async def get_load(load_id: str):
    load = load_repo.get_by_id(load_id)
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    return LoadOut(**load.__dict__)


@app.post(
    "/calls",
    response_model=CallRecordOut,
    dependencies=[Depends(require_api_key)],
)
async def record_call(body: CallRecordIn):
    record = CallRecord(**body.model_dump())
    record_id = await call_repo.save(record)
    return CallRecordOut(id=record_id, **body.model_dump())


@app.get(
    "/metrics",
    response_model=MetricsOut,
    dependencies=[Depends(require_api_key)],
)
async def get_metrics():
    return await metrics_svc.compute()
