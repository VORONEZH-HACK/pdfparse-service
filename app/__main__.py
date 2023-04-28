from fastapi import FastAPI, UploadFile, File


import pdfplumber
import spacy
import uvicorn
import logging
import re


app = FastAPI()

nlp = spacy.load("ru_core_news_sm")

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
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
    print(file)
    with pdfplumber.open(file.file) as pdf:
        text = '\n'.join(page.extract_text() for page in pdf.pages)


    res = {}

    doc = nlp(text)

    name = ' '.join([entity.text for entity in doc.ents if entity.label_ == 'PERSON'])
    if len(name) > 3:
        res['name'] = name
    birth_date = re.findall(r'\d{2}[-/]\d{2}[-/]\d{4}', text)
    if birth_date:
        res['birth_date'] = birth_date
    phone = re.findall(r'\+?\d{1,4}?[-. ]?\(?\d{1,3}?\)?[-. ]?\d{1,4}[-. ]?\d{1,9}', text)
    if phone:
        res['phone'] = phone[0]
    
    email = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', text)
    if email:
        res['email'] = email[0]

    links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    log.info(links)

    return res


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
