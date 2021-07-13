from fastapi import FastAPI, Response, status
from fastapi.responses import PlainTextResponse

from tatsu.exceptions import FailedParse
from requests.exceptions import ConnectionError, MissingSchema, InvalidSchema
from h11._util import RemoteProtocolError

import tools

app = FastAPI()

@app.get("/")
async def root():
    return {
        "title":        "iCal Transparentifier",
        "description":  ["If you (like me) have the pagerduty ics imported into your google calendar, I've made a little quality of life proxy thing that can sit in between google and pagerduty that:",
                        ["* Updates all the events to be marked as 'free' not busy, so it doesn't cause all your events to get all squashed up when the calendar is shown, and just sits in the background",
                        "* allows you to strip events with a certain name out"]],
        "github":       "https://github.com/whi-tw/ical-transparentifier",
        "usage":        ["https://ical-transparentifier.herokuapp.com/cal/${CALENDAR_URL}?strip=in+hours",
                        ["This example will strip any event with 'in hours' in the name out of the calendar"],
                        "The full url would look like:",
                        ["https://ical-transparentifier.herokuapp.com/cal/webcal://some-org.pagerduty.com/private/nz5gdccah69xpps5dsvzrpcgi4bvi5beyufxagusgpjhea1srmolobqb2gf6byxd/feed?strip=in+hours"]]
    }


@app.get("/cal/{cal_uri:path}", status_code=status.HTTP_400_BAD_REQUEST)
async def parse_cal(response: Response, cal_uri: str, strip: str = None):
    try:
        updated_cal, removed_items = tools.futz_with_ical(cal_uri, strip)
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

    return PlainTextResponse(content=updated_cal, media_type="text/calendar", headers={"X-Removed-Event-Count": str(removed_items)})
