from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from groundible_admin.root.mq_manager import (
    get_conn,
    mq_create_connection,
    start_consumer,
)
from groundible_admin.routers.auth_route import api_router as auth_router
from groundible_admin.routers.ums_route import api_router as ums_router
from groundible_admin.routers.misc_router import api_router as misc_router
from groundible_admin.routers.agent_route import api_router as agent_router
from groundible_admin.routers.maintenance.maintenace_route import (
    api_router as maintenace_router,
)
from groundible_admin.routers.survey_route import api_router as survey_router
import logging
from groundible_admin.listeners.admin_listener import admin_listener

LOGGER = logging.getLogger(__name__)


def intialize() -> FastAPI:
    app = FastAPI()
    app.include_router(router=auth_router)
    app.include_router(router=ums_router)
    app.include_router(router=misc_router)
    app.include_router(router=agent_router)
    app.include_router(router=survey_router)

    return app


app = intialize()


@app.on_event("startup")
async def startup_event():
    await mq_create_connection()
    print("MQ intialized")

    await start_consumer(listener=admin_listener)


@app.on_event("shutdown")
async def shutdown_event():
    # Cleanup code here
    connection = get_conn()
    await connection.close()
    print("MQ closed")


@app.get("/", status_code=307)
def root():
    return RedirectResponse(url="/docs")
