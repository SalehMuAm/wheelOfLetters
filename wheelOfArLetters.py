import streamlit as st
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
import math

# ---- Page Config ----
st.set_page_config(page_title="لعبة الحروف العربية", layout="wide")

# ---- Constants ----
ARABIC_LETTERS = [
    'ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ',
    'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص',
    'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق',
    'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي'
]

STATES = ["default", "green", "red", "dim"]

# ---- RTL Layout ----
st.markdown("""
    <style>
    body, .main, .block-container, .stApp {
        direction: rtl !important;
        text-align: right !important;
    }
    .stSlider, .stButton, .stTextInput, .stNumberInput, .stSelectbox, .stMarkdown, .stTitle, .stHeader, .stExpander {
        direction: rtl !important;
        text-align: right !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Session Initialization ----
if "players" not in st.session_state:
    st.session_state.players = {}

# Always auto-refresh every second for smooth interactivity
st_autorefresh(interval=1000, key="auto_refresh")

# Reset game
if st.button("🔄 إعادة تعيين اللعبة"):
    st.session_state.players = {}

# Select number of players
num_players = st.selectbox("Number of Players", options=[1, 2, 3, 4], index=1)

# Initialize player data
for i in range(1, num_players + 1):
    key = f"player_{i}"
    if key not in st.session_state.players:
        st.session_state.players[key] = {
            "score": 0,
            "letters": {letter: "default" for letter in ARABIC_LETTERS},
            "timer_length": 1,    # in minutes
            "timer_running": False,
            "timer_end": None,
            "time_remaining": None,  # in seconds
            "selected_letter_idx": 0,  # index of currently selected letter
            "name": f"لاعب {i}"
        }
    if "selected_letter_idx" not in st.session_state.players[key]:
        st.session_state.players[key]["selected_letter_idx"] = 0
    if "name" not in st.session_state.players[key]:
        st.session_state.players[key]["name"] = f"لاعب {i}"

# ---- Helper Functions ----
def next_state(current):
    idx = STATES.index(current)
    return STATES[(idx + 1) % len(STATES)]

def format_time(secs):
    m = secs // 60
    s = secs % 60
    return f"{m:02d}:{s:02d}"

def render_player_wheel(player_key, player_data, player_num):
    # Player name input
    player_data["name"] = st.text_input("اسم اللاعب", value=player_data["name"], key=f"{player_key}_name")

    # Score Controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("➖", key=f"{player_key}_minus"):
            player_data["score"] -= 1
    with col2:
        st.markdown(f"### النقاط: {player_data['score']}")
    with col3:
        if st.button("➕", key=f"{player_key}_plus"):
            player_data["score"] += 1

    st.divider()

    # Timer Controls
    timer_col1, timer_col2, timer_col3 = st.columns([2, 1, 1])
    with timer_col1:
        timer_length = st.selectbox(
            "المؤقت (بالدقائق)",
            options=[1, 2, 3, 4, 5],
            index=player_data["timer_length"] - 1,
            key=f"{player_key}_timer_length",
            help="ضبط مدة المؤقت بالدقائق"
        )
        player_data["timer_length"] = timer_length

    with timer_col2:
        if player_data["timer_running"]:
            if st.button("⏸️ إيقاف المؤقت", key=f"{player_key}_timer_stop"):
                if player_data["timer_end"]:
                    remaining = (player_data["timer_end"] - datetime.now()).total_seconds()
                    player_data["time_remaining"] = max(0, int(remaining))
                player_data["timer_running"] = False
                player_data["timer_end"] = None
        else:
            if st.button("▶️ بدء المؤقت", key=f"{player_key}_timer_start"):
                player_data["timer_running"] = True
                if player_data["time_remaining"] is not None:
                    player_data["timer_end"] = datetime.now() + timedelta(seconds=player_data["time_remaining"])
                else:
                    player_data["timer_end"] = datetime.now() + timedelta(minutes=player_data["timer_length"])
                player_data["time_remaining"] = None

    with timer_col3:
        if player_data["timer_running"] and player_data["timer_end"]:
            remaining = (player_data["timer_end"] - datetime.now()).total_seconds()
            if remaining <= 0:
                player_data["timer_running"] = False
                player_data["timer_end"] = None
                player_data["time_remaining"] = None
                st.markdown("⏰ انتهى الوقت!")
            else:
                st.markdown(f"⏳ {format_time(int(remaining))}")
        elif player_data["time_remaining"] is not None:
            st.markdown(f"⏸️ موقوف: {format_time(player_data['time_remaining'])}")
        else:
            st.markdown("⏸️ المؤقت متوقف")

    st.divider()

    # === Visual-Only Circular Wheel of Letters (with selected letter highlighted and background color) ===
    def get_bg_color(state):
        if state == "green":
            return "#81c784"  # أخضر فاتح
        elif state == "red":
            return "#e57373"  # أحمر فاتح
        elif state == "dim":
            return "#FFFF00"  # أصفر
        else:
            return "#fff"  # أبيض افتراضي

    def render_visual_wheel(player_data):
        # Larger wheel: 60vw, max 400px
        container_size = "min(60vw, 400px)"
        radius_percent = 50  # percent of container
        n = len(ARABIC_LETTERS)
        selected_idx = player_data["selected_letter_idx"]
        wheel_html = f'<div style="position:relative;width:{container_size};height:{container_size};margin:auto;margin-bottom:48px;">'
        for idx, letter in enumerate(ARABIC_LETTERS):
            angle = 2 * math.pi * idx / n - math.pi/2
            x = 50 + radius_percent * math.cos(angle)
            y = 50 + radius_percent * math.sin(angle)
            current_state = player_data["letters"][letter]
            bg_color = get_bg_color(current_state)
            if idx == selected_idx:
                size = 28
                wheel_html += (
                    f'<div style="position:absolute;'
                    f'left:calc({x}% - {size//2}px);top:calc({y}% - {size//2}px);'
                    f'width:{size}px;height:{size}px;display:flex;align-items:center;justify-content:center;'
                    f'font-size:18px;border-radius:50%;border:2px solid #1976d2;background:{bg_color};'
                    f'font-weight:bold;box-shadow:0 0 4px #1976d2;padding:2px;">{letter}</div>'
                )
            else:
                size = 20
                wheel_html += (
                    f'<div style="position:absolute;'
                    f'left:calc({x}% - {size//2}px);top:calc({y}% - {size//2}px);'
                    f'width:{size}px;height:{size}px;display:flex;align-items:center;justify-content:center;'
                    f'font-size:13px;border-radius:50%;border:1px solid #888;background:{bg_color};'
                    f'padding:1px;">{letter}</div>'
                )
        wheel_html += '</div>'
        st.markdown(wheel_html, unsafe_allow_html=True)

    render_visual_wheel(player_data)

    st.markdown("<div style='margin-bottom:32px;'></div>", unsafe_allow_html=True)
    st.markdown("#### لوحة التحكم بالحرف")
    action_key = f"{player_key}_last_action"
    if action_key not in st.session_state:
        st.session_state[action_key] = None
    col_prev, col_letter, col_next, col_change = st.columns([1,2,1,1])
    with col_prev:
        if st.button("⬅️ السابق", key=f"{player_key}_prev"):
            st.session_state[action_key] = "prev"
    with col_next:
        if st.button("التالي ➡️", key=f"{player_key}_next"):
            st.session_state[action_key] = "next"
    with col_letter:
        selected_idx = player_data["selected_letter_idx"]
        selected_letter = ARABIC_LETTERS[selected_idx]
        selected_state = player_data["letters"][selected_letter]
        st.markdown(f"<div style='text-align:center;font-size:48px;font-weight:bold;padding:16px 0 12px 0;background:{get_bg_color(selected_state)};border-radius:50%;border:3px solid #1976d2;display:inline-block;width:80px;height:80px;line-height:80px;margin:0 12px;'>{selected_letter}</div>", unsafe_allow_html=True)
    with col_change:
        if st.button("🔄 تغيير الحالة", key=f"{player_key}_change_state"):
            st.session_state[action_key] = "change"
    if st.session_state[action_key] == "prev":
        player_data["selected_letter_idx"] = (selected_idx - 1) % len(ARABIC_LETTERS)
        st.session_state[action_key] = None
    elif st.session_state[action_key] == "next":
        player_data["selected_letter_idx"] = (selected_idx + 1) % len(ARABIC_LETTERS)
        st.session_state[action_key] = None
    elif st.session_state[action_key] == "change":
        player_data["letters"][selected_letter] = next_state(selected_state)
        st.session_state[action_key] = None

# ---- Main Layout ----
st.title("🎲 لعبة الحروف العربية")

player_cols = st.columns(num_players)

for i, col in enumerate(player_cols, start=1):
    with col:
        player_key = f"player_{i}"
        player_data = st.session_state.players[player_key]
        with st.expander(f"{player_data['name']}", expanded=True):
            render_player_wheel(player_key, player_data, i)
