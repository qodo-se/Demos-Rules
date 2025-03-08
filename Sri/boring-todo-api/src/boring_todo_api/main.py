"""
This is the main module of the boring-todo-api project.
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Hello World"}
