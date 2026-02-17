import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Braze Migration Risk Model",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Color palette ───────────────────────────────────────────────────────────
COLORS = {
    "red":        "#E63946",
    "red_light":  "#F4A3A8",
    "orange":     "#F77F00",
    "orange_light":"#FCBF49",
    "yellow":     "#EAE2B7",
    "purple":     "#6A4C93",
    "purple_light":"#9D8EC7",
    "dark":       "#264653",
    "dark_mid":   "#457B9D",
    "gray":       "#8D99AE",
    "gray_light": "#EDF2F4",
    "white":      "#FFFFFF",
    "green":      "#2A9D8F",
}

CHART_LAYOUT = dict(
    plot_bgcolor=COLORS["white"],
    paper_bgcolor=COLORS["white"],
    font=dict(family="Inter, -apple-system, sans-serif", size=13, color=COLORS["dark"]),
    margin=dict(t=28, b=40, l=60, r=20),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        font=dict(size=11),
    ),
    xaxis=dict(gridcolor=COLORS["gray_light"], zeroline=False),
    yaxis=dict(gridcolor=COLORS["gray_light"], zeroline=False),
)

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Base */
    html, body, [class*="stApp"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: {COLORS["gray_light"]};
        border-right: 1px solid #ddd;
    }}
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stNumberInput label {{
        font-size: 0.82rem;
        font-weight: 500;
        color: {COLORS["dark"]};
    }}

    /* Metric cards */
    .hero-card {{
        background: {COLORS["white"]};
        border: 1px solid #e0e0e0;
        border-radius: 14px;
        padding: 24px 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        height: 100%;
    }}
    .hero-value {{
        font-size: 1.85rem;
        font-weight: 700;
        margin: 6px 0 2px 0;
        line-height: 1.15;
    }}
    .hero-label {{
        font-size: 0.72rem;
        font-weight: 600;
        color: {COLORS["gray"]};
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}
    .hero-sub {{
        font-size: 0.75rem;
        color: {COLORS["gray"]};
        margin-top: 4px;
    }}
    .text-red   {{ color: {COLORS["red"]}; }}
    .text-green {{ color: {COLORS["green"]}; }}
    .text-dark  {{ color: {COLORS["dark"]}; }}

    /* Decision badge */
    .decision-badge {{
        display: inline-block;
        padding: 12px 28px;
        border-radius: 10px;
        font-size: 0.95rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-top: 8px;
    }}
    .badge-extend {{
        background: #D8F3DC; color: #1B4332; border: 2px solid {COLORS["green"]};
    }}
    .badge-migrate {{
        background: #D1ECF1; color: #0C5460; border: 2px solid {COLORS["dark_mid"]};
    }}

    /* Section headers */
    .section-num {{
        display: inline-block;
        background: {COLORS["dark"]};
        color: white;
        width: 28px; height: 28px;
        border-radius: 50%;
        text-align: center;
        line-height: 28px;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 8px;
        vertical-align: middle;
    }}
    .section-title {{
        font-size: 1.2rem;
        font-weight: 700;
        color: {COLORS["dark"]};
        vertical-align: middle;
    }}
    .section-desc {{
        font-size: 0.83rem;
        color: {COLORS["gray"]};
        margin: 4px 0 20px 36px;
        line-height: 1.5;
    }}

    /* Tables */
    .clean-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
        margin: 12px 0;
    }}
    .clean-table th {{
        text-align: left;
        padding: 8px 12px;
        border-bottom: 2px solid {COLORS["dark"]};
        font-weight: 600;
        color: {COLORS["dark"]};
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }}
    .clean-table td {{
        padding: 7px 12px;
        border-bottom: 1px solid #eee;
        color: {COLORS["dark"]};
    }}
    .clean-table tr:last-child td {{
        border-bottom: 2px solid {COLORS["dark"]};
        font-weight: 600;
    }}
    .clean-table .num {{ text-align: right; font-variant-numeric: tabular-nums; }}

    /* Hide streamlit default metric styling tweaks */
    div[data-testid="stMetricValue"] {{ font-size: 1.1rem; }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin-bottom: 4px;">
    <span style="font-size: 2rem; font-weight: 700; color: {COLORS['dark']};">Braze Migration</span>
    <span style="font-size: 2rem; font-weight: 300; color: {COLORS['gray']};">  Risk & Cost Model</span>
</div>
<div style="font-size: 0.9rem; color: {COLORS['gray']}; margin-bottom: 8px;">
    What is the expected cost of a failed IP warmup vs. the cost of extending Iterable as a safety net?
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"<div style='font-weight:700; font-size:1.05rem; color:{COLORS['dark']}; margin-bottom:12px;'>Model Inputs</div>", unsafe_allow_html=True)

    st.markdown(f"<div style='font-weight:600; font-size:0.82rem; color:{COLORS['gray']}; text-transform:uppercase; letter-spacing:0.05em; margin:16px 0 8px 0;'>Core Assumptions</div>", unsafe_allow_html=True)

    failure_prob = st.slider(
        "IP Warmup Failure Probability",
        min_value=0, max_value=100, value=50, step=5,
        help="Likelihood that IP warmup fails and emails hit spam"
    ) / 100

    recovery_months = st.slider(
        "Recovery Window (months)",
        min_value=1, max_value=6, value=3, step=1,
        help="Months to recover from a failed warmup"
    )

    iterable_cost = st.number_input(
        "Iterable Extension Cost ($)",
        min_value=0, max_value=50_000_000, value=500_000, step=100_000,
        help="Cost to keep Iterable running in parallel"
    )

    arpu = st.number_input(
        "ARPU ($/month)", min_value=1.0, max_value=100.0, value=30.0, step=1.0
    )

    st.markdown(f"<div style='font-weight:600; font-size:0.82rem; color:{COLORS['gray']}; text-transform:uppercase; letter-spacing:0.05em; margin:20px 0 4px 0;'>1 · Signup Depression</div>", unsafe_allow_html=True)
    st.caption("How much signup volume drops during failure. 1.0 = no impact.")

    in_signup_depression = st.slider(
        "IN Signups", min_value=0.0, max_value=1.0, value=0.95, step=0.05, format="%.2f",
        help="IN signups are heavily email-dependent (drip campaigns, reminders)",
        key="in_signup"
    )
    oon_embed_signup_depression = st.slider(
        "OON / Embed Signups", min_value=0.0, max_value=1.0, value=1.0, step=0.05, format="%.2f",
        help="OON from performance marketing; Embed from partner flows — minimal email dependency",
        key="oon_signup"
    )

    st.markdown(f"<div style='font-weight:600; font-size:0.82rem; color:{COLORS['gray']}; text-transform:uppercase; letter-spacing:0.05em; margin:20px 0 4px 0;'>2 · Activation Depression</div>", unsafe_allow_html=True)
    st.caption("Post-signup email nudges affect ALL channels.")

    m0_activation_base = st.slider(
        "M0 Activation Rate (baseline)", min_value=0.50, max_value=0.80, value=0.6512,
        step=0.01, format="%.2f", key="m0_base"
    )
    m1_plus_uplift = st.slider(
        "M1+ Uplift (pp)", min_value=0.0, max_value=0.25, value=0.12,
        step=0.01, format="%.2f", help="Email-driven late activation uplift", key="m1_uplift"
    )
    m0_depression = st.slider(
        "M0 Depression (all channels)", min_value=0.0, max_value=1.0, value=0.95,
        step=0.05, format="%.2f", key="m0_dep"
    )
    m1_plus_depression = st.slider(
        "M1+ Depression (all channels)", min_value=0.0, max_value=1.0, value=0.95,
        step=0.05, format="%.2f", help="Nurture emails are the primary late-activation driver", key="m1_dep"
    )

    st.markdown(f"<div style='font-weight:600; font-size:0.82rem; color:{COLORS['gray']}; text-transform:uppercase; letter-spacing:0.05em; margin:20px 0 4px 0;'>3 · Rescue Depression</div>", unsafe_allow_html=True)
    st.caption("Rescue emails target ALL users regardless of signup channel.")

    active_rescue_depression = st.slider(
        "Active Rescue", min_value=0.0, max_value=1.0, value=0.95,
        step=0.05, format="%.2f", key="active_dep"
    )
    inactive_rescue_depression = st.slider(
        "Inactive Rescue", min_value=0.0, max_value=1.0, value=0.95,
        step=0.05, format="%.2f", help="Win-back emails are ~100% of the inactive rescue lever",
        key="inactive_dep"
    )

    st.markdown(f"<div style='font-weight:600; font-size:0.82rem; color:{COLORS['gray']}; text-transform:uppercase; letter-spacing:0.05em; margin:20px 0 4px 0;'>4 · Repeat Rate</div>", unsafe_allow_html=True)
    st.caption("~70% autopay — only ~30% manual-pay users are email-sensitive. SMS/push still active.")

    repeat_depression_bps = st.slider(
        "Repeat Rate Depression (bps)",
        min_value=0, max_value=200, value=50, step=10,
        help="Basis point drop in repeat rate. 50 bps = 0.50pp (85.3% → 84.8%)",
        key="repeat_dep"
    )


