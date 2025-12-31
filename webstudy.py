#pip install fastapi uvicorn holidays
#pip install streamlit holidays ipywidgets

from datetime import date, timedelta
import holidays

# 대한민국 공휴일
KR_HOLIDAYS = holidays.KR()


def is_holiday(d: date, extra_holidays: set[date] | None = None) -> bool:
    """
    휴일 여부 판별
    - 토요일 / 일요일
    - 국가 공휴일
    - 부대 전투휴무 (extra_holidays)
    """
    if extra_holidays is None:
        extra_holidays = set()
        
    return (
        d.weekday() >= 5  # 토, 일
        or d in KR_HOLIDAYS
        or d in extra_holidays
    )


def calculate_rest_period(
    leave_start: date,
    leave_days: int,
    extra_holidays: set[date] | None = None
) -> dict:
    """
    휴가 시작일 + 휴가 일수 → 실제 연속 휴식 기간 계산
    """
    if extra_holidays is None:
        extra_holidays = set()
        
    leave_end = leave_start + timedelta(days=leave_days - 1)

    # 앞쪽 확장
    rest_start = leave_start
    while is_holiday(rest_start - timedelta(days=1), extra_holidays):
        rest_start -= timedelta(days=1)

    # 뒤쪽 확장
    rest_end = leave_end
    while is_holiday(rest_end + timedelta(days=1), extra_holidays):
        rest_end += timedelta(days=1)

    return {
        "leave_start": leave_start,
        "leave_end": leave_end,
        "rest_start": rest_start,
        "rest_end": rest_end,
        "leave_days": leave_days,
        "total_rest_days": (rest_end - rest_start).days + 1
    }


def recommend_best_vacations(
    search_start: date,
    search_end: date,
    leave_days: int,
    extra_holidays: set[date] | None = None,
    top_k: int = 3
) -> list[dict]:
    """
    탐색 기간 내에서 가장 효율 좋은 휴가 TOP K 추천
    """
    if extra_holidays is None:
        extra_holidays = set()
        
    results = []
    cur = search_start

    while cur + timedelta(days=leave_days - 1) <= search_end:
        result = calculate_rest_period(
            leave_start=cur,
            leave_days=leave_days,
            extra_holidays=extra_holidays
        )
        results.append(result)
        cur += timedelta(days=1)

    # 실제 휴식 일수 기준 정렬
    results.sort(key=lambda x: x["total_rest_days"], reverse=True)
    return results[:top_k]
