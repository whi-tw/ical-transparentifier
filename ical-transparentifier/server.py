from fastapi import FastAPI, Response, status
from fastapi.responses import PlainTextResponse

from tatsu.exceptions import FailedParse
from requests.exceptions import ConnectionError, MissingSchema, InvalidSchema
from h11._util import RemoteProtocolError

import tools

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/cal/{cal_uri:path}", status_code=status.HTTP_400_BAD_REQUEST)
async def parse_cal(cal_uri: str, response: Response, strip: str = None):
    try:
        updated_cal = tools.futz_with_ical(cal_uri, strip)
    except FailedParse as e:
        return {"error": "Could not parse ical structure", "url": cal_uri}
    except ConnectionError:
        return {"error": "Could not connect to domain", "url": cal_uri}
    except MissingSchema as e:
        return {"error": str(e), "url": cal_uri}
    except InvalidSchema:
        return {"error": "provided url is bad.", "url": cal_uri}, 400
    except RemoteProtocolError:
        return {"error": "ensure all spaces in url are replaced with '+'", "url": cal_uri}

    response.status_code = status.HTTP_200_OK
    return PlainTextResponse(content=updated_cal, media_type="text/calendar")
