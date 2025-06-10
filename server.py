"""Minimal FastAPI server exposing a /extract endpoint that streams JSON tokens.

Run with:
    uvicorn server:app --reload --port 8000
"""
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse

from extract import Extractor

app = FastAPI(title="Bid Extractor API", version="0.1.0")


@app.post("/extract", response_class=StreamingResponse)
async def extract_endpoint(text: str = Body(..., media_type="text/plain")):
    """Stream extracted JSON tokens from raw text.

    Post plain text in the request body; receive a streaming response where raw
    JSON arrives incrementally. When parsing is complete, the server sends a
    sentinel line "##JSON-END##".
    """

    extractor = Extractor()

    def generate():
        for chunk in extractor.extract_stream(text):
            if isinstance(chunk, str):
                yield chunk
            else:
                # Final object emitted – mark end of stream
                yield "\n\n##JSON-END##\n\n"

    return StreamingResponse(generate(), media_type="text/plain") 