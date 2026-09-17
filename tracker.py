import streamlit as st
from datetime import datetime, timedelta
import streamlit as st
from datetime import datetime, timedelta
import json
import os

DB_FILE = "warehouse_db.json"

def load_secure_database():
    default_db = {
        23: {
            "Sunday": {"date": "05/07/2026", "score": 6.32, "stages": []},
            "Monday": {"date": "06/07/2026", "score": 6.45, "stages": []},
            "Tuesday": {"date": "07/07/2026", "score": 6.13, "stages": []}
        }
    }
    if not os.path.exists(DB_FILE):
        return default_db
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            return {int(k): v for k, v in data.items()}
    except:
        return default_db

def save_secure_database(db_data):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(db_data, f, indent=4)
        return True
    except:
        return False

st.set_page_config(page_title="Next Elmsall Automated Ledger", layout="wide")
st.title("📦 Next Elmsall - Annual Performance Ledger")


# -----------------------------------------------------------------
# 1. AMV DATABASE INDEX
# -----------------------------------------------------------------
ALL_JOBS = {
    "Soft Furnishings (1 Man)": 0.6243,
    "Handbags": 0.4628,
    "Soft Furnishings (2 Man)": 1.8581,
    "Recondition Boxed Footwear": 0.8983,
    "Recon Bagged Footwear": 0.7020,
    "Fold & Scan Accessories (Belt)": 0.3580,
    "Fold, Scan & Manual Bag Accessories": 0.4864,
    "Processing Jewellery": 0.8171,
    "Processing Cosmetics": 0.6058,
    "Crediting (Scan Item)": 0.2229,
    "Item Scan - Store": 0.1429,
    "Item Scan - Courier": 0.2162,
    "Fit (Level 4 Inspection)": 0.4664,
    "Fold & Bag Manual Top Up": 0.2764,
    "Perfect (Level 4)": 0.1833,
    "Faulty (Level 4)": 0.5906,
    "Spot Clean (Level 4)": 0.5111,
    "Wrong Destination (Level 4)": 0.2412,
    "Fraudulent (Level 4)": 0.7888,
    "Open & Fold Fashion to Belt": 0.3725,
    "Open, Fold & Manual Bag Fashion": 0.5175,
    "Open, Fold & Manual Bag Unsorted": 0.5923
}

HOURS = [f"{i:02d}" for i in range(24)]
MINUTES = [f"{i:02d}" for i in range(60)]
DAYS_OF_WEEK = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# -----------------------------------------------------------------
# 2. AUTOMATIC RETAIL CALENDAR ENGINE
# -----------------------------------------------------------------
def get_dates_for_retail_week(week_num, year=2026):
    year_start = datetime(year, 2, 1)
    week_start_date = year_start + timedelta(weeks=(week_num - 1))
    start_offset = (week_start_date.weekday() + 1) % 7
    week_sunday = week_start_date - timedelta(days=start_offset)
    
    week_map = {}
    for idx, day_name in enumerate(DAYS_OF_WEEK):
        day_date = week_sunday + timedelta(days=idx)
        week_map[day_name] = day_date.strftime("%d/%m/%Y")
    return week_map

if "annual_database" not in st.session_state:
    st.session_state.annual_database = load_secure_database()
    

if "live_stages" not in st.session_state:
    st.session_state.live_stages = [{"role": "Soft Furnishings (1 Man)", "sh": "06", "sm": "00", "eh": "18", "em": "00", "vol": 0}]
# -----------------------------------------------------------------
# -----------------------------------------------------------------
# 3. WORKSPACE WEEK CONTROLLER & TABS SPLIT
# -----------------------------------------------------------------
# Set up the split layout tab views first
tab1, tab2 = st.tabs(["📝 Live Work Tracker", "🗄️ Saved & Logged Weeks Archive"])

# Calculate a fallback dynamic week for default indexing
today_date = datetime.now()
retail_year_start = datetime(today_date.year, 2, 1)
if today_date < retail_year_start:
    retail_year_start = datetime(today_date.year - 1, 2, 1)
