import datetime as dt

from pydantic import BaseModel, ConfigDict, Field


class CertificateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=100, examples=["pasupula supriya"])
    course: str = Field(..., min_length=1, max_length=150, examples=["Python Programming"])
    date: dt.date = Field(..., examples=["2026-10-10"])