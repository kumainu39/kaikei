"""FastAPI route for manual ScanSnap OCR XML upload (multi-tenant)."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, UploadFile, Header, HTTPException

from ..auto_journal_scan import process_scansnap_xml
from ..db_manager import get_client_by_key


router = APIRouter(prefix="/api/scan", tags=["scan"])


@router.post("/import")
async def import_scansnap(file: UploadFile, x_client_key: str = Header(...)):
    tmp_dir = Path("tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    path = tmp_dir / file.filename
    data = await file.read()
    path.write_bytes(data)
    client = get_client_by_key(x_client_key)
    if not client:
        raise HTTPException(status_code=401, detail="Invalid client key")
    result = process_scansnap_xml(path, client_code=client.code)
    return {"status": "ok", "client": client.code, **result}
