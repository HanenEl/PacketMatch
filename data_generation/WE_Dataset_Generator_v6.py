# ════════════════════════════════════════════════════════════════════
# Simulates 50,000 WE internet subscribers, each with a usage profile
# (over / heavy / normal / casual), number of devices, and current
# package. Observable mid-cycle features (usage, remaining GB,
# projected usage, actual speed) are derived from a hidden daily rate.
# A scoring model then recommends whether to keep or switch packages,
# balancing volume fit (60%), price (30%), and speed (10%).
# ════════════════════════════════════════════════════════════════════

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)
TODAY = datetime.today()

# ═══════════════════════════════════════════
# 1. PACKAGES
# ═══════════════════════════════════════════

standard_packages = [
    {"package_id": "STD-1111-140",  "category": "Super", "package_type": "Standard", "package_size_gb": 140,  "monthly_price": 210,  "speed_mbps": 30},
    {"package_id": "STD-1111-200",  "category": "Super", "package_type": "Standard", "package_size_gb": 200,  "monthly_price": 290,  "speed_mbps": 30},
    {"package_id": "STD-1111-250",  "category": "Super", "package_type": "Standard", "package_size_gb": 250,  "monthly_price": 360,  "speed_mbps": 30},
    {"package_id": "STD-1111-400",  "category": "Super", "package_type": "Standard", "package_size_gb": 400,  "monthly_price": 570,  "speed_mbps": 30},
    {"package_id": "STD-1111-600",  "category": "Super", "package_type": "Standard", "package_size_gb": 600,  "monthly_price": 850,  "speed_mbps": 30},
    {"package_id": "STD-1111-1000", "category": "Super", "package_type": "Standard", "package_size_gb": 1000, "monthly_price": 1360, "speed_mbps": 30},
    {"package_id": "STD-2222-250",  "category": "Mega",  "package_type": "Standard", "package_size_gb": 250,  "monthly_price": 530,  "speed_mbps": 70},
    {"package_id": "STD-2222-600",  "category": "Mega",  "package_type": "Standard", "package_size_gb": 600,  "monthly_price": 1040, "speed_mbps": 70},
    {"package_id": "STD-2222-1000", "category": "Mega",  "package_type": "Standard", "package_size_gb": 1000, "monthly_price": 1560, "speed_mbps": 70},
    {"package_id": "STD-3333-250",  "category": "Ultra", "package_type": "Standard", "package_size_gb": 250,  "monthly_price": 700,  "speed_mbps": 100},
    {"package_id": "STD-3333-600",  "category": "Ultra", "package_type": "Standard", "package_size_gb": 600,  "monthly_price": 1230, "speed_mbps": 100},
    {"package_id": "STD-4444-1000", "category": "Max",   "package_type": "Standard", "package_size_gb": 1000, "monthly_price": 1760, "speed_mbps": 200},
    {"package_id": "STD-5555-1000", "category": "MaxP",  "package_type": "Standard", "package_size_gb": 1000, "monthly_price": 2000, "speed_mbps": 500},
]

packages_df     = pd.DataFrame(standard_packages)
packages_lookup = {p["package_id"]: p for p in standard_packages}

PKG_BY_CATEGORY = {
    "Super": ["STD-1111-140", "STD-1111-200", "STD-1111-250", "STD-1111-400", "STD-1111-600", "STD-1111-1000"],
    "Mega":  ["STD-2222-250", "STD-2222-600", "STD-2222-1000"],
    "Ultra": ["STD-3333-250", "STD-3333-600"],
    "Max":   ["STD-4444-1000"],
    "MaxP":  ["STD-5555-1000"],
}

CAT_INTERNAL_W = {
    "Super": [0.30, 0.25, 0.20, 0.13, 0.08, 0.04],
    "Mega":  [0.45, 0.35, 0.20],
    "Ultra": [0.60, 0.40],
    "Max":   [1.00],
    "MaxP":  [1.00],
}

