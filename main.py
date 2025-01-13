import uvicorn
from loguru import logger
from agent import router_conference
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()

class APIRequest(BaseModel):
    pdf_path: str


@app.post("/api/task2")
def recommender(body: APIRequest):
    logger.info(f"TASK 2 | {body.pdf_path}")
    
    object = router_conference(
        pdf_path=body.pdf_path
    )

    return {
        "content": f"{object.conference_title}",
        "metadata": f"{body.pdf_path}"
    }


@app.post("/api/task1")
def classifier(body: APIRequest):
    logger.info(f"TASK 1 | {body.pdf_path}")
    return {
        "message": "############@)))############"
    }


