
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import chat  # Importing our existing chat logic

app = FastAPI()

# Setup templates
templates = Jinja2Templates(directory="templates")

class ChatMessage(BaseModel):
    message: str
    mode: str = "chat" # "chat" or "rewrite"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat_endpoint(msg: ChatMessage):
    try:
        if msg.mode == "rewrite":
            response_text = chat.get_rewrite_response(msg.message)
            return {"response": response_text}
        else:
            response_text = chat.get_chat_response(msg.message)
            return {
                "response": response_text,
                "history": chat.chat_memory
            }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
