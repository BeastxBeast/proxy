from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Proxy Server"}

@app.get("/proxy")
def proxy_download(url: str):
    response = requests.get(url)
    return response.text
