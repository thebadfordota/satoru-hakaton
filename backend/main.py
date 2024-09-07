import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.loggin_config import setup_logging
from settings import settings

app = FastAPI(title=settings.PROJECT_TITLE)

app.include_router(router, prefix="/api")
setup_logging()


@app.get("/", include_in_schema=False)
async def check_health():
    return JSONResponse('Server worked!')


if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.SERVER_RELOAD,
        reload_dirs=['app'],
        workers=settings.SERVER_WORKERS_COUNT,
    )
