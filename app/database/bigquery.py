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

def bq_upsert_fitbit_days(user_id: str, days: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Fitbit日次データをBigQueryに保存（日付パーティションごとに上書き）"""
    if not bq_client or not days:
        return {"ok": False, "reason": "bq disabled or empty"}

    def to_int(x):
        try:
            return int(float(x))
        except Exception:
            return 0

    jobs = []
    for d in days:
        if not d.get("date"):
            continue
        date_str = d["date"]                 # "YYYY-MM-DD"
        part = date_str.replace("-", "")     # "YYYYMMDD"
        table_id = f"{settings.BQ_PROJECT_ID}.{settings.BQ_DATASET}.{settings.BQ_TABLE_FITBIT}${part}"

        row = {
            "user_id": user_id,
            "date": date_str,
            "steps_total": to_int(d.get("steps_total", 0)),
            "sleep_line": d.get("sleep_line", ""),
            "spo2_line": d.get("spo2_line", ""),
            "calories_total": to_int(d.get("calories_total", 0)),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }

        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            schema=[
                bigquery.SchemaField("user_id", "STRING"),
                bigquery.SchemaField("date", "DATE"),
                bigquery.SchemaField("steps_total", "INTEGER"),
                bigquery.SchemaField("sleep_line", "STRING"),
                bigquery.SchemaField("spo2_line", "STRING"),
                bigquery.SchemaField("calories_total", "INTEGER"),
                bigquery.SchemaField("ingested_at", "TIMESTAMP"),
            ],
        )

        job = bq_client.load_table_from_json([row], table_id, job_config=job_config)
        jobs.append(job)

    errors = []
    for j in jobs:
        j.result()
        if j.errors:
            errors.extend(j.errors)

    return {"ok": not bool(errors), "errors": errors, "count": len(jobs)}