days_elapsed = (today_date - retail_year_start).days
auto_week = max(1, min(53, (days_elapsed // 7) + 1))

# -----------------------------------------------------------------
# TAB 1: LIVE WORK TRACKER WORKSPACE
# -----------------------------------------------------------------
with tab1:
    # Clean manual dropdown directly at the top of your workspace page
    live_current_week = st.selectbox(
        "🗂️ Select Workspace Target Week", 
        list(range(1, 54)), 
        index=auto_week - 1
    )
    
    st.subheader(f"🗓️ Current Active Shift Workspace — Week {live_current_week}")
    col_top1, col_top2, col_top3 = st.columns(3)

    with col_top1:
        log_day = st.selectbox("Active Shift Day", DAYS_OF_WEEK, index=0)
        computed_dates = get_dates_for_retail_week(live_current_week)
        log_date_str = computed_dates[log_day]
        st.markdown(f"🗓️ Shift Date: **{log_date_str}**")

    with col_top2:
        st.markdown("**Shift Start Window**")
        c_s1, c_s2 = st.columns(2)
        with c_s1:
            m_sh = st.selectbox("Hour", HOURS, index=6, key="m_sh")
        with c_s2:
            m_sm = st.selectbox("Min", MINUTES, index=0, key="m_sm")

    with col_top3:
        st.markdown("**Shift End Window**")
        c_e1, c_e2 = st.columns(2)
        with c_e1:
            m_eh = st.selectbox("Hour", HOURS, index=18, key="m_eh")
        with c_e2:
            m_em = st.selectbox("Min", MINUTES, index=0, key="m_em")

    deduct_break = st.checkbox("Deduct standard 30-minute unpaid break from performance?", value=True)

    day_start_mins = int(m_sh) * 60 + int(m_sm)
    day_end_mins = int(m_eh) * 60 + int(m_em)
    total_shift_mins = day_end_mins - day_start_mins
    paid_shift_mins = float(total_shift_mins - 30) if deduct_break else float(total_shift_mins)

    st.write("---")
    st.header(f"📋 Shift Timeline Log: {log_day} ({log_date_str})")

    total_earned_minutes = 0.0
    total_tracked_work_mins = 0

    for idx, stage in enumerate(st.session_state.live_stages):
        st.markdown(f"### **Job Stage #{idx + 1}**")
        j1, j2, j3, j4 = st.columns([2.5, 2, 2, 1.5])
        
        with j1:
            default_job_idx = list(ALL_JOBS.keys()).index("Soft Furnishings (1 Man)") if idx == 0 else list(ALL_JOBS.keys()).index("Handbags")
            current_job = stage["role"] if stage["role"] in ALL_JOBS else list(ALL_JOBS.keys())[default_job_idx]
            st.session_state.live_stages[idx]["role"] = st.selectbox(
                "Job Role", list(ALL_JOBS.keys()), index=list(ALL_JOBS.keys()).index(current_job), key=f"jr_{idx}"
            )
        with j2:
            st.markdown("⏱ *Started At*")
            st_h, st_m = st.columns(2)
            with st_h:
                st.session_state.live_stages[idx]["sh"] = st.selectbox("Hour", HOURS, index=HOURS.index(stage["sh"]), key=f"jsh_{idx}")
            with st_m:
                st.session_state.live_stages[idx]["sm"] = st.selectbox("Min", MINUTES, index=MINUTES.index(stage["sm"]), key=f"jsm_{idx}")
        with j3:
            st.markdown("⏱ *Stopped At*")
            en_h, en_m = st.columns(2)
            with en_h:
                st.session_state.live_stages[idx]["eh"] = st.selectbox("Hour", HOURS, index=HOURS.index(stage["eh"]), key=f"jeh_{idx}")
            with en_m:
                st.session_state.live_stages[idx]["em"] = st.selectbox("Min", MINUTES, index=MINUTES.index(stage["em"]), key=f"jem_{idx}")
        with j4:
            st.session_state.live_stages[idx]["vol"] = st.number_input("Scanned Volume", min_value=0, value=stage["vol"], step=1, key=f"jv_{idx}")

        t_start = int(st.session_state.live_stages[idx]["sh"]) * 60 + int(st.session_state.live_stages[idx]["sm"])
        t_end = int(st.session_state.live_stages[idx]["eh"]) * 60 + int(st.session_state.live_stages[idx]["em"])
        job_duration = t_end - t_start
        
        # Deduct break directly inside single stage logic if it's a single full-day block
        if deduct_break and len(st.session_state.live_stages) == 1:
            effective_duration = float(job_duration - 30)
        else:
            effective_duration = float(job_duration)

        job_amv = ALL_JOBS[st.session_state.live_stages[idx]["role"]]
        earned_mins = st.session_state.live_stages[idx]["vol"] * job_amv
        
        if effective_duration > 0:
            stage_score = (earned_mins / effective_duration) * 10
            st.success(f"📊 Stage Performance Index: **{stage_score:.2f} / 10**")
            total_earned_minutes += earned_mins
            total_tracked_work_mins += job_duration

    b_c1, b_c2 = st.columns(2)
    with b_c1:
        if st.button("➕ Move to Another Job (Add Stage)"):
            last_h = st.session_state.live_stages[-1]["eh"]
            last_m = st.session_state.live_stages[-1]["em"]
            st.session_state.live_stages.append({"role": "Handbags", "sh": last_h, "sm": last_m, "eh": m_eh, "em": m_em, "vol": 0})
            st.rerun()
    with b_c2:
        if len(st.session_state.live_stages) > 1:
            if st.button("❌ Remove Last Stage"):
                st.session_state.live_stages.pop()
                st.rerun()

    st.write("---")
    st.header("📊 Live Shift Targets Calculator")
    day_score = (total_earned_minutes / paid_shift_mins) * 10 if paid_shift_mins > 0 else 0.0

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.metric(label=f"Combined Day Performance Index ({log_day})", value=f"{day_score:.2f} / 10")
    with d_col2:
        if st.button(f"💾 Lock & Save Entry to Week {live_current_week}"):
            if live_current_week not in st.session_state.annual_database:
                st.session_state.annual_database[live_current_week] = {}
            st.session_state.annual_database[live_current_week][log_day] = {
                "date": log_date_str,
                "score": round(day_score, 2),
                "stages": list(st.session_state.live_stages),
            }
            save_secure_database(st.session_state.annual_database)
            st.success(f"Successfully locked data into Saved Archive Section for Week {live_current_week}!")

    # Live Target Forecaster Table
    if len(st.session_state.live_stages) > 0:
        active_stage = st.session_state.live_stages[-1]
        active_role_name = active_stage["role"]
        active_amv = ALL_JOBS[active_role_name]

        st.subheader(f"🔮 Target Strategy Plan on {active_role_name} to hit your goal:")
        previous_earned_mins = 0.0
        for prev_idx in range(len(st.session_state.live_stages) - 1):
            prev_stage = st.session_state.live_stages[prev_idx]
            previous_earned_mins += prev_stage["vol"] * ALL_JOBS[prev_stage["role"]]
            
        predictions = []
        for tier in [6.0, 7.0, 8.0, 9.0, 10.0]:
            total_needed_for_day = (tier / 10.0) * paid_shift_mins
            needed_in_current_job = total_needed_for_day - previous_earned_mins
            
            if needed_in_current_job <= 0:
                strategy = "🏆 Goal Already Met by Previous Work!"
            else:
                items_needed = int(needed_in_current_job / active_amv) + 1
                act_start = int(active_stage["sh"]) * 60 + int(active_stage["sm"])
                act_end = int(active_stage["eh"]) * 60 + int(active_stage["em"])
                active_block_mins = max(1, act_end - act_start)
                
                hourly_pace = (items_needed / active_block_mins) * 60
                strategy = f"Process **{items_needed}** total items (Maintain speed: **{hourly_pace:.1f} / hour**)"
                
            predictions.append({"Target Performance Metric": f"{tier} / 10", "Required Strategy Action Plan": strategy})
        st.table(predictions)

# -----------------------------------------------------------------
# TAB 2: LIVE HISTORICAL LEDGER ARCHIVE
# -----------------------------------------------------------------
with tab2:
    st.header("🗄️ Historical Performance Records Vault")
    st.markdown("All completed weeks stored in the database registry are listed below automatically.")

    saved_weeks = sorted([wk for wk in st.session_state.annual_database.keys() if st.session_state.annual_database[wk]])

    if saved_weeks:
        for wk in saved_weeks:
            week_days_data = st.session_state.annual_database[wk]
            scores_list = [d["score"] for d in week_days_data.values()]
            week_avg = sum(scores_list) / len(scores_list) if scores_list else 0.0
            
            with st.container(border=True):
                st.markdown(f"### 📅 **Week {wk} Performance Dashboard** (Running Avg: `{week_avg:.2f} / 10`)")
                wl_cols = st.columns(7)
                for idx, day_name in enumerate(DAYS_OF_WEEK):
                    if day_name in week_days_data:
                        day_data = week_days_data[day_name]
                        wl_cols[idx].metric(label=f"{day_name}", value=f"{day_data['score']} / 10", help=f"Date: {day_data['date']}")
                    else:
                        wl_cols[idx].caption(f"**{day_name}**\n\n*No Entry*")
    else:
        st.info("No saved history records found yet.")
