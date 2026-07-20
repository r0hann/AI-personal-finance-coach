from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import transactions, insights, chat, budget

app = FastAPI(title="AI Personal Finance Coach", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions.router)
app.include_router(insights.router)
app.include_router(chat.router)
app.include_router(budget.router)


@app.get("/health")
def health():
    return {"status": "ok"}
