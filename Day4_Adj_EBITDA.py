"""
Day 04/30 — Private Credit Series
Adjusted EBITDA Analyser

What this does:
    Takes reported EBITDA and each add-back, flags aggressive
    ones, and shows what leverage looks like at different levels
    of add-back credibility.

    The core question: if these add-backs never materialise,
    what is actual leverage — and does it breach the covenant?

For CA students:
    In audit you question whether a charge is truly one-time.
    In credit you apply that same skepticism to the loan
    agreement's EBITDA definition — not the P&L.
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Addback:
    name: str
    amount: float           # crore
    category: str          # "verified", "projected", "aggressive"
    description: str       # management's argument
    reality_check: str     # the skeptical question


@dataclass
class EBITDAAnalysis:
    company_name: str
    reported_ebitda: float          # From audited accounts
    total_debt: float               # For leverage calculation
    leverage_covenant: float        # Max Debt/EBITDA allowed
    addbacks: List[Addback] = field(default_factory=list)


# Credibility weights by category
CREDIBILITY = {
    "verified":   1.00,   # Confirmed, already happened
    "projected":  0.50,   # Likely but not guaranteed
    "aggressive": 0.15,   # Skeptical — unlikely to materialise
}

CATEGORY_FLAGS = {
    "verified":   "✓",
    "projected":  "~",
    "aggressive": "⚠",
}


def run_analysis(ea: EBITDAAnalysis):
    """
    Run the full Adjusted EBITDA analysis.
    Shows: full addback, haircut scenarios, covenant impact.
    """

    total_addbacks = sum(a.amount for a in ea.addbacks)
    adj_ebitda_full = ea.reported_ebitda + total_addbacks
    addback_pct = total_addbacks / ea.reported_ebitda

    sep = "=" * 62
    print(f"\n{sep}")
    print(f"  ADJUSTED EBITDA ANALYSIS — {ea.company_name.upper()}")
    print(sep)

    # ── Add-back detail ──────────────────────────────────
    print(f"\n  Reported EBITDA: ₹{ea.reported_ebitda:.0f} crore")
    print(f"\n  {'Add-back':<28} {'Cat':>6} {'Amount':>8}  Reality check")
    print(f"  {'─'*58}")

    for ab in ea.addbacks:
        flag = CATEGORY_FLAGS[ab.category]
        pct_of_ebitda = ab.amount / ea.reported_ebitda
        aggressive_flag = " ← HIGH" if pct_of_ebitda > 0.10 else ""
        print(f"  {ab.name:<28} {flag:>4} "
              f"  +₹{ab.amount:>5.0f}cr{aggressive_flag}")
        print(f"  {'':28}       {ab.reality_check}")

    print(f"  {'─'*58}")
    print(f"  {'Total add-backs':<28}      +₹{total_addbacks:>5.0f}cr "
          f"({addback_pct:.0%} of reported)")

    if addback_pct > 0.15:
        print(f"\n  ⚠  Add-backs exceed 15% of reported EBITDA.")
        print(f"     Flag every single one before approving.")

    # ── Scenarios ────────────────────────────────────────
    print(f"\n  {'─'*58}")
    print(f"  EBITDA at different add-back credibility levels")
    print(f"  {'─'*58}")

    scenarios = [
        ("Management case (100%)", 1.00),
        ("Probable (75% credit)",  0.75),
        ("Conservative (50%)",     0.50),
        ("Skeptical (25%)",        0.25),
        ("Reported only (0%)",     0.00),
    ]

    for label, credit in scenarios:
        credited = sum(
            a.amount * CREDIBILITY[a.category] * credit
            for a in ea.addbacks
        )
        adj = ea.reported_ebitda + credited
        leverage = ea.total_debt / adj
        headroom = ea.leverage_covenant - leverage
        covenant_ok = leverage <= ea.leverage_covenant
        flag = "✓" if covenant_ok else "✗ BREACH"

        print(f"  {label:<30} ₹{adj:>6.0f}cr  "
              f"{leverage:.1f}x  {flag}")

    # ── Covenant impact ───────────────────────────────────
    print(f"\n  {'─'*58}")
    print(f"  COVENANT IMPACT")
    print(f"  Max Leverage Covenant: {ea.leverage_covenant:.1f}x")
    print(f"  Total Debt: ₹{ea.total_debt:.0f} crore")
    print(f"\n  At Adjusted EBITDA (₹{adj_ebitda_full:.0f}cr): "
          f"{ea.total_debt/adj_ebitda_full:.1f}x "
          f"{'✓ Compliant' if ea.total_debt/adj_ebitda_full <= ea.leverage_covenant else '✗ Breach'}")
    print(f"  At Reported EBITDA  (₹{ea.reported_ebitda:.0f}cr): "
          f"{ea.total_debt/ea.reported_ebitda:.1f}x "
          f"{'✓ Compliant' if ea.total_debt/ea.reported_ebitda <= ea.leverage_covenant else '✗ Breach'}")

    # ── Key question ──────────────────────────────────────
    breakeven = ea.total_debt / ea.leverage_covenant
    addbacks_needed = max(0, breakeven - ea.reported_ebitda)
    addback_survival = addbacks_needed / total_addbacks if total_addbacks > 0 else 0

    print(f"\n  KEY QUESTION FOR LENDER:")
    print(f"  What % of add-backs must materialise to stay")
    print(f"  within the {ea.leverage_covenant:.1f}x covenant?")
    print(f"  Answer: {addback_survival:.0%} of add-backs must be real.")
    if addback_survival < 0.5:
        print(f"  → Even if half the add-backs fail, covenant holds.")
    elif addback_survival < 0.8:
        print(f"  → Most add-backs must materialise. Watch carefully.")
    else:
        print(f"  → Almost all add-backs must be real. Very tight.")

    print(f"{sep}\n")


# ── Run the model ──────────────────────────────────────────

if __name__ == "__main__":

    analysis = EBITDAAnalysis(
        company_name="MidCo Holdings Pvt Ltd",
        reported_ebitda=80.0,
        total_debt=500.0,
        leverage_covenant=5.5,
        addbacks=[
            Addback(
                name="One-time restructuring",
                amount=12.0,
                category="aggressive",
                description="Non-recurring charges this year",
                reality_check="4th year in a row of 'one-time' charges"
            ),
            Addback(
                name="Run-rate cost savings",
                amount=10.0,
                category="projected",
                description="Savings identified from integration",
                reality_check="Projected only — not yet in the P&L"
            ),
            Addback(
                name="Sponsor management fees",
                amount=8.0,
                category="aggressive",
                description="Fees eliminated post-acquisition",
                reality_check="Returned as advisory fees 6 months later"
            ),
            Addback(
                name="Pro forma acquisition",
                amount=2.0,
                category="projected",
                description="Full year of acquired company",
                reality_check="Owned for 4 months only"
            ),
        ]
    )

    run_analysis(analysis)

    # ── Try your own deal ──
    # Pull the EBITDA definition from any credit agreement on
    # SEC EDGAR and model each add-back here.
    # The credibility category is your judgment call —
    # that judgment is the credit analysis.
