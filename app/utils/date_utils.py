from datetime import datetime, timezone, timedelta

def to_when_date_str(iso_str: str | None) -> str:
    """ISO8601文字列の先頭10桁(YYYY-MM-DD)を日付キーとして返す"""
    if not iso_str:
        return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
    return iso_str[:10]

def jst_now() -> datetime:
    """JST現在時刻を返す"""
    return datetime.now(timezone.utc) + timedelta(hours=9)

def format_datetime_hp(dt: datetime) -> str:
    """Health Planet API用の日時フォーマット（yyyymmddHHMMSS）"""
    return dt.strftime("%Y%m%d%H%M%S")

def get_date_range(days: int) -> tuple[str, str]:
    """指定日数分の日付範囲を取得"""
    today = datetime.now(timezone.utc).astimezone().date()
    end_date = today.strftime("%Y-%m-%d")
    start_date = (today - timedelta# 完全なファイル構成とコード

## 📁 ディレクトリ構造
