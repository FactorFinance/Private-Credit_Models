"""
Day 10/30 — Private Credit Series
Maintenance Capex Analyser

What this does:
    The single most manipulated number in credit analysis is
    maintenance capex — the portion of total capex required
    just to keep the business running at its current level.

    Management always argues it is lower than reality.
    Credit analysts always push it higher.
    The gap between these estimates can determine whether
    a loan gets approved or rejected.

    This model:
    - Takes reported capex and splits it by assumption
    - Shows FCF impact at different maintenance capex levels
    - Uses industry benchmarks to anchor the estimate
    - Runs sensitivity analysis across the full range

For CA students:
    In audit you verify total capex from the fixed asset register.
    In credit you ask what portion is truly discretionary —
    because only discretionary capex can be stopped in a stress.
    The non-discretionary portion is a fixed cash outflow
    that reduces the cushion protecting the lender.
"""

from dataclasses import dataclass
from typing import Dict


# Industry benchmark ranges for maintenance capex
# as a percentage of total capex
INDUSTRY_BENCHMARKS: Dict[str, tuple] = {
    "Manufacturing":       (0.60, 0.70),
    "Retail / Consumer":   (0.50, 0.65),
    "Healthcare Services": (0.55, 0.65),
    "Technology / SaaS":   (0.10, 0.25),
    "Logistics / Transport":(0.70, 0.80),
    "Business Services":   (0.30, 0.45),
    "Energy / Utilities":  (0.65, 0.80),
    "Media / Publishing":  (0.25, 0.40),
}


@dataclass
class CapexAnalysis:
    company_name: str
    industry: str

    # P&L inputs
    ebitda: float              # LTM EBITDA
    total_capex: float         # Total reported capex (no split given)
    cash_taxes: float          # Actual cash taxes
    cash_interest: float       # Cash interest on debt
    mandatory_principal: float # Mandatory debt repayment
    working_capital: float     # Working capital change

    # Management's claim
    mgmt_maintenance_pct: float  # What management says (e.g. 0.20 = 20%)

    # Total debt for leverage calculation
    total_debt: float
    leverage_covenant: float


