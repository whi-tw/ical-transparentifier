from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse

import tools

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/cal/{cal_uri:path}")
async def parse_cal(cal_uri: str, strip: str = None):
    updated_cal = tools.futz_with_ical(cal_uri, strip)

    return PlainTextResponse(content=updated_cal, media_type="text/calendar")
