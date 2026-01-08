from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import api
from app.utils.logger import logger

app = FastAPI(
    title="职能沟通翻译助手API",
    description="基于AI的产品与技术沟通翻译服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)


@app.on_event("startup")
async def startup_event():
    logger.info("应用启动")
    logger.info(f"API密钥已配置: {bool(settings.QWEN_API_KEY)}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("应用关闭")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=settings.DEBUG)

