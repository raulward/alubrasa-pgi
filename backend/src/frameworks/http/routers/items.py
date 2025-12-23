
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from src.use_cases.items.dtos import ImportResult
from src.use_cases.items.import_items import ImportItemsUseCase
from src.use_cases.items.list_items import ListItemsUseCase
from src.frameworks.http.dependencies import get_import_items_use_case, get_list_items_use_case
from typing import List, Dict, Any

router = APIRouter(prefix="/items", tags=["Itens"])

@router.post("/import", response_model=ImportResult)
async def import_items(
    id_obra: str = Form(...),
    file: UploadFile = File(...),
    use_case: ImportItemsUseCase = Depends(get_import_items_use_case)
):
    """
    Import items from an Excel file.
    """
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="File must be an Excel file")

    content = await file.read()
    try:
        result = await use_case.execute(id_obra=id_obra, file_bytes=content)
        return result
    except ValueError as e:
         raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
         # Log unhandled
         raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/", response_model=List[Dict[str, Any]])
async def list_items(
    id_obra: str,
    use_case: ListItemsUseCase = Depends(get_list_items_use_case)
):
    """
    List items for a specific obra.
    """
    return await use_case.execute(id_obra=id_obra)
