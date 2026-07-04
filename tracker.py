import streamlit as st
# maps every job code to its exact allowed min value (AMV)
JOB_DATABASE = {
    "handbags": {"name": "Handbags", "amv": 0.4628},
    "1man_soft": {"name": "1 Person Soft Furnishings", "amv": 0.6243},
    "2man_soft": {"name": "2 Person Soft Furnishings", "amv": 1.8581},
    "boxed_shoes": {"name": "Recondition Boxed Footwear (Shoes)", "amv": 0.8983},
    "bagged_pumps": {"name": "Recondition Bagged Footwear ('pumps')", "amv": 0.7020},
    "fold_scan_belt": {"name": "Fold & Scan Accessories to Belt", "amv": 0.3580},
    "fold_scan_manual": {"name": "Fold, Scan & Manual Bag Accessories", "amv": 0.4864},
    "process_jewellery": {"name": "Processing Jewellery", "amv": 0.8171},
    "process_cosmetics": {"name": "Processing Cosmetics", "amv": 0.6058},
} 
def calculate_complex_shift(completed_blocks, current_next_job, mins_remaining):
    total_earned_minutes = 0.0
    total_time_worked = 0
    
    st.write("==================================================")
    st.write("            SHIFT PROGRESS BREAKDOWN              ")
    st.write("==================================================")
    
    for block in completed_blocks:
        job_id = block["job_id"]
        items = block["items_done"]
        mins = block["mins_worked"]
        
        job_name = JOB_DATABASE[job_id]["name"]
        amv = JOB_DATABASE[job_id]["amv"]
        
        block_earned_mins = items * amv
        block_score = (block_earned_mins / mins) * 10
        
        total_earned_minutes += block_earned_mins
        total_time_worked += mins
        
        st.write(f"• {job_name}: Worked {mins} mins, did {items} items. Block Score: {round(block_score, 1)}/10")

    live_rolling_score = (total_earned_minutes / total_time_worked) * 10
    st.write("--------------------------------------------------")
    st.write(f"TOTAL TIME WORKED SO FAR: {total_time_worked} minutes")
    st.write(f"CURRENT ROLLING SCORE:    {round(live_rolling_score, 1)} / 10")
    st.write("--------------------------------------------------")
    
    total_shift_time = total_time_worked + mins_remaining
    total_earned_mins_needed_for_day = (6.0 * total_shift_time) / 10
    deficit_to_clear = total_earned_mins_needed_for_day - total_earned_minutes
    
    next_job_name = JOB_DATABASE[current_next_job]["name"]
    next_job_amv = JOB_DATABASE[current_next_job]["amv"]
    
    if deficit_to_clear <= 0:
        st.write(f"STATUS: You are already safely past 6/10 for the day! Cruise control active on {next_job_name}.")
    else:
        items_needed_next = int(deficit_to_clear / next_job_amv) + 1
        st.write(f"TARGET FOR NEXT JOB ({next_job_name}):")
        st.write(f"You have {mins_remaining} minutes remaining on this shift.")
        st.write(f"To finish the day safe at 6/10, you MUST do: {items_needed_next} items.")
    st.write("==================================================")


# ========================================================
# EXECUTION LAYER (Multi-Job Tracking Mode)
# ========================================================

st.title("🏃‍♂️ Warehouse Bonus Tracker")

# Setup a clean list to store whatever jobs you did
my_completed_blocks = []
job_choices = list(JOB_DATABASE.keys())

st.markdown("## 📥 Log Your Completed Work")

# --- JOB BLOCK 1 ---
st.markdown("### 🔹 Job 1")
job1_id = st.selectbox("What was your 1st job?", job_choices, key="j1")
block1_items = st.number_input("Items done on 1st job:", min_value=0, value=0, key="i1")
block1_minutes = st.number_input("Minutes worked on 1st job:", min_value=0, value=0, key="m1")

if block1_minutes > 0:
    my_completed_blocks.append({"job_id": job1_id, "items_done": block1_items, "mins_worked": block1_minutes})

# --- JOB BLOCK 2 ---
st.markdown("### 🔹 Job 2 (Optional)")
job2_id = st.selectbox("What was your 2nd job?", job_choices, key="j2")
block2_items = st.number_input("Items done on 2nd job:", min_value=0, value=0, key="i2")
block2_minutes = st.number_input("Minutes worked on 2nd job:", min_value=0, value=0, key="m2")

if block2_minutes > 0:
    my_completed_blocks.append({"job_id": job2_id, "items_done": block2_items, "mins_worked": block2_minutes})

# --- JOB BLOCK 3 ---
st.markdown("### 🔹 Job 3 (Optional)")
job3_id = st.selectbox("What was your 3rd job?", job_choices, key="j3")
block3_items = st.number_input("Items done on 3rd job:", min_value=0, value=0, key="i3")
block3_minutes = st.number_input("Minutes worked on 3rd job:", min_value=0, value=0, key="m3")

if block3_minutes > 0:
    my_completed_blocks.append({"job_id": job3_id, "items_done": block3_items, "mins_worked": block3_minutes})


# --- NEXT JOB SELECTION ---
st.markdown("---")
st.markdown("## 🔮 Next Job Target")
current_job_right_now = st.selectbox("Select the job you are moving to next:", job_choices, key="next_job")


# --- AUTOMATIC TIME CALCULATION WITH BREAKS ---
st.markdown("### 🕒 Shift End Time")
shift_end_hour = st.selectbox("What hour does your shift finish? (24h format):", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], index=17) # Defaults to 18 (6 PM)

break_taken = st.checkbox("Have you already taken your 30-minute break?", value=False)

import datetime
now = datetime.datetime.now()
finish_time = now.replace(hour=shift_end_hour, minute=0, second=0, microsecond=0)

total_minutes_until_clockout = max(0, int((finish_time - now).total_seconds() / 60))

if not break_taken:
    minutes_left_in_shift = max(0, total_minutes_until_clockout - 30)
else:
    minutes_left_in_shift = total_minutes_until_clockout

st.info(f"⏱️ **{minutes_left_in_shift} working minutes** remaining in your shift (excluding break time).")


# --- RUN MATH ENGINE ---
# Only calculate results if at least the first job has minutes tracked
if len(my_completed_blocks) > 0:
    st.markdown("---")
    st.markdown("## 📊 Your Live Shift Results")
    calculate_complex_shift(my_completed_blocks, current_job_right_now, minutes_left_in_shift)