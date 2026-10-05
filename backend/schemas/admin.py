from typing import List

from pydantic import BaseModel


class EmailRequest(BaseModel):
    client_level_id: str
    client_level: str
    ramo_id: str
    anno: int
    selected_ids: List[str]
