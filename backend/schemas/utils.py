from datetime import date, datetime
from typing import Annotated, Optional
from pydantic import BaseModel, BeforeValidator, Field

# 1. Define a Validator Function
def parse_italian_date(v: any) -> any:
    if isinstance(v, str):
        # Try Italian format
        try:
            return datetime.strptime(v, "%d/%m/%Y").date()
        except ValueError:
            # Fallback to standard ISO if needed
            pass
    return v

# 2. Create the Custom Type using Annotated + BeforeValidator
ItalianDate = Annotated[date, BeforeValidator(parse_italian_date)]