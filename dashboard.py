# dashboard.py - CafeEye AI

import streamlit as st
import cv2
import time
import threading
from datetime import datetime
from detector import (
    TableTracker, TABLES,
    detect_people_in_zone,
    draw_tables, draw_summary,
    format_duration
)
from menu import MENU, get_spice_emoji

st.set_page_config(
    page_title="CafeEye AI",
    page_icon="☕",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500&display=swap');

* { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Playfair Display', serif; }

.stApp {
    background-color: #f5f0e8;
    background-image:
        radial-gradient(ellipse at 20% 20%, rgba(210,180,140,0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(139,90,43,0.08) 0%, transparent 50%);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; }

.hero {
    background: linear-gradient(135deg, #2c1810 0%, #5c3317 50%, #8b5e3c 100%);
    border-radius: 24px;
    padding: 28px 36px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 32px rgba(44,24,16,0.25);
}
.hero-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 2.4rem;
    font-weight: 700;
    color: #f5e6d3;
    margin: 0;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    font-size: 0.9rem;
    color: rgba(245,230,211,0.7);
    margin: 4px 0 0 0;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
.hero-time {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    color: #f5e6d3;
    opacity: 0.85;
}
.metric-card {
    background: white;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 2px 12px rgba(44,24,16,0.08);
    border: 1px solid rgba(139,90,43,0.1);
    text-align: center;
}
.table-card {
    background: white;
    border-radius: 14px;
    padding: 14px 18px;
    margin: 8px 0;
    box-shadow: 0 2px 8px rgba(44,24,16,0.06);
    border-left: 4px solid #ddd;
    display: flex;
    align-items: center;
    gap: 12px;
}
.table-card.occupied { border-left-color: #c0392b; }
.table-card.empty { border-left-color: #27ae60; }
.table-card.attention { border-left-color: #e67e22; }
.table-name {
    font-weight: 600;
    color: #2c1810;
    font-size: 0.95rem;
}
.table-info {
    font-size: 0.8rem;
    color: #8b7355;
    margin-top: 2px;
}
.table-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
}
.dot-occupied { background: #c0392b; box-shadow: 0 0 6px rgba(192,57,43,0.5); }
.dot-empty { background: #27ae60; box-shadow: 0 0 6px rgba(39,174,96,0.5); }
.dot-attention { background: #e67e22; box-shadow: 0 0 6px rgba(230,126,34,0.5); }
.ai-bubble {
    background: linear-gradient(135deg, #2c1810, #5c3317);
    border-radius: 16px;
    padding: 18px 22px;
    margin: 12px 0;
    color: #f5e6d3;
    font-size: 15px;
    line-height: 1.7;
    box-shadow: 0 4px 16px rgba(44,24,16,0.2);
}
.welcome-box {
    background: linear-gradient(135deg, #2c1810 0%, #5c3317 50%, #8b5e3c 100%);
    border-radius: 24px;
    padding: 40px;
    text-align: center;
    color: #f5e6d3;
    margin: 16px 0;
    box-shadow: 0 8px 32px rgba(44,24,16,0.25);
}
.welcome-title {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 8px;
}
.welcome-sub { font-size: 1rem; opacity: 0.8; }
.dish-card {
    background: white;
    border-radius: 16px;
    padding: 16px;
    margin: 8px 0;
    border: 1px solid rgba(139,90,43,0.12);
    box-shadow: 0 2px 8px rgba(44,24,16,0.06);
}
.dish-name {
    font-weight: 600;
    color: #2c1810;
    font-size: 1rem;
    margin-bottom: 6px;
}
.dish-meta { font-size: 0.8rem; color: #8b7355; }
.order-card {
    background: white;
    border-left: 4px solid #27ae60;
    border-radius: 12px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #2c1810;
    font-size: 0.9rem;
    box-shadow: 0 2px 8px rgba(44,24,16,0.06);
}
.log-entry {
    background: white;
    border-radius: 10px;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 0.85rem;
    color: #5c3317;
    border: 1px solid rgba(139,90,43,0.1);
}
.section-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem;
    color: #2c1810;
    font-weight: 600;
    margin: 20px 0 12px 0;
}
.stButton > button {
    border-radius: 12px !important;
    font-weight: 500 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all 0.2s !important;
    border: 1px solid rgba(139,90,43,0.2) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2c1810, #5c3317) !important;
    color: #f5e6d3 !important;
    border: none !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(44,24,16,0.2) !important;
}
hr { border-color: rgba(139,90,43,0.15) !important; margin: 20px 0 !important; }
.stTabs [data-baseweb="tab-list"] {
    background: #ece5d8 !important;
    border-radius: 12px !important;
    padding: 4px !important;
}
div[data-testid="metric-container"] {
    background: white !important;
    border-radius: 16px !important;
    padding: 16px !important;
    border: 1px solid rgba(139,90,43,0.1) !important;
    box-shadow: 0 2px 12px rgba(44,24,16,0.06) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', serif !important;
    color: #2c1810 !important;
}
[data-testid="stMetricLabel"] { color: #8b7355 !important; }
.stTextArea textarea {
    border-radius: 12px !important;
    border-color: rgba(139,90,43,0.25) !important;
    background: white !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────
if "tracker" not in st.session_state:
    st.session_state.tracker = TableTracker()
if "log" not in st.session_state:
    st.session_state.log = []
if "stop_flag" not in st.session_state:
    st.session_state.stop_flag = {"stop": True}
if "frame_holder" not in st.session_state:
    st.session_state.frame_holder = [None]
if "orders" not in st.session_state:
    st.session_state.orders = []
if "page" not in st.session_state:
    st.session_state.page = "main"
if "order_step" not in st.session_state:
    st.session_state.order_step = "idle"
if "order_type" not in st.session_state:
    st.session_state.order_type = None
if "order_text" not in st.session_state:
    st.session_state.order_text = ""
if "rec_spoken" not in st.session_state:
    st.session_state.rec_spoken = False
if "confirm_spoken" not in st.session_state:
    st.session_state.confirm_spoken = False

# ── Camera Thread ─────────────────────────────────────────
def camera_loop(tracker, log_list, stop_flag, frame_holder):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 860)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while not stop_flag["stop"]:
        ret, frame = cap.read()
        if not ret:
            break
        for name, zone in TABLES.items():
            was_occupied = tracker.tables[name]["occupied"]
            person_detected, count = detect_people_in_zone(frame, zone)
            tracker.update(name, person_detected, count)
            is_occupied = tracker.tables[name]["occupied"]
            if was_occupied and not is_occupied:
                log_list.insert(0, f"🟢 {datetime.now().strftime('%H:%M:%S')} — {name} EMPTY")
            if not was_occupied and is_occupied:
                log_list.insert(0, f"🔴 {datetime.now().strftime('%H:%M:%S')} — {name} OCCUPIED")
        frame = draw_tables(frame, tracker)
        frame = draw_summary(frame, tracker)
        frame_holder[0] = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        time.sleep(0.05)
    cap.release()
    frame_holder[0] = None

# ── Speak Helper ──────────────────────────────────────────
def speak(text):
    try:
        from live_agent import say_text
        say_text(text)
    except Exception as e:
        print(f"Speak error: {e}")

# ══════════════════════════════════════════════════════════
# HERO HEADER
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
    <div>
        <div class="hero-title">☕ CafeEye AI</div>
        <div class="hero-subtitle">Real-time Restaurant Intelligence</div>
    </div>
    <div class="hero-time">{datetime.now().strftime('%H:%M')}</div>
</div>
""", unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────
n1, n2, n3, n4 = st.columns(4)
with n1:
    if st.button("🏠  Dashboard", use_container_width=True, key="nav_home"):
        st.session_state.page = "main"
        st.rerun()
with n2:
    if st.button("🎤  Ask AI", use_container_width=True, key="nav_ask"):
        st.session_state.page = "ask"
        st.rerun()
with n3:
    if st.button("🍽️  Menu", use_container_width=True, key="nav_menu"):
        st.session_state.page = "menu"
        st.rerun()
with n4:
    if st.button("🛎️  Place Order", type="primary",
                 use_container_width=True, key="nav_order"):
        st.session_state.page = "order"
        st.session_state.order_step = "idle"
        st.session_state.rec_spoken = False
        st.session_state.confirm_spoken = False
        st.rerun()

st.divider()

# ══════════════════════════════════════════════════════════
# PAGE: MAIN DASHBOARD
# ══════════════════════════════════════════════════════════
if st.session_state.page == "main":

    cc1, cc2, cc3 = st.columns([1, 1, 2])
    with cc1:
        if st.button("▶  Start Camera", type="primary",
                     use_container_width=True, key="cam_start"):
            if st.session_state.stop_flag["stop"]:
                st.session_state.stop_flag = {"stop": False}
                t = threading.Thread(
                    target=camera_loop,
                    args=(
                        st.session_state.tracker,
                        st.session_state.log,
                        st.session_state.stop_flag,
                        st.session_state.frame_holder
                    ),
                    daemon=True
                )
                t.start()
    with cc2:
        if st.button("⏹  Stop",
                     use_container_width=True, key="cam_stop"):
            st.session_state.stop_flag["stop"] = True
    with cc3:
        if st.button("🔄  Reset All Data",
                     use_container_width=True, key="cam_reset"):
            st.session_state.stop_flag["stop"] = True
            time.sleep(0.2)
            st.session_state.tracker = TableTracker()
            st.session_state.log = []
            st.session_state.orders = []
            st.session_state.frame_holder = [None]
            st.rerun()

    # ── Live Camera ───────────────────────────────────────
    st.markdown('<div class="section-header">📷 Live Camera Feed</div>',
                unsafe_allow_html=True)

    cam_placeholder = st.empty()
    frame = st.session_state.frame_holder[0]
    if frame is not None:
        cam_placeholder.image(frame, channels="RGB", use_container_width=True)
    else:
        cam_placeholder.markdown("""
        <div style="background:white; border-radius:20px; padding:60px;
                    text-align:center; border:2px dashed rgba(139,90,43,0.2)">
            <div style="font-size:3rem">📷</div>
            <div style="font-family:'Playfair Display',serif; font-size:1.2rem;
                        color:#5c3317; margin-top:12px">Camera not started</div>
            <div style="color:#8b7355; font-size:0.9rem; margin-top:6px">
                Click Start Camera above to begin</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Metrics ───────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Live Stats</div>',
                unsafe_allow_html=True)
    summary = st.session_state.tracker.get_summary()
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Occupied Tables",
                  f"{summary['occupied_tables']}/{summary['total_tables']}")
    with m2:
        st.metric("Empty Tables", summary['empty_tables'])
    with m3:
        st.metric("Visitors Today", summary['total_visitors'])
    with m4:
        st.metric("Alerts", len(summary['attention_needed']))

    # ── Table Status ──────────────────────────────────────
    st.markdown('<div class="section-header">🪑 Table Status</div>',
                unsafe_allow_html=True)
    tracker = st.session_state.tracker
    t_cols = st.columns(3)
    for i, (name, table) in enumerate(tracker.tables.items()):
        with t_cols[i % 3]:
            if table["needs_attention"]:
                css = "attention"
                dot = "dot-attention"
                info = f"⚠️ Needs Attention • {format_duration(table['duration'])}"
            elif table["occupied"]:
                css = "occupied"
                dot = "dot-occupied"
                info = f"🕐 {format_duration(table['duration'])} • {table['customer_count']} guests"
            else:
                css = "empty"
                dot = "dot-empty"
                info = "Available"
            st.markdown(f"""
            <div class="table-card {css}">
                <div class="table-dot {dot}"></div>
                <div>
                    <div class="table-name">{name}</div>
                    <div class="table-info">{info}</div>
                </div>
            </div>""", unsafe_allow_html=True)

    # ── Log + Chart ───────────────────────────────────────
    st.markdown('<div class="section-header">📋 Activity & Analytics</div>',
                unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.log:
            for entry in st.session_state.log[:8]:
                st.markdown(f'<div class="log-entry">{entry}</div>',
                            unsafe_allow_html=True)
        else:
            st.info("No activity yet — start the camera to begin tracking")
    with col2:
        if summary["peak_hours"]:
            st.bar_chart(summary["peak_hours"])
        else:
            st.info("Peak hour data will appear here")

    # Auto refresh for live camera
    time.sleep(1)
    st.rerun()

# ══════════════════════════════════════════════════════════
# PAGE: ASK AI
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "ask":
    st.markdown("""
    <div class="welcome-box">
        <div class="welcome-title">🎤 Ask CafeEye</div>
        <div class="welcome-sub">I can see the restaurant — ask me anything!</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="ai-bubble">
        🤖 <b>Hi! I'm CafeEye.</b> I can see the restaurant through the camera right now.
        Ask me anything — which tables are free, how long guests have been seated,
        how many people are here, or any question about the restaurant!
        <br><br>
        <i>Just click the button below and speak naturally</i>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🎤  Click & Speak", type="primary",
                 use_container_width=True, key="ask_speak"):
        with st.spinner("🎤 Listening... speak your question now!"):
            try:
                from live_agent import ask_voice
                result = ask_voice(st.session_state.tracker, format_duration)
                if result:
                    st.success("✅ Done! Click again to ask another question.")
                else:
                    st.error("❌ No response received — please try again.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ══════════════════════════════════════════════════════════
# PAGE: MENU
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "menu":
    st.markdown("""
    <div class="welcome-box">
        <div class="welcome-title">🍽️ Our Menu</div>
        <div class="welcome-sub">Fresh ingredients, crafted with love</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🥦  Vegetarian", "🍗  Non-Vegetarian"])

    with tab1:
        cols = st.columns(2)
        for i, dish in enumerate(MENU["veg"]):
            with cols[i % 2]:
                spice_icon = get_spice_emoji(dish["spice"])
                st.markdown(f"""
                <div class="dish-card">
                    <div class="dish-name">{dish['id']}. {dish['name']}</div>
                    <div class="dish-meta">
                        💰 <b>Rs.{dish['price']}</b> &nbsp;•&nbsp;
                        🔥 {dish['calories']} cal &nbsp;•&nbsp;
                        {spice_icon} {dish['spice']}
                    </div>
                    <div style="font-size:0.8rem;color:#8b7355;margin-top:6px">
                        {dish['description']}
                    </div>
                </div>""", unsafe_allow_html=True)

    with tab2:
        cols = st.columns(2)
        for i, dish in enumerate(MENU["nonveg"]):
            with cols[i % 2]:
                spice_icon = get_spice_emoji(dish["spice"])
                st.markdown(f"""
                <div class="dish-card">
                    <div class="dish-name">{dish['id']}. {dish['name']}</div>
                    <div class="dish-meta">
                        💰 <b>Rs.{dish['price']}</b> &nbsp;•&nbsp;
                        🔥 {dish['calories']} cal &nbsp;•&nbsp;
                        {spice_icon} {dish['spice']}
                    </div>
                    <div style="font-size:0.8rem;color:#8b7355;margin-top:6px">
                        {dish['description']}
                    </div>
                </div>""", unsafe_allow_html=True)

    st.divider()
    if st.button("🛎️  Place an Order", type="primary", key="menu_to_order"):
        st.session_state.page = "order"
        st.session_state.order_step = "idle"
        st.rerun()

# ══════════════════════════════════════════════════════════
# PAGE: ORDER
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "order":

    # ── STEP: idle ────────────────────────────────────────
    if st.session_state.order_step == "idle":
        st.markdown("""
        <div class="welcome-box">
            <div class="welcome-title">🍽️ Welcome!</div>
            <div class="welcome-sub">
                Our AI assistant will guide you through your order
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="ai-bubble">
            🤖 <b>CafeEye says:</b> Welcome! I'm delighted to help you
            order today. Would you prefer
            <b>Vegetarian</b> or <b>Non-Vegetarian</b> cuisine?
            I'll personally recommend our best dishes!
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🥦  Vegetarian", type="primary",
                         use_container_width=True, key="order_veg"):
                st.session_state.order_type = "veg"
                st.session_state.order_step = "recommend"
                st.session_state.rec_spoken = False
                st.rerun()
        with col2:
            if st.button("🍗  Non-Vegetarian", type="primary",
                         use_container_width=True, key="order_nonveg"):
                st.session_state.order_type = "nonveg"
                st.session_state.order_step = "recommend"
                st.session_state.rec_spoken = False
                st.rerun()

    # ── STEP: recommend ───────────────────────────────────
    elif st.session_state.order_step == "recommend":
        order_type = st.session_state.order_type
        dishes = MENU[order_type]
        type_label = "Vegetarian" if order_type == "veg" else "Non-Vegetarian"
        top3 = dishes[:3]
        rec_text = ", ".join([d["name"] for d in top3])

        if not st.session_state.rec_spoken:
            with st.spinner("🔊 CafeEye is recommending dishes..."):
                speak(
                    f"Great choice! Here are my top {type_label} recommendations today. "
                    f"{rec_text}. "
                    f"These are our most popular dishes! "
                    f"Choose one or type your own order below."
                )
            st.session_state.rec_spoken = True

        st.markdown(f"""
        <div class="ai-bubble">
            🤖 <b>CafeEye recommends:</b> Here are our finest {type_label}
            dishes today. Choose one or scroll down to place a custom order!
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">⭐ Chef\'s Recommendations</div>',
                    unsafe_allow_html=True)
        rec_cols = st.columns(3)
        for i, dish in enumerate(top3):
            with rec_cols[i]:
                spice_icon = get_spice_emoji(dish["spice"])
                st.markdown(f"""
                <div class="dish-card" style="text-align:center;padding:20px">
                    <div style="font-size:2rem">
                        {"🥦" if order_type=="veg" else "🍗"}
                    </div>
                    <div class="dish-name" style="margin-top:8px">
                        {dish['name']}
                    </div>
                    <div class="dish-meta" style="margin:8px 0">
                        💰 <b>Rs.{dish['price']}</b><br>
                        🔥 {dish['calories']} cal &nbsp;•&nbsp;
                        {spice_icon} {dish['spice']}
                    </div>
                    <div style="font-size:0.78rem;color:#8b7355">
                        {dish['description']}
                    </div>
                </div>""", unsafe_allow_html=True)
                if st.button("Order This →",
                             key=f"rec_btn_{i}",
                             use_container_width=True):
                    st.session_state.order_text = dish["name"]
                    st.session_state.order_step = "confirm"
                    st.session_state.confirm_spoken = False
                    st.rerun()

        st.divider()

        st.markdown(f'<div class="section-header">📋 Full {type_label} Menu</div>',
                    unsafe_allow_html=True)
        cols = st.columns(2)
        for i, dish in enumerate(dishes):
            with cols[i % 2]:
                spice_icon = get_spice_emoji(dish["spice"])
                st.markdown(f"""
                <div class="dish-card">
                    <div class="dish-name">#{dish['id']} {dish['name']}</div>
                    <div class="dish-meta">
                        💰 Rs.{dish['price']} &nbsp;•&nbsp;
                        {spice_icon} {dish['spice']} &nbsp;•&nbsp;
                        🔥 {dish['calories']} cal
                    </div>
                </div>""", unsafe_allow_html=True)

        st.divider()

        st.markdown("""
        <div class="ai-bubble">
            🤖 <b>CafeEye says:</b> Can't find what you're looking for?
            Type your custom order below!
        </div>
        """, unsafe_allow_html=True)

        order_input = st.text_area(
            "Your Order",
            placeholder="e.g. 1 Butter Chicken, 2 Veg Biryani, 1 Dal Makhani...",
            height=100,
            key="order_text_input",
            label_visibility="collapsed"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅  Place Order", type="primary",
                         use_container_width=True, key="place_custom"):
                if order_input.strip():
                    st.session_state.order_text = order_input.strip()
                    st.session_state.order_step = "confirm"
                    st.session_state.confirm_spoken = False
                    st.rerun()
                else:
                    st.warning("Please type your order or choose a recommendation!")
        with col2:
            if st.button("← Go Back",
                         use_container_width=True, key="back_recommend"):
                st.session_state.order_step = "idle"
                st.session_state.rec_spoken = False
                st.rerun()

    # ── STEP: confirm ─────────────────────────────────────
    elif st.session_state.order_step == "confirm":
        order = st.session_state.order_text

        st.markdown(f"""
        <div class="welcome-box">
            <div style="font-size:3rem">✅</div>
            <div class="welcome-title" style="margin-top:12px">
                Order Confirmed!
            </div>
            <div style="font-size:1.2rem;opacity:0.9;margin-top:8px;
                        background:rgba(255,255,255,0.15);padding:10px 20px;
                        border-radius:12px;display:inline-block">
                {order}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.confirm_spoken:
            with st.spinner("🔊 CafeEye is confirming your order..."):
                speak(
                    f"Thank you so much for your order! "
                    f"You have ordered {order}. "
                    f"Your food will be freshly prepared and served shortly. "
                    f"Thank you for dining with us today. Enjoy your meal!"
                )
            st.session_state.confirm_spoken = True
            order_entry = f"🛎️ {datetime.now().strftime('%H:%M:%S')} — {order}"
            st.session_state.orders.insert(0, order_entry)
            st.session_state.log.insert(0, order_entry)

        st.markdown(f"""
        <div class="ai-bubble">
            🤖 <b>CafeEye says:</b> Your order of <b>{order}</b> has been
            placed! Our kitchen is already preparing it fresh.
            Sit back and relax — your food will be with you shortly. 🍽️
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄  Place Another Order", type="primary",
                         use_container_width=True, key="another_order"):
                st.session_state.order_step = "idle"
                st.session_state.order_text = ""
                st.session_state.rec_spoken = False
                st.session_state.confirm_spoken = False
                st.rerun()
        with col2:
            if st.button("🏠  Back to Dashboard",
                         use_container_width=True, key="back_dashboard"):
                st.session_state.page = "main"
                st.session_state.order_step = "idle"
                st.session_state.rec_spoken = False
                st.session_state.confirm_spoken = False
                st.rerun()

        if st.session_state.orders:
            st.divider()
            st.markdown('<div class="section-header">📋 Orders Today</div>',
                        unsafe_allow_html=True)
            for o in st.session_state.orders:
                st.markdown(f'<div class="order-card">{o}</div>',
                            unsafe_allow_html=True)