# ═══════════════════════════════════════════
# 2. GOVERNORATES
# ═══════════════════════════════════════════

governorates = [
    ("Cairo",          "02",  0.162),
    ("Giza",           "02",  0.117),
    ("Alexandria",     "03",  0.108),
    ("Dakahlia",       "050", 0.043),
    ("Sharqia",        "055", 0.055),
    ("Gharbia",        "040", 0.048),
    ("Kafr El Sheikh", "047", 0.034),
    ("Monufia",        "048", 0.026),
    ("Beheira",        "045", 0.033),
    ("Damietta",       "057", 0.023),
    ("Port Said",      "066", 0.022),
    ("Ismailia",       "064", 0.022),
    ("Suez",           "062", 0.022),
    ("Faiyum",         "084", 0.024),
    ("Beni Suef",      "082", 0.022),
    ("Minya",          "086", 0.029),
    ("Assiut",         "088", 0.028),
    ("Sohag",          "093", 0.020),
    ("Qena",           "095", 0.019),
    ("Luxor",          "095", 0.015),
    ("Aswan",          "097", 0.014),
    ("Red Sea",        "065", 0.014),
    ("North Sinai",    "069", 0.009),
    ("South Sinai",    "068", 0.007),
    ("Matrouh",        "046", 0.003),
]

gov_names   = [g[0] for g in governorates]
gov_codes   = [g[1] for g in governorates]
gov_weights = np.array([g[2] for g in governorates])
gov_weights = gov_weights / gov_weights.sum()

# ═══════════════════════════════════════════
# 3. DISTRIBUTIONS
# ═══════════════════════════════════════════

PROFILES        = ["over", "heavy", "normal", "casual"]
PROFILE_WEIGHTS = [0.40,   0.30,    0.20,     0.10]

# ═══════════════════════════════════════════
# 4. HELPER FUNCTIONS
# ═══════════════════════════════════════════

USED_IDS = set()

def generate_user_id(gov_code):
    n = 7 if len(gov_code) == 2 else 6
    for _ in range(100):
        uid = int(gov_code + ''.join([str(random.randint(0, 9)) for _ in range(n)]))
        if uid not in USED_IDS:
            USED_IDS.add(uid)
            return uid
    uid = int(gov_code + ''.join([str(random.randint(0, 9)) for _ in range(n)])) + len(USED_IDS)
    USED_IDS.add(uid)
    return uid


def select_current_package(profile, num_devices):
    if profile == "over":
        if num_devices <= 2:
            cat_w = {"Super": 0.55, "Mega": 0.25, "Ultra": 0.15, "Max": 0.04, "MaxP": 0.01}
        elif num_devices <= 5:
            cat_w = {"Super": 0.30, "Mega": 0.35, "Ultra": 0.25, "Max": 0.08, "MaxP": 0.02}
        else:
            cat_w = {"Super": 0.10, "Mega": 0.25, "Ultra": 0.35, "Max": 0.22, "MaxP": 0.08}
    elif profile == "heavy":
        if num_devices <= 2:
            cat_w = {"Super": 0.40, "Mega": 0.35, "Ultra": 0.15, "Max": 0.08, "MaxP": 0.02}
        elif num_devices <= 5:
            cat_w = {"Super": 0.20, "Mega": 0.40, "Ultra": 0.25, "Max": 0.12, "MaxP": 0.03}
        else:
            cat_w = {"Super": 0.05, "Mega": 0.30, "Ultra": 0.40, "Max": 0.20, "MaxP": 0.05}
    elif profile == "normal":
        if num_devices <= 2:
            cat_w = {"Super": 0.60, "Mega": 0.25, "Ultra": 0.10, "Max": 0.04, "MaxP": 0.01}
        elif num_devices <= 5:
            cat_w = {"Super": 0.40, "Mega": 0.35, "Ultra": 0.15, "Max": 0.08, "MaxP": 0.02}
        else:
            cat_w = {"Super": 0.20, "Mega": 0.40, "Ultra": 0.25, "Max": 0.12, "MaxP": 0.03}
    else:  # casual
        if num_devices <= 2:
            cat_w = {"Super": 0.80, "Mega": 0.15, "Ultra": 0.04, "Max": 0.01, "MaxP": 0.00}
        elif num_devices <= 5:
            cat_w = {"Super": 0.60, "Mega": 0.30, "Ultra": 0.08, "Max": 0.02, "MaxP": 0.00}
        else:
            cat_w = {"Super": 0.40, "Mega": 0.35, "Ultra": 0.18, "Max": 0.06, "MaxP": 0.01}

    cats    = list(cat_w.keys())
    weights = np.array(list(cat_w.values()))
    weights = weights / weights.sum()
    chosen_cat = np.random.choice(cats, p=weights)

    pkg_ids = PKG_BY_CATEGORY[chosen_cat]
    pkg_w   = np.array(CAT_INTERNAL_W[chosen_cat])
    pkg_w   = pkg_w / pkg_w.sum()
    return np.random.choice(pkg_ids, p=pkg_w)


