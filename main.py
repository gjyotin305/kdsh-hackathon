import uvicorn
from loguru import logger
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()

class APIRequest(BaseModel):
    pdf_path: str


@app.post("/api/task1")
def classifier(body: APIRequest):
    logger.info(f"TASK 1 | {body.pdf_path}")


