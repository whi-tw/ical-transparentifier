from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse

from tatsu.exceptions import FailedParse
from requests.exceptions import ConnectionError

import tools

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/cal/{cal_uri:path}")
async def parse_cal(cal_uri: str, strip: str = None):
    try:
        updated_cal = tools.futz_with_ical(cal_uri, strip)
    except FailedParse:
        return {"error": "Could not parse ical structure", "url": cal_uri}
    except ConnectionError as e:
        print(str(e))
        return {"error": "Could not connect to domain", "url": cal_uri}

    return PlainTextResponse(content=updated_cal, media_type="text/calendar")
