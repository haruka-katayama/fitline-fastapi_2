from google.cloud import bigquery
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.config import settings

bq_client = bigquery.Client(project=settings.BQ_PROJECT_ID) if settings.BQ_PROJECT_ID else None

def bq_insert_rows(table: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """BigQueryにデータを挿入"""
    if not bq_client:
        return {"ok": False, "reason": "bq disabled"}
    
    table_id = f"{settings.BQ_PROJECT_ID}.{settings.BQ_DATASET}.{table}"
    errors = bq_client.insert_rows_json(table_id, rows, ignore_unknown_values=True)
    return {"ok": not bool(errors), "errors": errors}

def bq_upsert_profile(user_id: str = "demo") -> Dict[str, Any]:
    """プロフィールをBigQueryに保存/更新"""
    from app.database.firestore import get_latest_profile
    
    if not bq_client:
        return {"ok": False, "reason": "bq disabled"}

    prof = get_latest_profile(user_id)
    if not prof:
        return {"ok": False, "reason": "no profile in firestore"}

    past_history = ",".join(prof.get("past_history") or [])
    row = {
        "user_id": user_id,
        "updated_at": prof.get("updated_at") or datetime.now(timezone.utc).isoformat(),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "age": prof.get("age"),
        "sex": prof.get("sex"),
        "height_cm": prof.get("height_cm"),
        "weight_kg": prof.get("weight_kg"),
        "target_weight_kg": prof.get("target_weight_kg"),
        "goal": prof.get("goal"),
        "smoking_status": prof.get("smoking_status"),
        "alcohol_habit": prof.get("alcohol_habit"),
        "past_history": past_history,
        "medications": prof.get("medications"),
        "allergies": prof.get("allergies"),
        "notes": prof.get("notes"),
    }
    return bq_insert_rows(settings.BQ_TABLE_PROFILES, [row])
