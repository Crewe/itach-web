from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="iTachWeb API", root_path="/api/v1")

# app.include_router(ip2cc_api_router)

app.mount("/static", StaticFiles(directory="itachweb/static"), name="static")