def generate_daily_rate(profile, package_size_gb, num_devices):
    pct_ranges = {
        "over":   (0.95, 1.40),
        "heavy":  (0.75, 0.94),
        "normal": (0.45, 0.74),
        "casual": (0.15, 0.44),
    }
    low, high  = pct_ranges[profile]
    base_pct   = random.uniform(low, high)
    device_mul = 1 + (num_devices - 1) * 0.08
    daily_rate = (base_pct * package_size_gb / 30) * device_mul
    noise      = random.gauss(1.0, 0.05)
    return max(daily_rate * noise, 0.5)


def compute_observable_features(daily_rate_gb, days_passed, pkg_size_gb, pkg_speed_mbps, num_devices):
    usage_so_far_gb   = round(min(daily_rate_gb * days_passed, pkg_size_gb * 1.05), 2)
    remaining_gb      = round(max(pkg_size_gb - usage_so_far_gb, 0), 2)
    projected_usage_gb = round((usage_so_far_gb / days_passed) * 30, 2)
    actual_speed_mbps = round(pkg_speed_mbps / (num_devices ** 0.5), 2)
    return usage_so_far_gb, remaining_gb, projected_usage_gb, actual_speed_mbps


def recommend_package(projected_usage_gb, current_pkg_id, num_devices, all_pkgs_df):
    risk_factor = 1.10 if num_devices <= 4 else 1.15
    needed_gb   = projected_usage_gb * risk_factor

    speed_need = 30  

    std_pkgs         = all_pkgs_df[all_pkgs_df["package_type"] == "Standard"].copy()
    global_max_price = std_pkgs["monthly_price"].max()
    current_pkg      = packages_lookup[current_pkg_id]
    current_size     = current_pkg["package_size_gb"]

    # Hybrid no-change check (±15%)
    fit_ratio = current_size / max(needed_gb, 1)
    if 0.85 <= fit_ratio <= 1.30:
        return current_pkg_id

    suitable = std_pkgs[std_pkgs["package_size_gb"] >= needed_gb].copy()
    if len(suitable) == 0:
        suitable = std_pkgs.copy()

    def score(row):
        # W1: Volume 60%
        if row["package_size_gb"] >= needed_gb:
            vol = 1.0 - min((row["package_size_gb"] - needed_gb) / max(needed_gb, 1), 0.5) * 0.3
        else:
            vol = row["package_size_gb"] / needed_gb * 0.5

        # W2: Speed 10%
        speed_ratio = row["speed_mbps"] / max(speed_need, 1)
        spd = np.log1p(speed_ratio) / np.log1p(3.0)
        spd = min(spd, 1.0)

        # W3: Price 30%
        prc = 1 - (row["monthly_price"] / global_max_price)

        return 0.60*vol + 0.10*spd + 0.30*prc

    suitable["score"] = suitable.apply(score, axis=1)
    best = suitable.sort_values("score", ascending=False).iloc[0]

    # MaxP override
    if projected_usage_gb > 900:
        return "STD-5555-1000"

    return best["package_id"]