# ═══════════════════════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════════════════════
months_all = ["Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
in_signups_all = [90763, 87470, 89865, 90257, 94113, 99681, 103436, 113150, 112419, 106892, 102895]
oon_embed_signups_all = [44133, 42530, 43694, 43884, 45760, 48466, 50292, 55015, 54659, 51971, 50028]

migration_idx = 3  # May
model_months = months_all[migration_idx : migration_idx + recovery_months]
in_signups_model = in_signups_all[migration_idx : migration_idx + recovery_months]
oon_embed_signups_model = oon_embed_signups_all[migration_idx : migration_idx + recovery_months]

while len(model_months) < recovery_months:
    model_months.append(f"M+{len(model_months)}")
    in_signups_model.append(in_signups_model[-1])
    oon_embed_signups_model.append(oon_embed_signups_model[-1])

total_signups_model = [i + o for i, o in zip(in_signups_model, oon_embed_signups_model)]

active_users_feb = 303809
inactive_users_feb = 1_120_177
active_rescue_rate = 0.2591
inactive_rescue_rate = 0.0113

# Repeat rate data
repeat_rates_6mo = [0.8632, 0.8503, 0.8687, 0.8360, 0.8473, 0.8521]  # Feb–Sep 2025 trailing 6mo
repeat_rate_base = sum(repeat_rates_6mo) / len(repeat_rates_6mo)       # ~85.29%
bp_prev_month_feb = 1_100_855  # Feb 2026 actual

def grow(base, months_from_feb, rate=0.03):
    return base * (1 + rate) ** months_from_feb


# ═══════════════════════════════════════════════════════════════════════════
# MODEL
# ═══════════════════════════════════════════════════════════════════════════
def compute_monthly_impact(mi, in_signup, oon_embed_signup):
    rp = 0.0 if recovery_months == 1 else mi / recovery_months

    eff_in_signup = in_signup_depression + (1.0 - in_signup_depression) * rp
    eff_oon_signup = oon_embed_signup_depression + (1.0 - oon_embed_signup_depression) * rp
    eff_m0 = m0_depression + (1.0 - m0_depression) * rp
    eff_m1 = m1_plus_depression + (1.0 - m1_plus_depression) * rp
    eff_active_rescue = active_rescue_depression + (1.0 - active_rescue_depression) * rp
    eff_inactive_rescue = inactive_rescue_depression + (1.0 - inactive_rescue_depression) * rp

    in_signup_loss = in_signup * (eff_in_signup - 1)
    oon_signup_loss = oon_embed_signup * (eff_oon_signup - 1)
    eff_in_signups = in_signup * eff_in_signup
    eff_oon_signups = oon_embed_signup * eff_oon_signup

    in_m0_loss = eff_in_signups * m0_activation_base * eff_m0 - in_signup * m0_activation_base
    oon_m0_loss = eff_oon_signups * m0_activation_base * eff_m0 - oon_embed_signup * m0_activation_base
    in_m1_loss = eff_in_signups * m1_plus_uplift * eff_m1 - in_signup * m1_plus_uplift
    oon_m1_loss = eff_oon_signups * m1_plus_uplift * eff_m1 - oon_embed_signup * m1_plus_uplift

    months_from_feb = migration_idx + mi
    active_base = grow(active_users_feb, months_from_feb)
    active_rescue_loss = active_base * active_rescue_rate * (eff_active_rescue - 1)
    inactive_base = grow(inactive_users_feb, months_from_feb)
    inactive_rescue_loss = inactive_base * inactive_rescue_rate * (eff_inactive_rescue - 1)

    return {
        "month": model_months[mi],
        "in_signup_loss": in_signup_loss, "oon_signup_loss": oon_signup_loss,
        "total_signup_loss": in_signup_loss + oon_signup_loss,
        "in_m0_loss": in_m0_loss, "oon_m0_loss": oon_m0_loss,
        "in_m1_loss": in_m1_loss, "oon_m1_loss": oon_m1_loss,
        "total_activation_loss": in_m0_loss + oon_m0_loss + in_m1_loss + oon_m1_loss,
        "active_rescue_loss": active_rescue_loss, "inactive_rescue_loss": inactive_rescue_loss,
        "total_rescue_loss": active_rescue_loss + inactive_rescue_loss,
        "eff_in_signup": eff_in_signup, "eff_oon_signup": eff_oon_signup,
        "eff_m0": eff_m0, "eff_m1": eff_m1,
        "eff_active_rescue": eff_active_rescue, "eff_inactive_rescue": eff_inactive_rescue,
        "in_signup": in_signup, "oon_signup": oon_embed_signup,
    }

results = [compute_monthly_impact(i, in_signups_model[i], oon_embed_signups_model[i])
           for i in range(recovery_months)]
df = pd.DataFrame(results)

# ── Repeat Rate Model ────────────────────────────────────────────────────────
repeat_losses = []
for mi in range(recovery_months):
    rp = 0.0 if recovery_months == 1 else mi / recovery_months
    eff_dep_bps = repeat_depression_bps * (1.0 - rp)
    months_from_feb = migration_idx + mi
    bp_prev = bp_prev_month_feb * (1.03 ** months_from_feb)
    lost = bp_prev * (eff_dep_bps / 10000)
    repeat_losses.append({
        "repeat_bp_loss": -lost,
        "bp_prev_month": bp_prev,
        "eff_repeat_dep_bps": eff_dep_bps,
        "eff_repeat_ratio": 1.0 - (eff_dep_bps / 10000) / repeat_rate_base,
    })
df_rpt = pd.DataFrame(repeat_losses)
for col in df_rpt.columns:
    df[col] = df_rpt[col].values

total_activation_bp_loss = df["total_activation_loss"].sum()
total_active_rescue_loss = df["active_rescue_loss"].sum()
total_inactive_rescue_loss = df["inactive_rescue_loss"].sum()
total_rescue_bp_loss = df["total_rescue_loss"].sum()
total_repeat_bp_loss = df["repeat_bp_loss"].sum()
total_bp_loss = total_activation_bp_loss + total_rescue_bp_loss + total_repeat_bp_loss

# ── Retention curves & LTV multipliers ──────────────────────────────────────
# Activation: avg of Apr–Jun 2024 cohorts with 12mo data (M0–M12)
ACTIVATION_RETENTION = [1.0, 0.751, 0.662, 0.611, 0.574, 0.543, 0.513, 0.486, 0.465, 0.449, 0.435, 0.420, 0.400]
# Active rescue retention (M0–M12)
ACTIVE_RESCUE_RETENTION = [1.0, 0.6554, 0.5387, 0.4640, 0.3806, 0.3220, 0.2861, 0.2661, 0.2461, 0.2261, 0.2061, 0.1861, 0.1661]
# Inactive rescue retention (M0–M12)
INACTIVE_RESCUE_RETENTION = [1.0, 0.6844, 0.5544, 0.4706, 0.4055, 0.3625, 0.3180, 0.2980, 0.2780, 0.2580, 0.2380, 0.2180, 0.1980]

LTV_MULT_ACT = sum(ACTIVATION_RETENTION)              # ~7.31
LTV_MULT_ACTIVE_RESC = sum(ACTIVE_RESCUE_RETENTION)    # ~4.95
LTV_MULT_INACTIVE_RESC = sum(INACTIVE_RESCUE_RETENTION) # ~5.28

# Repeat rate uses activation retention curve as LTV proxy (existing retained users)
LTV_MULT_REPEAT = LTV_MULT_ACT

# ── Three revenue views ─────────────────────────────────────────────────────
rev_in_month = abs(total_bp_loss) * arpu
rev_ltv = (abs(total_activation_bp_loss) * arpu * LTV_MULT_ACT +
           abs(total_active_rescue_loss) * arpu * LTV_MULT_ACTIVE_RESC +
           abs(total_inactive_rescue_loss) * arpu * LTV_MULT_INACTIVE_RESC +
           abs(total_repeat_bp_loss) * arpu * LTV_MULT_REPEAT)
# Per-metric LTV revenue (for section tables)
act_rev_ltv = abs(total_activation_bp_loss) * arpu * LTV_MULT_ACT
active_resc_rev_ltv = abs(total_active_rescue_loss) * arpu * LTV_MULT_ACTIVE_RESC
inactive_resc_rev_ltv = abs(total_inactive_rescue_loss) * arpu * LTV_MULT_INACTIVE_RESC
repeat_rev_ltv = abs(total_repeat_bp_loss) * arpu * LTV_MULT_REPEAT

# Decision uses LTV as primary
revenue_impact_if_failure = rev_ltv
expected_revenue_impact = revenue_impact_if_failure * failure_prob
expected_in_month_impact = rev_in_month * failure_prob
net_value_of_extension = abs(expected_revenue_impact) - iterable_cost


# ═══════════════════════════════════════════════════════════════════════════
# TOP-LINE: REVENUE IMPACT IF FAILURE
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown(f"<div style='font-size:0.78rem; font-weight:600; color:{COLORS['gray']}; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:10px;'>If Failure Occurs — Total Revenue Impact ({recovery_months}mo window)</div>", unsafe_allow_html=True)

rv1, rv2 = st.columns(2)
with rv1:
    st.markdown(f"""<div class="hero-card">
        <div class="hero-label">In-Month Revenue Lost</div>
        <div class="hero-value text-dark">-${rev_in_month:,.0f}</div>
        <div class="hero-sub">BPs lost &times; ${arpu:.0f} ARPU, summed over {recovery_months}mo</div>
    </div>""", unsafe_allow_html=True)
with rv2:
    st.markdown(f"""<div class="hero-card" style="border: 2px solid {COLORS['dark']};">
        <div class="hero-label">LTV-Weighted Revenue Lost</div>
        <div class="hero-value text-red">-${rev_ltv:,.0f}</div>
        <div class="hero-sub">Uses 12-month retention curves per metric type</div>
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# EXPECTED VALUE ROW (probability-weighted)
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
st.markdown(f"<div style='font-size:0.78rem; font-weight:600; color:{COLORS['gray']}; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:10px;'>Probability-Weighted Expected Impact ({failure_prob:.0%} failure rate)</div>", unsafe_allow_html=True)

e1, e2 = st.columns(2)
with e1:
    st.markdown(f"""<div class="hero-card">
        <div class="hero-label">Expected In-Month Revenue at Risk</div>
        <div class="hero-value text-dark">${abs(expected_in_month_impact):,.0f}</div>
        <div class="hero-sub">{failure_prob:.0%} prob &times; ${rev_in_month:,.0f} in-month impact</div>
    </div>""", unsafe_allow_html=True)
with e2:
    st.markdown(f"""<div class="hero-card">
        <div class="hero-label">Expected LTV Revenue at Risk</div>
        <div class="hero-value text-red">${abs(expected_revenue_impact):,.0f}</div>
        <div class="hero-sub">{failure_prob:.0%} prob &times; ${rev_ltv:,.0f} LTV impact</div>
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# DECISION ROW
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1.1, 1.1, 0.8])

