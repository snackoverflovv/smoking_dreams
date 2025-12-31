import streamlit as st
from datetime import date, timedelta
import holidays

# ---------- 백엔드 ----------
KR_HOLIDAYS = holidays.KR()

def is_holiday(d, extra_holidays=None):
    if extra_holidays is None:
        extra_holidays = set()
    return d.weekday() >= 5 or d in KR_HOLIDAYS or d in extra_holidays


def calculate_rest_period(leave_start, leave_days, extra_holidays=None):
    if extra_holidays is None:
        extra_holidays = set()
        
    leave_end = leave_start + timedelta(days=leave_days - 1)

    rest_start = leave_start
    while is_holiday(rest_start - timedelta(days=1), extra_holidays):
        rest_start -= timedelta(days=1)

    rest_end = leave_end
    while is_holiday(rest_end + timedelta(days=1), extra_holidays):
        rest_end += timedelta(days=1)

    return {
        "leave_start": leave_start,
        "leave_end": leave_end,
        "rest_start": rest_start,
        "rest_end": rest_end,
        "total_rest_days": (rest_end - rest_start).days + 1
    }


def recommend_best_vacations(search_start, search_end, leave_days, extra_holidays=None):
    if extra_holidays is None:
        extra_holidays = set()

    results = []
    cur = search_start

    while cur + timedelta(days=leave_days - 1) <= search_end:
        results.append(
            calculate_rest_period(cur, leave_days, extra_holidays)
        )
        cur += timedelta(days=1)

    results.sort(key=lambda x: x["total_rest_days"], reverse=True)
    return results[:3]


# ---------- UI ----------
st.set_page_config(page_title="군인 휴가 추천", page_icon="🎖️")
st.title("🎖️ 군인 휴가 추천기")

leave_days = st.selectbox("사용할 휴가 일수", [1, 2, 3, 4, 5, 7, 10])
search_start = st.date_input("탐색 시작일", date.today())
search_end = st.date_input("탐색 종료일", date.today() + timedelta(days=180))

extra_input = st.text_area("부대 전투휴무 (YYYY-MM-DD)", placeholder="2026-02-06")

extra_holidays = set()
for line in extra_input.splitlines():
    try:
        extra_holidays.add(date.fromisoformat(line.strip()))
    except:
        pass

if st.button("🔥 최적 휴가 추천"):
    results = recommend_best_vacations(
        search_start,
        search_end,
        leave_days,
        extra_holidays
    )

    for i, r in enumerate(results, 1):
        st.markdown(f"""
### 🥇 추천 {i}
- ✈️ 휴가 사용: **{r['leave_start']} ~ {r['leave_end']}**
- 🏖️ 실제 휴식: **{r['rest_start']} ~ {r['rest_end']}**
- ⏳ 총 휴식: **{r['total_rest_days']}일**
""")
