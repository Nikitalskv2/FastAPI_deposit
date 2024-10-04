from datetime import datetime
from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel, Field, field_validator


app = FastAPI(title="Deposit calculate")


def validate_date(value: str):
    try:
        datetime.strptime(value, '%d.%m.%Y')
        result = True
        return result
    except ValueError as e:
        result = False
        return result


class Deposit(BaseModel):
    date: str = Field(..., example="01.01.2020")
    periods: int = Field(ge=1, le=60)
    amount: int = Field(ge=10000, le=3000000)
    rate: float = Field(ge=1, le=8)

    @field_validator("date")
    def validate_date_range(cls, date):
        if not validate_date(date):
            raise ValueError("Date must be in the format DD.MM.YYYY")
        return date


@app.post("/")

def calculate(deposit: Deposit):

    start_date = datetime.strptime(deposit.date, '%d.%m.%Y')
    dates = pd.date_range(start=start_date, periods=deposit.periods, freq='M')

    amounts = []
    for date in dates:
        percent_amount = deposit.amount * (1 + (deposit.rate/100) / 12) ** (dates.get_loc(date) + 1)
        amounts.append(round(percent_amount, 2))

    result = dict(zip(dates.strftime('%d.%m.%Y'), amounts))
    return result


# uvicorn app.main:app --reload
