"""
Day 03/30 — Private Credit Series
EBITDA → CFADS → Cushion Bridge

What this does:
    Walks from EBITDA to Cash Available for Debt Service (CFADS)
    to the residual cushion — the real measure of credit risk.

    The cushion is the shock absorber. It tells you how far
    EBITDA can fall before the lender stops getting paid.

For CA students:
    Every item here is something you verified in articleship.
    The lender is asking a harder question about the same numbers:
    is the cushion thick enough to survive a bad year?
"""

from dataclasses import dataclass


@dataclass
class CreditDeal:
    company_name: str

    # ── Operating inputs ──────────────────────────────────
    ebitda: float               # Starting EBITDA (crore)
    cash_taxes: float           # Actual cash taxes paid
    maintenance_capex: float    # Capex to keep business running
    working_capital: float      # Cash consumed by WC changes

    # ── Debt structure ────────────────────────────────────
    senior_interest: float      # Senior lender's interest (paid first)
    my_interest: float          # Your tranche's interest obligation
    my_principal: float         # Mandatory principal repayment


def run_cfads_bridge(deal: CreditDeal) -> dict:
    """
    EBITDA → CFADS → Cushion walk.
    Returns all intermediate values.
    """

    # Step 1: Fixed cash outflows before any debt service
    fixed_outflows = (deal.cash_taxes
                      + deal.maintenance_capex
                      + deal.working_capital)

    # Step 2: Cash Available for Debt Service
    cfads = deal.ebitda - fixed_outflows

    # Step 3: Pay senior lender first (they sit on ground floor)
    after_senior = cfads - deal.senior_interest

    # Step 4: Coverage ratio — how many times can you cover interest?
    coverage = after_senior / deal.my_interest if deal.my_interest > 0 else 99

    # Step 5: Pay your interest
    after_my_interest = after_senior - deal.my_interest

    # Step 6: Pay mandatory principal
    cushion = after_my_interest - deal.my_principal

    # Step 7: Cushion as % of EBITDA
    cushion_pct = cushion / deal.ebitda if deal.ebitda > 0 else 0

    sep = "=" * 56
    print(f"\n{sep}")
    print(f"  CFADS BRIDGE — {deal.company_name.upper()}")
    print(sep)
    print(f"\n  {'EBITDA':<38} ₹{deal.ebitda:>7.1f}cr")
    print(f"  {'─'*48}")
    print(f"  {'— Cash taxes paid':<38} ₹{deal.cash_taxes:>7.1f}cr")
    print(f"  {'— Maintenance capex':<38} ₹{deal.maintenance_capex:>7.1f}cr")
    print(f"  {'— Working capital consumed':<38} ₹{deal.working_capital:>7.1f}cr")
    print(f"  {'─'*48}")
    print(f"  {'CFADS (Cash for Debt Service)':<38} ₹{cfads:>7.1f}cr")
    print(f"  {'─'*48}")
    print(f"  {'— Senior interest (paid first)':<38} ₹{deal.senior_interest:>7.1f}cr")
    print(f"  {'  → After senior lender':<38} ₹{after_senior:>7.1f}cr")
    print(f"  {'─'*48}")
    print(f"  {'— My interest obligation':<38} ₹{deal.my_interest:>7.1f}cr")
    print(f"  {'  → Coverage ratio':<38} {coverage:>7.1f}x")
    print(f"  {'— Mandatory principal':<38} ₹{deal.my_principal:>7.1f}cr")
    print(f"  {'─'*48}")

    cushion_flag = "✓" if cushion > 0 else "✗"
    print(f"  {'CUSHION (Margin of Safety)':<38} "
          f"₹{cushion:>7.1f}cr {cushion_flag}")
    print(f"  {'Cushion as % of EBITDA':<38} {cushion_pct:>7.1%}")

    if cushion > deal.ebitda * 0.20:
        verdict = "STRONG — thick shock absorber"
    elif cushion > 0:
        verdict = "ADEQUATE — thin, watch carefully"
    else:
        verdict = "CRITICAL — no cushion, default risk"

    print(f"\n  Lender verdict: {verdict}")
    print(f"{sep}\n")

    return {
        "ebitda": deal.ebitda,
        "fixed_outflows": fixed_outflows,
        "cfads": cfads,
        "after_senior": after_senior,
        "coverage": coverage,
        "cushion": cushion,
        "cushion_pct": cushion_pct,
    }


def stress_test(deal: CreditDeal,
                haircuts: list = [0, 0.10, 0.20, 0.30]):
    """
    Run the CFADS bridge at different EBITDA levels.

    Key insight: fixed outflows don't shrink when EBITDA falls.
    This creates non-linear cushion compression — the shock absorber
    gets thinner much faster than EBITDA declines.
    """

    sep = "=" * 68
    print(f"{sep}")
    print(f"  STRESS TEST — How cushion compresses as EBITDA falls")
    print(f"  Fixed outflows stay constant. Only EBITDA moves.")
    print(f"{sep}")
    print(f"  {'Scenario':<18} {'EBITDA':>9} {'CFADS':>9} "
          f"{'Coverage':>10} {'Cushion':>10} {'Safe?':>7}")
    print(f"  {'─'*62}")

    labels = ["Base case", "-10% EBITDA", "-20% EBITDA", "-30% EBITDA"]

    fixed = (deal.cash_taxes + deal.maintenance_capex
             + deal.working_capital)

    for label, h in zip(labels, haircuts):
        ebitda_s = deal.ebitda * (1 - h)
        cfads = ebitda_s - fixed
        after_s = cfads - deal.senior_interest
        cov = after_s / deal.my_interest if deal.my_interest > 0 else 99
        cushion = after_s - deal.my_interest - deal.my_principal
        safe = "✓ Yes" if cushion > 0 else "✗ No"

        print(f"  {label:<18} "
              f"₹{ebitda_s:>7.0f}cr "
              f"₹{cfads:>7.0f}cr "
              f"{cov:>9.1f}x "
              f"₹{cushion:>8.0f}cr "
              f"{safe:>7}")

    print(f"{sep}\n")


# ── Run the model ──────────────────────────────────────────

if __name__ == "__main__":

    # Example deal — change numbers for any company
    deal = CreditDeal(
        company_name="MidCo Holdings Pvt Ltd",

        ebitda=100.0,

        # Fixed outflows — these do not move with EBITDA
        cash_taxes=10.0,
        maintenance_capex=10.0,
        working_capital=20.0,       # ₹20cr fixed outflows total

        # Debt structure
        senior_interest=10.0,       # Senior lender paid first
        my_interest=20.0,           # Our tranche interest
        my_principal=5.0,           # Mandatory principal repayment
    )

    # Run the full CFADS bridge
    run_cfads_bridge(deal)

    # Stress test — shows cushion compression
    stress_test(deal)

    # ── Try your own deal ──
    # Pull any company's numbers from their annual report
    # and see how thick or thin their cushion actually is

    # my_deal = CreditDeal(
    #     company_name="Your Company",
    #     ebitda=0,
    #     cash_taxes=0,
    #     maintenance_capex=0,
    #     working_capital=0,
    #     senior_interest=0,
    #     my_interest=0,
    #     my_principal=0,
    # )
    # run_cfads_bridge(my_deal)
    # stress_test(my_deal)
