from fastapi import FastAPI, Response
import requests
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Proxy Server"}

@app.get("/proxy")
def proxy_download(url: str, response: Response):
    try:
        # URL se data fetch karo
        r = requests.get(url)
        
        # Content-Type set karo XML ke liye
        response.headers["Content-Type"] = "application/xml; charset=utf-8"
        
        # Raw content lo
        content = r.text
        
        # Agar response quotes me wrapped hai, toh unhe remove karo
        if content.startswith('"') and content.endswith('"'):
            content = content[1:-1]
        
        # Escape sequences replace karo
        content = content.replace('\\"', '"')
        content = content.replace('\\n', '\n')
        content = content.replace('\\u003C', '<')
        content = content.replace('\\u003E', '>')
        content = content.replace('\\\\', '\\')
        
        # Return karo as plain text (FastAPI automatically converts to Response)
        return Response(content=content, media_type="application/xml")
        
    except Exception as e:
        response.headers["Content-Type"] = "text/plain; charset=utf-8"
        return f"Error: {str(e)}"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