with c1:
    st.markdown(f"""<div class="hero-card">
        <div class="hero-label">Iterable Extension Cost</div>
        <div class="hero-value text-dark">${iterable_cost:,.0f}</div>
        <div class="hero-sub">Cost to keep as safety net</div>
    </div>""", unsafe_allow_html=True)

with c2:
    val_color = "text-green" if net_value_of_extension > 0 else "text-red"
    st.markdown(f"""<div class="hero-card">
        <div class="hero-label">Net Value of Extending</div>
        <div class="hero-value {val_color}">${net_value_of_extension:,.0f}</div>
        <div class="hero-sub">Expected LTV risk &minus; extension cost</div>
    </div>""", unsafe_allow_html=True)

with c3:
    if net_value_of_extension > 0:
        st.markdown("""<div class="hero-card" style="display:flex;align-items:center;justify-content:center;">
            <div class="decision-badge badge-extend">Extend<br>Iterable</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="hero-card" style="display:flex;align-items:center;justify-content:center;">
            <div class="decision-badge badge-migrate">Proceed with<br>Migration</div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# BREAKEVEN
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)
st.markdown(f"<div style='font-size:1.15rem; font-weight:700; color:{COLORS['dark']};'>Breakeven Analysis</div>", unsafe_allow_html=True)
st.markdown(f"<div style='font-size:0.83rem; color:{COLORS['gray']}; margin-bottom:16px;'>At what failure probability does the Iterable extension pay for itself?</div>", unsafe_allow_html=True)

breakeven_prob_ltv = iterable_cost / rev_ltv if rev_ltv != 0 else 1.0

be1, be2, be3 = st.columns(3)
with be1:
    st.metric("Breakeven Probability (LTV)", f"{min(breakeven_prob_ltv, 1.0):.0%}")
with be2:
    st.metric("Your Assumption", f"{failure_prob:.0%}")
with be3:
    pass

probs = np.arange(0, 1.01, 0.05)

fig_be = go.Figure()
fig_be.add_trace(go.Scatter(
    x=probs, y=[p * rev_ltv for p in probs], mode="lines", name="LTV-Weighted",
    line=dict(color=COLORS["red"], width=3)
))
fig_be.add_hline(y=iterable_cost, line_dash="dash", line_color=COLORS["green"], line_width=2.5,
                  annotation_text=f"Iterable: ${iterable_cost/1e6:.1f}M",
                  annotation_position="top right",
                  annotation_font=dict(size=12, color=COLORS["green"]))
fig_be.add_vline(x=failure_prob, line_dash="dot", line_color=COLORS["purple"],
                  annotation_text=f"Current: {failure_prob:.0%}",
                  annotation_position="top left",
                  annotation_font=dict(size=12, color=COLORS["purple"]))
if 0 < breakeven_prob_ltv <= 1.0:
    fig_be.add_vline(x=breakeven_prob_ltv, line_dash="dash", line_color=COLORS["green"],
                      annotation_text=f"Breakeven: {breakeven_prob_ltv:.0%}",
                      annotation_position="bottom right",
                      annotation_font=dict(size=12, color=COLORS["green"]))
fig_be.update_layout(
    **CHART_LAYOUT,
    xaxis_title="Failure Probability", yaxis_title="Expected Revenue Impact ($)",
    xaxis_tickformat=".0%", yaxis_tickprefix="$", yaxis_tickformat=",",
    height=340,
)
st.plotly_chart(fig_be, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# IMPACT SUMMARY
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
st.markdown(f"<div style='font-size:1.15rem; font-weight:700; color:{COLORS['dark']};'>If Failure Occurs — Impact by Email Metric</div>", unsafe_allow_html=True)
st.markdown(f"<div style='font-size:0.83rem; color:{COLORS['gray']}; margin-bottom:16px;'>Cumulative impact across {recovery_months}-month recovery window. Not probability-weighted.</div>", unsafe_allow_html=True)

total_in_signup_loss = abs(df["in_signup_loss"].sum())
total_oon_signup_loss = abs(df["oon_signup_loss"].sum())
total_signup_loss_count = total_in_signup_loss + total_oon_signup_loss
total_act_loss = abs(total_activation_bp_loss)
total_resc_loss = abs(total_rescue_bp_loss)

s1, s2, s3, s4, s5 = st.columns(5)
with s1:
    st.metric("Signups Lost", f"{total_signup_loss_count:,.0f}",
              delta=f"IN {total_in_signup_loss:,.0f} · OON {total_oon_signup_loss:,.0f}", delta_color="off")
with s2:
    st.metric("Activation BPs Lost", f"{total_act_loss:,.0f}",
              delta=f"LTV: -${act_rev_ltv:,.0f}", delta_color="off")
with s3:
    resc_rev_ltv = active_resc_rev_ltv + inactive_resc_rev_ltv
    st.metric("Rescue BPs Lost", f"{total_resc_loss:,.0f}",
              delta=f"LTV: -${resc_rev_ltv:,.0f}", delta_color="off")
with s4:
    total_rpt_loss = abs(total_repeat_bp_loss)
    st.metric("Repeat BPs Lost", f"{total_rpt_loss:,.0f}",
              delta=f"LTV: -${repeat_rev_ltv:,.0f}", delta_color="off")
with s5:
    st.metric(f"Total LTV Impact ({recovery_months}mo)",
              f"-${rev_ltv:,.0f}",
              delta=f"In-month: -${rev_in_month:,.0f}", delta_color="off")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: SIGNUPS
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:32px; border-top:1px solid #e0e0e0; margin-top:24px;'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div>
    <span class="section-num">1</span>
    <span class="section-title">Signups — IN vs. OON/Embed</span>
</div>
<div class="section-desc">
    IN signups are heavily email-dependent (reminders, drip campaigns).
    OON comes from performance marketing; Embed comes through partner flows — both have minimal email dependency for signup.
</div>
""", unsafe_allow_html=True)

