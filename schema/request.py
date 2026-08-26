from pydantic import BaseModel

from typing import Optional


class RequestSchema(BaseModel):
    amount: int 
    res_num: Optional[str] = None
    cell_number: Optional[str] = None