def run_capex_analysis(ca: CapexAnalysis):
    """
    Full maintenance capex sensitivity analysis.
    Shows FCF, coverage, and credit verdict at each assumption.
    """

    sep = "=" * 65
    print(f"\n{sep}")
    print(f"  MAINTENANCE CAPEX ANALYSIS — {ca.company_name.upper()}")
    print(f"  Industry: {ca.industry}")
    print(sep)

    # Industry benchmark
    benchmark = INDUSTRY_BENCHMARKS.get(ca.industry)
    if benchmark:
        low_pct, high_pct = benchmark
        print(f"\n  Industry benchmark for {ca.industry}:")
        print(f"  Maintenance capex = {low_pct:.0%}–{high_pct:.0%} of total capex")
        print(f"  → ₹{ca.total_capex * low_pct:.0f}cr – "
              f"₹{ca.total_capex * high_pct:.0f}cr")
    else:
        print(f"\n  No benchmark available for {ca.industry}")
        low_pct, high_pct = 0.30, 0.60

    mgmt_capex = ca.total_capex * ca.mgmt_maintenance_pct
    mid_capex  = ca.total_capex * ((low_pct + high_pct) / 2)
    high_capex = ca.total_capex * high_pct

    print(f"\n  Management's claim:      "
          f"₹{mgmt_capex:.0f}cr "
          f"({ca.mgmt_maintenance_pct:.0%} of total)")
    print(f"  Industry midpoint:       "
          f"₹{mid_capex:.0f}cr "
          f"({(low_pct+high_pct)/2:.0%} of total)")
    print(f"  Industry high (stress):  "
          f"₹{high_capex:.0f}cr "
          f"({high_pct:.0%} of total)")

    # FCF sensitivity table
    print(f"\n  {'─'*60}")
    print(f"  FCF SENSITIVITY — How capex assumption changes everything")
    print(f"  {'─'*60}")
    print(f"  {'Scenario':<28} {'Maint Capex':>12} "
          f"{'FCF':>10} {'Coverage':>10} {'Verdict'}")
    print(f"  {'─'*60}")

    scenarios = [
        ("Management (low)",    mgmt_capex,  "Management"),
        ("Industry midpoint",   mid_capex,   "Analyst"),
        ("Industry high/stress", high_capex, "Stress"),
    ]

    # Also add some intermediate points
    for pct in [0.30, 0.40, 0.50, 0.60, 0.70]:
        capex = ca.total_capex * pct
        if not any(abs(capex - s[1]) < 2 for s in scenarios):
            scenarios.append(
                (f"  {pct:.0%} of total capex", capex, ""))

    scenarios.sort(key=lambda x: x[1])

    for label, maint_capex, tag in scenarios:
        fcf = (ca.ebitda
               - ca.cash_interest
               - ca.cash_taxes
               - maint_capex
               - ca.mandatory_principal
               - ca.working_capital)

        total_debt_service = ca.cash_interest + ca.mandatory_principal
        coverage = fcf / total_debt_service if total_debt_service > 0 else 99

        if fcf > total_debt_service * 0.5:
            verdict = "✓ Strong"
        elif fcf > 0:
            verdict = "~ Adequate"
        elif fcf > -10:
            verdict = "⚠ Marginal"
        else:
            verdict = "✗ Cannot service"

        tag_str = f" [{tag}]" if tag else ""
        print(f"  {label+tag_str:<28} "
              f"₹{maint_capex:>10.0f}cr "
              f"₹{fcf:>8.0f}cr "
              f"{coverage:>8.1f}x "
              f"  {verdict}")

    # Key question
    print(f"\n  {'─'*60}")
    print(f"  THE KEY QUESTION FOR EVERY CREDIT")
    print(f"  {'─'*60}")

    mgmt_fcf = (ca.ebitda - ca.cash_interest - ca.cash_taxes
                - mgmt_capex - ca.mandatory_principal - ca.working_capital)
    stress_fcf = (ca.ebitda - ca.cash_interest - ca.cash_taxes
                  - high_capex - ca.mandatory_principal - ca.working_capital)

    fcf_gap = mgmt_fcf - stress_fcf
    print(f"\n  Gap between management and stress FCF: "
          f"₹{fcf_gap:.0f} crore")
    print(f"  This is the uncertainty embedded in one input.")

    if stress_fcf < 0:
        print(f"\n  ⚠  In the stress case FCF turns negative.")
        print(f"     Company cannot service debt if maintenance")
        print(f"     capex is at the high end of industry norms.")
        print(f"     This is not a stress scenario — it is a")
        print(f"     plausible base case the model is hiding.")
    elif stress_fcf < ca.cash_interest:
        print(f"\n  ⚠  In the stress case FCF barely covers interest.")
        print(f"     No margin for error on working capital or taxes.")
    else:
        print(f"\n  ✓  Even in the stress case FCF is positive.")
        print(f"     Maintenance capex risk is manageable here.")

    # How to verify
    print(f"\n  {'─'*60}")
    print(f"  HOW TO VERIFY IN PRACTICE")
    print(f"  {'─'*60}")
    print(f"  1. Compare capex/revenue ratio over 5+ years")
    print(f"     (stable ratio suggests mostly maintenance)")
    print(f"  2. Ask management to itemise the top 10 capex projects")
    print(f"     (growth projects should be identifiable)")
    print(f"  3. Compare to listed peers in the same sector")
    print(f"     (maintenance intensity is industry-specific)")
    print(f"  4. Read the capex discussion in the MD&A")
    print(f"     (management often signals growth vs maintenance)")
    print(f"  5. Ask: if revenue fell 20%, how much capex could")
    print(f"     you cut? The answer = growth capex estimate.")
    print(f"{sep}\n")


# ── Run the model ──────────────────────────────────────────

if __name__ == "__main__":

    analysis = CapexAnalysis(
        company_name="MidCo Holdings Pvt Ltd",
        industry="Manufacturing",
        ebitda=100.0,
        total_capex=120.0,           # Total capex — no split disclosed
        cash_taxes=10.0,
        cash_interest=40.0,
        mandatory_principal=8.0,
        working_capital=10.0,
        mgmt_maintenance_pct=0.17,   # Management says only 17% = ₹20cr
        total_debt=400.0,
        leverage_covenant=5.5,
    )

    run_capex_analysis(analysis)

    # ── Try different industries ──
    # Change the industry field to see how benchmarks shift.
    # A SaaS company with 15% maintenance capex is normal.
    # A logistics company with 15% maintenance capex is
    # almost certainly understating — and hiding FCF risk.

    # ── The CA student exercise ──
    # Pull any manufacturing or retail company's annual report.
    # They report one capex number. Apply the industry benchmark.
    # Calculate FCF at management assumption vs industry benchmark.
    # The gap tells you the uncertainty in the credit decision.
