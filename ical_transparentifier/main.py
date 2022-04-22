from urllib.parse import quote_plus, unquote_plus, urlencode, urljoin

from fastapi import FastAPI, HTTPException, Request, Response
from h11._util import RemoteProtocolError
from requests.exceptions import ConnectionError, InvalidSchema, MissingSchema
from tatsu.exceptions import FailedParse

from . import tools
from ._version import VERSION
from .models import CalendarResponse, ErrorResponse, SourceUrl, SourceUrlResponse

description = """
If you (like me) have the pagerduty ics imported into your google calendar, this tool could be your savior!

It's a little quality of life proxy thing that can sit in between google and pagerduty that:
* Updates all the events to be marked as 'free' not busy, so it doesn't cause all your events to get all squashed up when the calendar is shown, and just sits in the background
* Allows you to strip events with a certain name out

## Usage
> https://ical-transparentifier.herokuapp.com/cal/?source_url=${URLENCODED_CALENDAR_URL}&strip=in+hours

This example will strip any event with 'in hours' in the name out of the calendar

The full URL would look like: `https://ical-transparentifier.herokuapp.com/cal?source_url=http://serviceurl/cal?source_url=webcal%3A%2F%2Fsome-org.pagerduty.com%2Fprivate%2Fnz5gdccah69xpps5dsvzrpcgi4bvi5beyufxagusgpjhea1srmolobqb2gf6byxd%2Ffeed&strip=in+hours`
"""
app = FastAPI(
    title="iCal Transparentifier",
    description=description,
    version=VERSION,
    contact={
        "name": "Tom Whitwell",
        "url": "https://whi.tw/ell",
        "email": "ical-transparentifier@mail.whi.tw",
    },
    docs_url=None,
    redoc_url="/",
)


@app.post(
    "/get_url",
    response_model=SourceUrlResponse,
    name="Get formatted URL",
    description="Get a URL that can be used with this service",
)
async def get_url(source: SourceUrl, request: Request):
    params = urlencode(source.dict())
    url = urljoin(str(request.base_url), "/cal?" + params)
    return {
        "url": url,
        "source_url": quote_plus(source.source_url),
        "strip": quote_plus(source.strip) if source.strip else None,
    }


@app.get(
    "/cal",
    name="Parse calendar from Query String",
    description=(
        "Process a calendar, passing the URL in the query string."
        "The correct query parameters can be generated at /get_url"
    ),
    response_class=CalendarResponse,
    responses={
        200: {
            "content": {
                CalendarResponse.media_type: {"example": CalendarResponse.example}
            },
            "description": "The modified calendar",
        },
        400: {
            "description": "The input caused some kind of error.",
            "content": {"application/json": {}},
        },
        500: {
            "description": "Internal server error",
            "content": {"application/json": {}},
        },
        502: {
            "description": "Unable to access the provided URL",
            "content": {"application/json": {}},
        },
    },
)
async def parse_cal_qs(source_url: str, strip: str | None = None):
    try:
        updated_cal, removed_items = await tools.futz_with_ical(
            unquote_plus(source_url), unquote_plus(strip) if strip else None
        )
    except FailedParse:
        raise HTTPException(400, "Could not parse ical structure")
    except InvalidSchema:
        raise HTTPException(400, "Provided URL is incorrect")
    except RemoteProtocolError:
        raise HTTPException(
            400,
            (
                "Provided URL is incorrect. Ensure all spaces in url are "
                "replaced with '+'"
            ),
        )
    except ConnectionError:
        raise HTTPException(502, "Could not retrieve calendar from URL")
    except MissingSchema as e:
        raise HTTPException(500, str(e))

    return CalendarResponse(
        content=updated_cal,
        headers={"X-Removed-Event-Count": str(removed_items)},
    )


@app.get(
    "/cal/{cal_uri:path}",
    deprecated=True,
    description=(
        "Process a calendar, passing the URL as path parameter."
        "This is a bit unstable because of special characters, so "
        "should no longer be used."
    ),
    name="Parse calendar from URL path Parameter",
    response_class=CalendarResponse,
    responses={
        200: {
            "content": {
                CalendarResponse.media_type: {"example": CalendarResponse.example}
            },
            "description": "The modified calendar",
        },
        400: {
            "description": "The input caused some kind of error.",
            "content": {"application/json": {}},
        },
        500: {
            "description": "Internal server error",
            "content": {"application/json": {}},
        },
        502: {
            "description": "Unable to access the provided URL",
            "content": {"application/json": {}},
        },
    },
)
async def parse_cal(response: Response, source_url: str, strip: str = None):
    try:
        updated_cal, removed_items = await tools.futz_with_ical(source_url, strip)
    except FailedParse:
        raise HTTPException(400, "Could not parse ical structure")
    except InvalidSchema:
        raise HTTPException(400, "Provided URL is incorrect")
    except RemoteProtocolError:
        raise HTTPException(
            400,
            (
                "Provided URL is incorrect. Ensure all spaces in url are "
                "replaced with '+'"
            ),
        )
    except ConnectionError:
        raise HTTPException(502, "Could not retrieve calendar from URL")
    except MissingSchema as e:
        raise HTTPException(500, str(e))

    return CalendarResponse(
        content=updated_cal,
        headers={"X-Removed-Event-Count": str(removed_items)},
    )