# ═══════════════════════════════════════════
# 5. MAIN GENERATION
# ═══════════════════════════════════════════

def generate_dataset(n=50000):
    records = []

    for _ in range(n):

        # ── Governorate ──
        idx      = np.random.choice(len(gov_names), p=gov_weights)
        gov_name = gov_names[idx]
        gov_code = gov_codes[idx]

        # ── User ID ──
        user_id = generate_user_id(gov_code)

        # ── Profile ──
        profile = np.random.choice(PROFILES, p=PROFILE_WEIGHTS)

        # ── Number of Devices ──
        device_probs = {
            "over":   [0.05, 0.10, 0.15, 0.18, 0.18, 0.14, 0.10, 0.06, 0.04],
            "heavy":  [0.08, 0.15, 0.20, 0.20, 0.15, 0.10, 0.07, 0.03, 0.02],
            "normal": [0.15, 0.22, 0.22, 0.18, 0.12, 0.06, 0.03, 0.01, 0.01],
            "casual": [0.30, 0.30, 0.20, 0.10, 0.05, 0.03, 0.01, 0.005, 0.005],
        }
        num_devices = np.random.choice(range(1, 10), p=device_probs[profile])

        # ── Current Package ──
        pkg_id = select_current_package(profile, num_devices)
        pkg    = packages_lookup[pkg_id]

        # ── HIDDEN: daily_rate ──
        daily_rate_gb = generate_daily_rate(profile, pkg["package_size_gb"], num_devices)

        # ── Renewal Date & Days ──
        days_passed        = random.randint(1, 29)
        days_until_renewal = 30 - days_passed
        renewal_date       = (TODAY + timedelta(days=days_until_renewal)).strftime("%Y-%m-%d")

        # ── Observable Features ──
        usage_so_far_gb, remaining_gb, projected_usage_gb, actual_speed_mbps = \
            compute_observable_features(
                daily_rate_gb, days_passed,
                pkg["package_size_gb"], pkg["speed_mbps"], num_devices
            )

        # ── Target (with dynamic risk) ──
        rec_pkg_id = recommend_package(
            projected_usage_gb,
            pkg_id,
            num_devices,
            packages_df
        )

        is_change = int(rec_pkg_id != pkg_id)

        # ── device_group: للـ EDA والـ analysis ──
        device_group = "small (1-4)" if num_devices <= 4 else "large (5-9)"

        records.append({
            # User & Location
            "user_id":                  user_id,
            "governorate":              gov_name,
            "governorate_code":         gov_code,

            # Current Package
            "current_package_id":       pkg_id,
            "current_package_size_gb":  pkg["package_size_gb"],
            "current_package_price":    pkg["monthly_price"],
            "current_speed_mbps":       pkg["speed_mbps"],

            # Devices
            "number_of_devices":        num_devices,
            "device_group":             device_group,  

            # Observable Features
            "renewal_date":             renewal_date,
            "days_passed":              days_passed,
            "days_until_renewal":       days_until_renewal,
            "usage_so_far_gb":          usage_so_far_gb,
            "remaining_gb":             remaining_gb,
            "projected_usage_gb":       projected_usage_gb,
            "actual_speed_mbps":        actual_speed_mbps,

            # Validation/EDA only
            "user_profile":             profile,

            # Target & helper
            "recommended_package_id":   rec_pkg_id,
            "is_change":                is_change,
        })

    return pd.DataFrame(records)

# ═══════════════════════════════════════════
# 6. RUN & VALIDATE
# ═══════════════════════════════════════════

print("Generating 50,000 rows...")
df = generate_dataset(50000)