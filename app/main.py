import uvicorn
from fastapi import FastAPI
from app.tasks.router import router as router_tasks
from app.users.router import router as router_users


app = FastAPI()

app.include_router(router_tasks)
app.include_router(router_users)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
