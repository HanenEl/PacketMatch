import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import date

st.set_page_config(page_title="WE Package Recommender", layout="wide")
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#------------------Data----------------------
standard_packages = [
    {"package_id": "STD-1111-140",  "category": "Super", "package_size_gb": 140,  "monthly_price": 210,  "speed_mbps": 30},
    {"package_id": "STD-1111-200",  "category": "Super", "package_size_gb": 200,  "monthly_price": 290,  "speed_mbps": 30},
    {"package_id": "STD-1111-250",  "category": "Super", "package_size_gb": 250,  "monthly_price": 360,  "speed_mbps": 30},
    {"package_id": "STD-1111-400",  "category": "Super", "package_size_gb": 400,  "monthly_price": 570,  "speed_mbps": 30},
    {"package_id": "STD-1111-600",  "category": "Super", "package_size_gb": 600,  "monthly_price": 850,  "speed_mbps": 30},
    {"package_id": "STD-1111-1000", "category": "Super", "package_size_gb": 1000, "monthly_price": 1360, "speed_mbps": 30},
    {"package_id": "STD-2222-250",  "category": "Mega",  "package_size_gb": 250,  "monthly_price": 530,  "speed_mbps": 70},
    {"package_id": "STD-2222-600",  "category": "Mega",  "package_size_gb": 600,  "monthly_price": 1040, "speed_mbps": 70},
    {"package_id": "STD-2222-1000", "category": "Mega",  "package_size_gb": 1000, "monthly_price": 1560, "speed_mbps": 70},
    {"package_id": "STD-3333-250",  "category": "Ultra", "package_size_gb": 250,  "monthly_price": 700,  "speed_mbps": 100},
    {"package_id": "STD-3333-600",  "category": "Ultra", "package_size_gb": 600,  "monthly_price": 1230, "speed_mbps": 100},
    {"package_id": "STD-4444-1000", "category": "Max",   "package_size_gb": 1000, "monthly_price": 1760, "speed_mbps": 200},
    {"package_id": "STD-5555-1000", "category": "MaxP",  "package_size_gb": 1000, "monthly_price": 2000, "speed_mbps": 500},
]
PKG_LOOKUP = {p["package_id"]: p for p in standard_packages}

GOVERNORATES =[
    "Cairo","Giza","Alexandria","Dakahlia","Sharqia","Gharbia",
    "Kafr El Sheikh","Monufia","Beheira","Damietta","Port Said",
    "Ismailia","Suez","Faiyum","Beni Suef","Minya","Assiut",
    "Sohag","Qena","Luxor","Aswan","Red Sea","North Sinai",
    "South Sinai","Matrouh",]

# -----------------Model----------------------
@st.cache_resource(show_spinner="Loading model...")
def load_model():
    return (
        joblib.load("models\we_model.pkl"),
        joblib.load("models\we_target_le.pkl"),
        joblib.load("models\we_pkg_le.pkl"),
        joblib.load("models\we_feature_cols.pkl"),
    )
model, target_le, pkg_le, feature_cols = load_model()
print(model.get_booster().feature_names)

#-----------------Prediction-------------------
def predict(gov, pkg_id, num_devices, renewal_date, usage_so_far):
    pkg          = PKG_LOOKUP[pkg_id]
    days_until   = max((renewal_date - date.today()).days, 0)
    days_passed  = max(30 - days_until, 1)
    remaining    = max(pkg["package_size_gb"] - usage_so_far, 0)
    projected    = round((usage_so_far / days_passed) * 30, 2)
    actual_speed = round(pkg["speed_mbps"] / (num_devices ** 0.5), 2)

    row = {
        "current_package_id":      pkg_le.transform([pkg_id])[0],
        "current_package_size_gb": pkg["package_size_gb"],
        "current_package_price":   pkg["monthly_price"],
        "current_speed_mbps":      pkg["speed_mbps"],
        "number_of_devices":       num_devices,
        "days_passed":             days_passed,
        "days_until_renewal":      days_until,
        "usage_so_far_gb":         usage_so_far,
        "remaining_gb":            remaining,
        "actual_speed_mbps":       actual_speed,
        "usage_efficiency":        usage_so_far / pkg["package_size_gb"],
        "price_per_gb":            pkg["monthly_price"] / pkg["package_size_gb"],
        "speed_per_device":        actual_speed / num_devices,
    }

    X        = pd.DataFrame([row])[list(feature_cols)]
    pred_enc = model.predict(X, validate_features=False)[0]
    rec_pkg_id = target_le.inverse_transform([pred_enc])[0]

    return rec_pkg_id, projected, remaining, actual_speed

#-------------Result card------------------------
def render_result_card(direction, rec_pkg_id, pkg_id, rec_pkg, price_diff):
    if direction == "no_change":
        st.markdown(f"""
        <div class="we-result-card card-same">
            <div class="we-card-subtitle text-green">No Change Needed</div>
            <div class="we-card-pkg-name">{pkg_id}</div>
            <div class="we-card-muted">Your current package is already the best fit.</div>
        </div>
        """, unsafe_allow_html=True)

    elif direction == "upgrade":
        st.markdown(f"""
        <div class="we-result-card card-upgrade">
            <div class="we-card-subtitle text-gold">Upgrade Recommended</div>
            <div class="we-card-pkg-name">{rec_pkg_id}</div>
            <div class="we-card-details">{rec_pkg['package_size_gb']} GB &nbsp;·&nbsp; {rec_pkg['monthly_price']} EGP/mo &nbsp;·&nbsp; up to {rec_pkg['speed_mbps']} Mbps</div>
            <div class="we-card-price-row">Price change: &nbsp;<span class="we-card-price-val text-red">{price_diff:+,} EGP/mo</span></div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="we-result-card card-downgrade">
            <div class="we-card-subtitle text-blue">Downgrade Available</div>
            <div class="we-card-pkg-name">{rec_pkg_id}</div>
            <div class="we-card-details">{rec_pkg['package_size_gb']} GB &nbsp;·&nbsp; {rec_pkg['monthly_price']} EGP/mo &nbsp;·&nbsp; up to {rec_pkg['speed_mbps']} Mbps</div>
            <div class="we-card-price-row">Price change: &nbsp;<span class="we-card-price-val text-green">{price_diff:+,} EGP/mo</span></div>
        </div>
        """, unsafe_allow_html=True)

