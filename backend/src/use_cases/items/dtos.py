
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ImportResult(BaseModel):
    total_ok: int
    errors: List[Dict[str, Any]]
    validation_errors: List[Dict[str, Any]]
