from fastapi import FastAPI
from app.tasks.router import router as router_tasks
from app.users.router import router as router_users


app = FastAPI()

app.include_router(router_tasks)
app.include_router(router_users)


@app.get("/")
async def healthcheck():
    return {"status": "ok"}