# -------------------Sidebar----------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:10px 0 20px;">
        <div style="font-size:2.2rem; font-weight:900; letter-spacing:-1px;">
            <span style="color:#6B21A8;">WE</span>
            <span style="color:#F5F0E8; font-size:1rem; font-weight:400; margin-left:6px;">Telecom Egypt</span>
        </div>
        <div style="color:#F5F0E8; font-size:0.7rem; letter-spacing:3px; text-transform:uppercase; margin-top:2px;">
            Package Recommender
        </div>
    </div>
    <hr style="border-color: rgb(224, 216, 204); opacity:0.4;">
    """, unsafe_allow_html=True)

    page = st.radio("", ["Package Information", "Recommender"])
    st.markdown('<hr style="border-color:#E0D8CC; opacity:0.3;">', unsafe_allow_html=True)

# -------------Page 1: Packages Info-----------------
if page == "Package Information":
    st.markdown('<div style="text-align:center; font-size:2.5rem; font-weight:900; margin-bottom:30px;">WE Space Super</div>', unsafe_allow_html=True)

    # Full-width main row so tabs + card grid span the content area (avoids nested column shrink / left bias)
    selected_cat = st.radio("Category", ["Super","Mega","Ultra","Max","MaxP"],
                            horizontal=True, label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)

    cat_pkgs = [p for p in standard_packages if p["category"] == selected_cat]
    for i in range(0, len(cat_pkgs), 3):
        cols = st.columns(3, gap="large")
        for j, pkg in enumerate(cat_pkgs[i:i+3]):
            with cols[j]:
                st.markdown(f"""
                <div class="we-plan-card">
                    <div class="we-plan-top">
                        <div class="we-plan-size">{pkg['package_size_gb']} GB</div>
                        <div class="we-plan-price">{pkg['monthly_price']} EGP / Month</div>
                        <div class="we-plan-price-year">{pkg['monthly_price']*12:,} EGP / year</div>
                    </div>
                    <div class="we-plan-bottom">
                        <div class="we-plan-speed-text">Speed Up to {pkg['speed_mbps']} Mbps</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

#------------- Page 2: Recommender-------------------
elif page == "Recommender":
    st.markdown("""
    <div style="font-size:2.5rem; font-weight:900; margin-top:30px;">PACKAGE RECOMMENDER</div>
    <p style="color:#6B6B6B; font-size:0.95rem; margin-bottom:40px;">
        Enter your details to get a personalized package recommendation
    </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="we-section-title">Customer Info</div>', unsafe_allow_html=True)
        gov     = st.selectbox("Governorate", GOVERNORATES)
        pkg_opts= {f"{p['package_id']}  —  {p['package_size_gb']} GB  ·  {p['monthly_price']} EGP  ·  {p['speed_mbps']} Mbps": p["package_id"] for p in standard_packages}
        pkg_id  = pkg_opts[st.selectbox("Current Package", list(pkg_opts.keys()))]
        pkg     = PKG_LOOKUP[pkg_id]
        num_devices = st.slider("Number of Devices", 1, 9, 3)

    with col2:
        st.markdown('<div class="we-section-title">Usage Info</div>', unsafe_allow_html=True)
        renewal_date = st.date_input("Renewal Date",
                                     value=date.today().replace(day=min(date.today().day+15, 28)),
                                     min_value=date.today())
        usage_so_far = st.slider("Usage so far (GB)", 1.0, float(pkg["package_size_gb"]*1.5),
                                 float(pkg["package_size_gb"])*0.5, step=1.0)

    st.markdown('<hr class="we-divider">', unsafe_allow_html=True)

    if st.button("Get My Recommendation", type="primary", use_container_width=True):
        rec_pkg_id, projected, remaining, actual_speed = predict(
            gov, pkg_id, num_devices, renewal_date, usage_so_far)

        rec_pkg    = PKG_LOOKUP[rec_pkg_id]
        price_diff = rec_pkg["monthly_price"] - pkg["monthly_price"]
        direction  = "no_change" if rec_pkg_id == pkg_id else ("upgrade" if price_diff > 0 else "downgrade")

        r1, r2, r3 = st.columns(3)
        r1.metric("Projected Usage", f"{projected:.0f} GB",      delta=f"{projected - pkg['package_size_gb']:+.0f} vs package")
        r2.metric("Remaining",       f"{remaining:.0f} GB",      delta=f"{remaining/pkg['package_size_gb']*100:.0f}% left")
        r3.metric("Actual Speed",    f"{actual_speed:.1f} Mbps", delta=f"shared · {num_devices} devices")

        st.markdown('<hr class="we-divider">', unsafe_allow_html=True)
        render_result_card(direction, rec_pkg_id, pkg_id, rec_pkg, price_diff)       