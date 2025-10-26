from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import StreamingResponse
import requests
import uvicorn
import re

app = FastAPI()

class VideoStreamer:
    def __init__(self):
        self.chunk_size = 8192  # 8KB chunks
    
    def stream_video(self, video_url: str, range_header: str = None):
        try:
            headers = {}
            if range_header:
                headers['Range'] = range_header
            
            # Stream the video from original source
            response = requests.get(video_url, headers=headers, stream=True, timeout=30)
            
            # Forward appropriate headers
            resp_headers = {}
            if 'Content-Type' in response.headers:
                resp_headers['Content-Type'] = response.headers['Content-Type']
            if 'Content-Length' in response.headers:
                resp_headers['Content-Length'] = response.headers['Content-Length']
            if 'Content-Range' in response.headers:
                resp_headers['Content-Range'] = response.headers['Content-Range']
            if 'Accept-Ranges' in response.headers:
                resp_headers['Accept-Ranges'] = response.headers['Accept-Ranges']
            
            # Create generator for streaming
            def generate():
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    yield chunk
            
            status_code = 206 if range_header else 200
            
            return StreamingResponse(
                generate(),
                status_code=status_code,
                headers=resp_headers,
                media_type=response.headers.get('Content-Type', 'video/mp4')
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Streaming failed: {str(e)}')

# Initialize streamer
streamer = VideoStreamer()

@app.get("/")
def home():
    return {"message": "Video Streaming & MPD Proxy Server", "endpoints": {
        "proxy": "/proxy?url=VIDEO_URL",
        "health": "/health"
    }}

@app.get("/proxy")
async def proxy_download(url: str, response: Response):
    try:
        # Check if URL contains 'mpd'
        if 'mpd' in url.lower():
            # MPD file handling - original logic
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
            
            # Return karo as plain text
            return Response(content=content, media_type="application/xml")
        
        else:
            # Video streaming handling
            range_header = response.headers.get("Range", "")
            return streamer.stream_video(url, range_header)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "Video Streamer & MPD Proxy"}

if __name__ == "__main__":
    print("🚀 FastAPI Video Streaming & MPD Proxy starting on port 8000")
    print("📹 Endpoints:")
    print("   GET /proxy?url=VIDEO_URL")
    print("   GET /health")
    uvicorn.run(app, host="0.0.0.0", port=8000)
