from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="iTachWeb API", root_path="/api/v1")
app.mount("/static", StaticFiles(directory="itachweb/static"), name="static")
