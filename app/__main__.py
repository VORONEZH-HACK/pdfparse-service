import logging
import shutil

import spacy
import uvicorn
from app.iparser import ParserForResume
from fastapi import FastAPI, File, UploadFile

app = FastAPI()

nlp = spacy.load("ru_core_news_sm")

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    filename='logs.txt',
)

log = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    log.info('Initializing API ...')


@app.on_event("shutdown")
async def shutdown_event():
    log.info('Shutting down API')


@app.post("/parse_resume/")
async def parse_resume(file: UploadFile = File(...)):
    with open(file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    data = ParserForResume('./file.filename').get_data()

    return data


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
