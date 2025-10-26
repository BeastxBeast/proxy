from fastapi import FastAPI
import requests
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Proxy Server"}

@app.get("/proxy")
def proxy_download(url: str):
    response = requests.get(url)
    return response.text

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
