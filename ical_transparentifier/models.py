from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field


class CalendarResponse(PlainTextResponse):
    media_type = "text/calendar"
    example = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:ics.py - http://git.io/lLljaA
BEGIN:VEVENT
ATTENDEE;CN=some.person@example.com:mailto:some.person@example.com
DTEND:20220901T080000Z
DTSTART:20220831T160000Z
SUMMARY:On Call - Some rota - out of hours
TRANSP:TRANSPARENT
UID:XXXXXXXXXX
URL:https://some-org.pagerduty.com/schedules#XXXXX
END:VEVENT
...
END:VCALENDAR
    """


class SourceUrl(BaseModel):
    source_url: str
    strip: str | None = None

    class Config:
        schema_extra = {
            "example": {
                "source_url": (
                    "webcal://some-org.pagerduty.com/private/"
                    "nz5gdccah69xpps5dsvzrpcgi4bvi5beyufxagusgpjhea1srmolobqb2gf6byxd/"
                    "feed"
                ),
                "strip": "in hours",
            }
        }


class ErrorResponse(BaseModel):
    error: str = "An error occurred"
    context: SourceUrl

    class Config:
        schema_extra = {
            "example": {
                "error": "An error occurred",
                "context": SourceUrl.Config.schema_extra["example"],
            }
        }


class SourceUrlResponse(SourceUrl):
    url: str
    source_url: str = Field(title="URL encoded representation of `source_url`")
    strip: str = Field(None, title="URL encoded representation of `strip`")

    class Config:
        schema_extra = {
            "example": {
                "url": (
                    "http://serviceurl/cal?source_url=webcal%3A%2F%2Fsome-org."
                    "pagerduty.com%2Fprivate%2Fnz5gdccah69xpps5dsvzrpcgi4bvi5beyufx"
                    "agusgpjhea1srmolobqb2gf6byxd%2Ffeed&strip=in+hours"
                ),
                "source_url": (
                    "webcal%3A%2F%2Fsome-org."
                    "pagerduty.com%2Fprivate%2Fnz5gdccah69xpps5dsvzrpcgi4bvi5beyufx"
                    "agusgpjhea1srmolobqb2gf6byxd%2Ffeed"
                ),
                "strip": "in+hours",
            }
        }
