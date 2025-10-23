import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agent_config import create_legal_agent
from collections import defaultdict
from datetime import datetime

app = FastAPI()
agent = create_legal_agent()

user_activity = defaultdict(list)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def log_request(ip, question):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 {ip} asked: {question}")

def check_rate_limit(ip, limit=5, window=60):
    now = time.time()
    user_activity[ip] = [t for t in user_activity[ip] if now - t < window]
    if len(user_activity[ip]) >= limit:
        raise HTTPException(status_code=429, detail="⏳ Too many requests. Try later.")
    user_activity[ip].append(now)

@app.post("/ask")
async def ask_question(request: Request):
    data = await request.json()
    query = data.get("question")
    ip = request.client.host
    if not query:
        raise HTTPException(status_code=400, detail="Missing 'question' field")
    check_rate_limit(ip)
    log_request(ip, query)

    try:
        response = agent.run(query)
        output = getattr(response, "output_text", str(response))
    except Exception as e:
        output = f"⚠️ Error: {e}"

    return {
        "user": ip,
        "question": query,
        "answer": output, 
        "timestamp": datetime.now().isoformat(),
        "requests_last_minute": len(user_activity[ip]),
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Legal Agent API at http://127.0.0.1:8000 ...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