sig1, sig2 = st.columns([3, 2])

with sig1:
    fig_signups = go.Figure()
    fig_signups.add_trace(go.Bar(
        name="IN — Baseline", x=df["month"], y=df["in_signup"],
        marker_color=COLORS["dark_mid"], opacity=0.35
    ))
    fig_signups.add_trace(go.Bar(
        name="IN — Impaired", x=df["month"], y=df["in_signup"] * df["eff_in_signup"],
        marker_color=COLORS["red"]
    ))
    fig_signups.add_trace(go.Bar(
        name="OON/Embed — Baseline", x=df["month"], y=df["oon_signup"],
        marker_color=COLORS["orange_light"], opacity=0.45
    ))
    fig_signups.add_trace(go.Bar(
        name="OON/Embed — Impaired", x=df["month"], y=df["oon_signup"] * df["eff_oon_signup"],
        marker_color=COLORS["orange"]
    ))
    fig_signups.update_layout(
        **CHART_LAYOUT, barmode="group",
        yaxis_title="Signups", yaxis_tickformat=",", height=360,
    )
    st.plotly_chart(fig_signups, use_container_width=True)

with sig2:
    rows_html = ""
    for _, row in df.iterrows():
        in_pct = (1 - row["eff_in_signup"]) * 100
        oon_pct = (1 - row["eff_oon_signup"]) * 100
        rows_html += f"""<tr>
            <td>{row['month']}</td>
            <td class="num" style="color:{COLORS['red']}">-{in_pct:.0f}%</td>
            <td class="num">{abs(row['in_signup_loss']):,.0f}</td>
            <td class="num" style="color:{COLORS['orange']}">-{oon_pct:.0f}%</td>
            <td class="num">{abs(row['oon_signup_loss']):,.0f}</td>
        </tr>"""

    st.markdown(f"""
    <table class="clean-table">
        <tr><th></th><th colspan="2" style="text-align:center;">IN</th><th colspan="2" style="text-align:center;">OON / Embed</th></tr>
        <tr><th>Month</th><th class="num">Drop</th><th class="num">Lost</th><th class="num">Drop</th><th class="num">Lost</th></tr>
        {rows_html}
    </table>
    """, unsafe_allow_html=True)

    st.markdown(f"<div style='font-size:0.8rem; color:{COLORS['gray']}; margin-top:12px; line-height:1.5;'>Email drives the IN signup funnel — confirmation emails, onboarding drips, reminders. OON enters via paid ads/landing pages; Embed through partner integrations.</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: ACTIVATION
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:32px; border-top:1px solid #e0e0e0; margin-top:24px;'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div>
    <span class="section-num">2</span>
    <span class="section-title">Activation — M0 + M1+ (All Channels)</span>
</div>
<div class="section-desc">
    Post-signup email nudges drive activation across ALL channels.
    Impact compounds: fewer signups &times; lower activation rate = multiplicative BP loss.
</div>
""", unsafe_allow_html=True)

act1, act2 = st.columns([1.2, 1])

with act1:
    fig_act = go.Figure()
    fig_act.add_trace(go.Bar(name="IN — M0", x=df["month"], y=df["in_m0_loss"].abs(), marker_color=COLORS["red"]))
    fig_act.add_trace(go.Bar(name="IN — M1+", x=df["month"], y=df["in_m1_loss"].abs(), marker_color=COLORS["red_light"]))
    fig_act.add_trace(go.Bar(name="OON/Embed — M0", x=df["month"], y=df["oon_m0_loss"].abs(), marker_color=COLORS["orange"]))
    fig_act.add_trace(go.Bar(name="OON/Embed — M1+", x=df["month"], y=df["oon_m1_loss"].abs(), marker_color=COLORS["orange_light"]))
    fig_act.update_layout(
        **CHART_LAYOUT, barmode="stack",
        yaxis_title="BPs Lost", yaxis_tickformat=",", height=380,
    )
    st.plotly_chart(fig_act, use_container_width=True)

with act2:
    total_act_rate = m0_activation_base + m1_plus_uplift
    signup_effect_bps = 0
    activation_effect_bps = 0
    for _, row in df.iterrows():
        in_base, oon_base = row["in_signup"], row["oon_signup"]
        in_eff = in_base * row["eff_in_signup"]
        oon_eff = oon_base * row["eff_oon_signup"]
        signup_effect_bps += ((in_eff - in_base) + (oon_eff - oon_base)) * total_act_rate
        eff_act = m0_activation_base * row["eff_m0"] + m1_plus_uplift * row["eff_m1"]
        activation_effect_bps += (in_base + oon_base) * (eff_act - total_act_rate)
    interaction_bps = total_activation_bp_loss - signup_effect_bps - activation_effect_bps

    st.markdown(f"""
    <div style="font-size:0.88rem; font-weight:600; color:{COLORS['dark']}; margin-bottom:8px;">Impact decomposition</div>
    <table class="clean-table">
        <tr><th>Driver</th><th class="num">BPs Lost</th><th class="num">LTV Revenue ({LTV_MULT_ACT:.1f}×)</th></tr>
        <tr><td>Fewer signups (volume)</td><td class="num">{abs(signup_effect_bps):,.0f}</td><td class="num">-${abs(signup_effect_bps) * arpu * LTV_MULT_ACT:,.0f}</td></tr>
        <tr><td>Lower activation rate</td><td class="num">{abs(activation_effect_bps):,.0f}</td><td class="num">-${abs(activation_effect_bps) * arpu * LTV_MULT_ACT:,.0f}</td></tr>
        <tr><td>Compounding interaction</td><td class="num">{abs(interaction_bps):,.0f}</td><td class="num">-${abs(interaction_bps) * arpu * LTV_MULT_ACT:,.0f}</td></tr>
        <tr><td><strong>Total</strong></td><td class="num"><strong>{abs(total_activation_bp_loss):,.0f}</strong></td><td class="num"><strong>-${act_rev_ltv:,.0f}</strong></td></tr>
    </table>
    <div style="font-size:0.8rem; color:{COLORS['gray']}; margin-top:12px; line-height:1.5;">
        LTV multiplier ({LTV_MULT_ACT:.1f}×) = sum of 12-month retention curve.
        A lost BP today costs ~${arpu * LTV_MULT_ACT:.0f} in lifetime revenue, not just ${arpu:.0f}.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: RESCUE
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:32px; border-top:1px solid #e0e0e0; margin-top:24px;'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div>
    <span class="section-num">3</span>
    <span class="section-title">Rescue — Active + Inactive Users</span>
</div>
<div class="section-desc">
    Rescue emails target ALL users regardless of original signup channel.
    Active users get nudges to maintain BPs; inactive users get win-back campaigns.
</div>
""", unsafe_allow_html=True)

res1, res2 = st.columns([1.2, 1])

with res1:
    fig_rescue = go.Figure()
    fig_rescue.add_trace(go.Bar(name="Active Rescue", x=df["month"], y=df["active_rescue_loss"].abs(), marker_color=COLORS["red"]))
    fig_rescue.add_trace(go.Bar(name="Inactive Rescue", x=df["month"], y=df["inactive_rescue_loss"].abs(), marker_color=COLORS["gray"]))
    fig_rescue.update_layout(
        **CHART_LAYOUT, barmode="stack",
        yaxis_title="BPs Lost", yaxis_tickformat=",", height=360,
    )
    st.plotly_chart(fig_rescue, use_container_width=True)

with res2:
    total_active_loss = abs(df["active_rescue_loss"].sum())
    total_inactive_loss = abs(df["inactive_rescue_loss"].sum())

    st.markdown(f"""
    <div style="font-size:0.88rem; font-weight:600; color:{COLORS['dark']}; margin-bottom:8px;">Rescue by segment</div>
    <table class="clean-table">
        <tr><th>Segment</th><th class="num">BPs Lost</th><th class="num">LTV Revenue</th></tr>
        <tr><td>Active ({LTV_MULT_ACTIVE_RESC:.1f}× mult)</td><td class="num">{total_active_loss:,.0f}</td><td class="num">-${active_resc_rev_ltv:,.0f}</td></tr>
        <tr><td>Inactive ({LTV_MULT_INACTIVE_RESC:.1f}× mult)</td><td class="num">{total_inactive_loss:,.0f}</td><td class="num">-${inactive_resc_rev_ltv:,.0f}</td></tr>
        <tr><td><strong>Total</strong></td><td class="num"><strong>{total_active_loss + total_inactive_loss:,.0f}</strong></td><td class="num"><strong>-${active_resc_rev_ltv + inactive_resc_rev_ltv:,.0f}</strong></td></tr>
    </table>
    <div style="font-size:0.8rem; color:{COLORS['gray']}; margin-top:12px; line-height:1.5;">
        Active rescue: {active_rescue_rate:.1%} rate, ~{LTV_MULT_ACTIVE_RESC:.1f}mo retention &rarr; ~${arpu * LTV_MULT_ACTIVE_RESC:.0f}/BP.
        Inactive rescue: {inactive_rescue_rate:.2%} rate, ~{LTV_MULT_INACTIVE_RESC:.1f}mo retention &rarr; ~${arpu * LTV_MULT_INACTIVE_RESC:.0f}/BP.
        Win-back emails are the <em>only</em> channel for inactive rescue.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: REPEAT RATE
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:32px; border-top:1px solid #e0e0e0; margin-top:24px;'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div>
    <span class="section-num">4</span>
    <span class="section-title">Repeat Rate — Existing Bill-Paid Users</span>
</div>
<div class="section-desc">
    ~70% of users are on autopay and unaffected by email disruption.
    The remaining ~30% on manual pay rely partly on email reminders — but SMS and push notifications still function.
    Impact is measured in basis points of repeat rate decline.
</div>
""", unsafe_allow_html=True)

rpt1, rpt2 = st.columns([1.2, 1])

with rpt1:
    fig_rpt = go.Figure()
    fig_rpt.add_trace(go.Bar(
        name="Baseline Repeats",
        x=df["month"],
        y=df["bp_prev_month"] * repeat_rate_base,
        marker_color=COLORS["dark_mid"], opacity=0.35,
    ))
    fig_rpt.add_trace(go.Bar(
        name="Impaired Repeats",
        x=df["month"],
        y=df["bp_prev_month"] * (repeat_rate_base - df["eff_repeat_dep_bps"] / 10000),
        marker_color=COLORS["purple"],
    ))
    fig_rpt.update_layout(
        **CHART_LAYOUT, barmode="group",
        yaxis_title="Repeating Users", yaxis_tickformat=",", height=360,
    )
    st.plotly_chart(fig_rpt, use_container_width=True)

with rpt2:
    total_rpt_loss = abs(total_repeat_bp_loss)
    rows_rpt = ""
    for _, row in df.iterrows():
        dep_bps = row["eff_repeat_dep_bps"]
        lost = abs(row["repeat_bp_loss"])
        rows_rpt += f"""<tr>
            <td>{row['month']}</td>
            <td class="num">{row['bp_prev_month']:,.0f}</td>
            <td class="num" style="color:{COLORS['purple']}">-{dep_bps:.0f} bps</td>
            <td class="num">{lost:,.0f}</td>
        </tr>"""

    st.markdown(f"""
    <div style="font-size:0.88rem; font-weight:600; color:{COLORS['dark']}; margin-bottom:8px;">Monthly breakdown</div>
    <table class="clean-table">
        <tr><th>Month</th><th class="num">BP Prev Mo</th><th class="num">Depression</th><th class="num">BPs Lost</th></tr>
        {rows_rpt}
    </table>

    <div style="font-size:0.88rem; font-weight:600; color:{COLORS['dark']}; margin:16px 0 8px 0;">Revenue impact (LTV, {LTV_MULT_REPEAT:.1f}× mult)</div>
    <table class="clean-table">
        <tr><th></th><th class="num">BPs Lost</th><th class="num">LTV Revenue</th></tr>
        <tr><td><strong>Total</strong></td><td class="num"><strong>{total_rpt_loss:,.0f}</strong></td><td class="num"><strong>-${repeat_rev_ltv:,.0f}</strong></td></tr>
    </table>
    <div style="font-size:0.8rem; color:{COLORS['gray']}; margin-top:12px; line-height:1.5;">
        Baseline repeat rate: {repeat_rate_base:.2%} (trailing 6mo avg).
        Depression of {repeat_depression_bps} bps = {repeat_depression_bps/100:.2f}pp.
        Low sensitivity due to autopay dominance.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# RECOVERY CURVE
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:32px; border-top:1px solid #e0e0e0; margin-top:24px;'></div>", unsafe_allow_html=True)
st.markdown(f"<div style='font-size:1.15rem; font-weight:700; color:{COLORS['dark']};'>Recovery Curve</div>", unsafe_allow_html=True)
st.markdown(f"<div style='font-size:0.83rem; color:{COLORS['gray']}; margin-bottom:16px;'>Linear recovery from max depression back to baseline over {recovery_months} months.</div>", unsafe_allow_html=True)

fig_recovery = go.Figure()
traces = [
    ("IN Signup",       "eff_in_signup",       COLORS["red"],          "solid"),
    ("OON/Embed Signup","eff_oon_signup",       COLORS["orange"],       "solid"),
    ("M0 Activation",   "eff_m0",              COLORS["purple"],       "dash"),
    ("M1+ Activation",  "eff_m1",              COLORS["purple_light"], "dash"),
    ("Active Rescue",   "eff_active_rescue",   COLORS["dark"],         "dot"),
    ("Inactive Rescue", "eff_inactive_rescue", COLORS["gray"],         "dot"),
    ("Repeat Rate",     "eff_repeat_ratio",    COLORS["purple"],       "dashdot"),
]
for name, col, color, dash in traces:
    fig_recovery.add_trace(go.Scatter(
        x=df["month"], y=df[col], mode="lines+markers", name=name,
        line=dict(color=color, width=2.5, dash=dash),
        marker=dict(size=7),
    ))
fig_recovery.add_hline(y=1.0, line_dash="dash", line_color=COLORS["green"], line_width=1.5,
                        annotation_text="Baseline", annotation_position="top right",
                        annotation_font=dict(size=11, color=COLORS["green"]))
fig_recovery.update_layout(
    **CHART_LAYOUT,
    yaxis_title="Performance vs. Baseline", yaxis_range=[0, 1.12],
    yaxis_tickformat=".0%", height=380,
)
st.plotly_chart(fig_recovery, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# MONTHLY DETAIL
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:32px; border-top:1px solid #e0e0e0; margin-top:24px;'></div>", unsafe_allow_html=True)

with st.expander("Monthly Detail Table"):
    detail_rows = ""
    totals = {"in_su": 0, "oon_su": 0, "su": 0, "in_m0": 0, "oon_m0": 0,
              "in_m1": 0, "oon_m1": 0, "act": 0, "active_r": 0, "inactive_r": 0,
              "resc": 0, "repeat": 0, "total_bp": 0, "ltv": 0}

    for _, row in df.iterrows():
        in_su = abs(row["in_signup_loss"])
        oon_su = abs(row["oon_signup_loss"])
        su = in_su + oon_su
        in_m0 = abs(row["in_m0_loss"])
        oon_m0 = abs(row["oon_m0_loss"])
        in_m1 = abs(row["in_m1_loss"])
        oon_m1 = abs(row["oon_m1_loss"])
        act = in_m0 + oon_m0 + in_m1 + oon_m1
        active_r = abs(row["active_rescue_loss"])
        inactive_r = abs(row["inactive_rescue_loss"])
        resc = active_r + inactive_r
        rpt = abs(row["repeat_bp_loss"])
        total_bp = act + resc + rpt
        ltv_mo = (act * arpu * LTV_MULT_ACT +
                  active_r * arpu * LTV_MULT_ACTIVE_RESC +
                  inactive_r * arpu * LTV_MULT_INACTIVE_RESC +
                  rpt * arpu * LTV_MULT_REPEAT)

        for k, v in [("in_su", in_su), ("oon_su", oon_su), ("su", su),
                     ("in_m0", in_m0), ("oon_m0", oon_m0), ("in_m1", in_m1), ("oon_m1", oon_m1),
                     ("act", act), ("active_r", active_r), ("inactive_r", inactive_r),
                     ("resc", resc), ("repeat", rpt), ("total_bp", total_bp), ("ltv", ltv_mo)]:
            totals[k] += v

        detail_rows += f"""<tr>
            <td>{row['month']}</td>
            <td class="num">{in_su:,.0f}</td><td class="num">{oon_su:,.0f}</td><td class="num" style="font-weight:600">{su:,.0f}</td>
            <td class="num">{in_m0:,.0f}</td><td class="num">{oon_m0:,.0f}</td>
            <td class="num">{in_m1:,.0f}</td><td class="num">{oon_m1:,.0f}</td><td class="num" style="font-weight:600">{act:,.0f}</td>
            <td class="num">{active_r:,.0f}</td><td class="num">{inactive_r:,.0f}</td><td class="num" style="font-weight:600">{resc:,.0f}</td>
            <td class="num">{rpt:,.0f}</td>
            <td class="num" style="font-weight:700">{total_bp:,.0f}</td>
            <td class="num" style="font-weight:700; color:{COLORS['red']}">-${ltv_mo:,.0f}</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto;">
    <table class="clean-table" style="font-size:0.78rem;">
        <tr>
            <th></th>
            <th colspan="3" style="text-align:center; border-bottom:2px solid {COLORS['dark_mid']};">Signups Lost</th>
            <th colspan="5" style="text-align:center; border-bottom:2px solid {COLORS['red']};">Activation BPs Lost</th>
            <th colspan="3" style="text-align:center; border-bottom:2px solid {COLORS['gray']};">Rescue BPs Lost</th>
            <th style="text-align:center; border-bottom:2px solid {COLORS['purple']};">Repeat</th>
            <th colspan="2" style="text-align:center; border-bottom:2px solid {COLORS['dark']};">Total</th>
        </tr>
        <tr>
            <th>Month</th>
            <th class="num">IN</th><th class="num">OON</th><th class="num">Sub</th>
            <th class="num">IN M0</th><th class="num">OON M0</th>
            <th class="num">IN M1+</th><th class="num">OON M1+</th><th class="num">Sub</th>
            <th class="num">Active</th><th class="num">Inactive</th><th class="num">Sub</th>
            <th class="num">BPs</th>
            <th class="num">BPs Lost</th>
            <th class="num">LTV Rev</th>
        </tr>
        {detail_rows}
        <tr style="background:{COLORS['gray_light']};">
            <td><strong>Total</strong></td>
            <td class="num"><strong>{totals['in_su']:,.0f}</strong></td><td class="num"><strong>{totals['oon_su']:,.0f}</strong></td><td class="num"><strong>{totals['su']:,.0f}</strong></td>
            <td class="num"><strong>{totals['in_m0']:,.0f}</strong></td><td class="num"><strong>{totals['oon_m0']:,.0f}</strong></td>
            <td class="num"><strong>{totals['in_m1']:,.0f}</strong></td><td class="num"><strong>{totals['oon_m1']:,.0f}</strong></td><td class="num"><strong>{totals['act']:,.0f}</strong></td>
            <td class="num"><strong>{totals['active_r']:,.0f}</strong></td><td class="num"><strong>{totals['inactive_r']:,.0f}</strong></td><td class="num"><strong>{totals['resc']:,.0f}</strong></td>
            <td class="num"><strong>{totals['repeat']:,.0f}</strong></td>
            <td class="num" style="font-weight:700">{totals['total_bp']:,.0f}</td>
            <td class="num" style="font-weight:700; color:{COLORS['red']}">-${totals['ltv']:,.0f}</td>
        </tr>
    </table>
    </div>
    <div style="font-size:0.75rem; color:{COLORS['gray']}; margin-top:8px; line-height:1.5;">
        All values are absolute losses (positive = bad). <strong>Sub</strong> = subtotal for that metric group.
        <strong>BPs Lost</strong> = activation + rescue + repeat (signups don't directly generate revenue).
        <strong>LTV Rev</strong> = BPs lost weighted by metric-specific retention multipliers (activation {LTV_MULT_ACT:.1f}×, active rescue {LTV_MULT_ACTIVE_RESC:.1f}×, inactive rescue {LTV_MULT_INACTIVE_RESC:.1f}×, repeat {LTV_MULT_REPEAT:.1f}×).
    </div>
    """, unsafe_allow_html=True)

with st.expander("Model Assumptions & Data Sources"):
    oon_embed_ratio = oon_embed_signups_all[0] / in_signups_all[0]
    st.markdown(f"""
**Signup Projections** (Feb–Dec 2026)
- IN signups from BP forecast (regular column)
- OON/Embed estimated at ~{oon_embed_ratio:.0%} of IN (Feb 2026 actuals)

**Recovery Model**
- All depression levers recover **linearly** back to baseline over the recovery window
- Example with {recovery_months}mo window and 0.90 depression: Month 1 = 0.90 → Month 2 = {0.90 + (1.0 - 0.90) * 1/recovery_months:.2f} → Month 3 = {0.90 + (1.0 - 0.90) * 2/recovery_months:.2f} → then back to 1.0
- This applies to all levers: signup, activation, rescue, and repeat rate depression

**Channel-Specific Email Dependency**
- **Signups**: IN heavily email-dependent. OON from performance marketing; Embed via partner flows.
- **Activation**: All channels depend on post-signup email nudges.
- **Rescue**: All users targeted by email regardless of signup channel.

**Rates** (from Sigma)
- M0 activation: {m0_activation_base:.2%} · M1+ uplift: {m1_plus_uplift:.0%}pp
- Active rescue: {active_rescue_rate:.2%} · Inactive rescue: {inactive_rescue_rate:.2%}
- Repeat rate: {repeat_rate_base:.2%} (trailing 6mo avg, Sep 2025–Feb 2026)
- Bill Paid Previous Month: {bp_prev_month_feb:,} (Feb 2026), growing ~3%/mo
- ~70% autopay → only ~30% manual-pay users are email-sensitive for repeat rate

**Revenue — LTV-Weighted (Primary)**
- BPs lost × ARPU × retention multiplier — accounts for 12-month retention curve per metric
  - Activation: {LTV_MULT_ACT:.2f}× (~${arpu * LTV_MULT_ACT:.0f}/lost BP)
  - Active rescue: {LTV_MULT_ACTIVE_RESC:.2f}× (~${arpu * LTV_MULT_ACTIVE_RESC:.0f}/lost BP)
  - Inactive rescue: {LTV_MULT_INACTIVE_RESC:.2f}× (~${arpu * LTV_MULT_INACTIVE_RESC:.0f}/lost BP)
  - Repeat rate: {LTV_MULT_REPEAT:.2f}× (~${arpu * LTV_MULT_REPEAT:.0f}/lost BP, uses activation curve as proxy)
- **In-month** shown for reference: BPs lost × ARPU (${arpu:.0f}/mo) — floor estimate, ignores retention tail

Retention curves from Apr–Jun 2024 cohorts (activation) and active/inactive segments (rescue).
    """)
