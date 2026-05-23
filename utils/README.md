# WE Internet Subscribers — Dataset Generator

Simulates 50,000 WE internet subscribers with realistic usage profiles, package selections, and upgrade recommendations.

---

## Available Packages

| Category | Speed | Size | Price (EGP) |
|----------|-------|------|-------------|
| Super | 30 Mbps | 140 – 1000 GB | 210 – 1360 |
| Mega  | 70 Mbps | 250 – 1000 GB | 530 – 1560 |
| Ultra | 100 Mbps | 250 – 600 GB | 700 – 1230 |
| Max   | 200 Mbps | 1000 GB | 1760 |
| MaxP  | 500 Mbps | 1000 GB | 2000 |

---

## Data Generation Pipeline

### 1 — Governorate
Sampled from 25 Egyptian governorates using real population weights. Cairo, Giza, and Alexandria take the largest share.

### 2 — Usage Profile
Each subscriber gets one of four profiles:

| Profile | Probability | Meaning |
|---------|-------------|---------|
| `over`   | 40% | Consistently exceeds quota |
| `heavy`  | 30% | High but within-quota usage |
| `normal` | 20% | Average usage |
| `casual` | 10% | Light usage |

### 3 — Number of Devices
Sampled per profile. `over` users tend to have more devices connected.

### 4 — Current Package Selection
Two-step process:
1. Pick a **category** (Super / Mega / Ultra / ...) based on profile + device count
2. Pick a **specific package** within that category using internal weights (cheaper = more common)

### 5 — Daily Rate 
An internal variable that drives all observable consumption:
- Derived from a usage percentage range, device count multiplier, and Gaussian noise
- **Not present in the final dataset** — everything else is computed from it

### 6 — Observable Features
Computed from the daily rate:

| Column | Formula |
|--------|---------|
| `usage_so_far_gb` | daily rate × days elapsed |
| `remaining_gb` | package size − usage so far |
| `projected_usage_gb` | (usage ÷ days elapsed) × 30 |
| `actual_speed_mbps` | package speed ÷ √(device count) |

### 7 — Package Recommendation (target)
Scored across three criteria:

| Criterion | Weight |
|-----------|--------|
| Volume fit (package size vs projected usage) | 60% |
| Price (lower is better) | 30% |
| Speed | 10% |

**Decision logic:**
- If `package size ÷ projected usage` is between 0.85 and 1.30 → **keep current package**
- If projected usage > 900 GB → force **STD-5555-1000**
- Otherwise → recommend the highest-scoring package

---

## Final Dataset

Each row represents one subscriber with 20 columns:

```
user_id, governorate, current_package_id, current_package_size_gb,
current_package_price, current_speed_mbps, number_of_devices,
renewal_date, days_passed, days_until_renewal,
usage_so_far_gb, remaining_gb, projected_usage_gb, actual_speed_mbps,
user_profile, recommended_package_id, is_change
```

- `is_change = 1` → recommendation is to switch packages
- `is_change = 0` → current package is a good fit

---
