"""
Day 05/30 — Private Credit Series
Covenant Compliance Tracker

What this does:
    Takes a company's quarterly financials and tests three
    standard maintenance covenants every quarter:
    1. Leverage covenant (Debt / EBITDA)
    2. Coverage covenant (EBITDA / Interest)
    3. FCCR (EBITDA / Interest + Principal)

    The key output is not just pass/fail — it is headroom
    trajectory. A company falling toward a breach is more
    dangerous than one that already breached once.

For CA students:
    In audit you verify covenant compliance as a disclosure.
    In credit you track headroom every quarter as an early
    warning signal — before the breach, not after.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class QuarterlyData:
    quarter: str           # e.g. "Q1 FY25"
    ebitda_ltm: float      # Last twelve months EBITDA
    total_debt: float      # Total debt outstanding
    cash_interest: float   # LTM cash interest paid
    mandatory_principal: float  # LTM mandatory principal repayment


@dataclass
class CovenantPackage:
    max_leverage: float        # Max Debt/EBITDA (e.g. 5.5)
    min_coverage: float        # Min EBITDA/Interest (e.g. 2.0)
    min_fccr: float            # Min EBITDA/(Interest+Principal) (e.g. 1.1)


def test_quarter(q: QuarterlyData, cov: CovenantPackage) -> dict:
    """Test all three covenants for one quarter."""

    leverage  = q.total_debt / q.ebitda_ltm if q.ebitda_ltm > 0 else 99
    coverage  = q.ebitda_ltm / q.cash_interest if q.cash_interest > 0 else 99
    fccr      = q.ebitda_ltm / (q.cash_interest + q.mandatory_principal) \
                if (q.cash_interest + q.mandatory_principal) > 0 else 99

    lev_headroom  = (cov.max_leverage - leverage) / cov.max_leverage
    cov_headroom  = (coverage - cov.min_coverage) / cov.min_coverage
    fccr_headroom = (fccr - cov.min_fccr) / cov.min_fccr

    lev_pass  = leverage <= cov.max_leverage
    cov_pass  = coverage >= cov.min_coverage
    fccr_pass = fccr    >= cov.min_fccr
    all_pass  = lev_pass and cov_pass and fccr_pass

    # Risk flag based on minimum headroom
    min_headroom = min(lev_headroom, cov_headroom, fccr_headroom)
    if not all_pass:
        risk = "🔴 BREACH"
    elif min_headroom < 0.05:
        risk = "🔴 CRITICAL"
    elif min_headroom < 0.15:
        risk = "🟡 WATCH"
    elif min_headroom < 0.30:
        risk = "🟠 MONITOR"
    else:
        risk = "🟢 STRONG"

    return {
        "quarter":        q.quarter,
        "leverage":       leverage,
        "lev_pass":       lev_pass,
        "lev_headroom":   lev_headroom,
        "coverage":       coverage,
        "cov_pass":       cov_pass,
        "cov_headroom":   cov_headroom,
        "fccr":           fccr,
        "fccr_pass":      fccr_pass,
        "fccr_headroom":  fccr_headroom,
        "all_pass":       all_pass,
        "min_headroom":   min_headroom,
        "risk":           risk,
    }


def run_covenant_tracker(quarters: List[QuarterlyData],
                         cov: CovenantPackage,
                         company_name: str = "Company"):
    """
    Run covenant tests across all quarters.
    Shows headroom trajectory — the early warning signal.
    """

    results = [test_quarter(q, cov) for q in quarters]

    sep = "=" * 72
    print(f"\n{sep}")
    print(f"  COVENANT TRACKER — {company_name.upper()}")
    print(f"  Covenants: Leverage ≤{cov.max_leverage}x | "
          f"Coverage ≥{cov.min_coverage}x | FCCR ≥{cov.min_fccr}x")
    print(sep)

    # Main table
    print(f"\n  {'Quarter':<10} {'Leverage':>10} {'Hdroom':>8} "
          f"{'Coverage':>10} {'Hdroom':>8} "
          f"{'FCCR':>8} {'Hdroom':>8}  {'Status'}")
    print(f"  {'─'*68}")

    for r in results:
        lev_flag = "✓" if r["lev_pass"] else "✗"
        cov_flag = "✓" if r["cov_pass"] else "✗"
        fcc_flag = "✓" if r["fccr_pass"] else "✗"

        print(f"  {r['quarter']:<10} "
              f"{r['leverage']:>8.2f}x{lev_flag} "
              f"{r['lev_headroom']:>7.1%} "
              f"{r['coverage']:>8.2f}x{cov_flag} "
              f"{r['cov_headroom']:>7.1%} "
              f"{r['fccr']:>6.2f}x{fcc_flag} "
              f"{r['fccr_headroom']:>7.1%}  "
              f"{r['risk']}")

    # Headroom trend analysis
    print(f"\n  {'─'*68}")
    print(f"  HEADROOM TRAJECTORY (minimum headroom across all covenants)")
    print(f"  {'─'*68}")

    for i, r in enumerate(results):
        bar_len = max(0, int(r["min_headroom"] * 40))
        bar = "█" * bar_len

        if r["min_headroom"] < 0:
            bar = "✗ BREACH"
            color_label = ""
        elif r["min_headroom"] < 0.10:
            color_label = " ← DANGER"
        elif r["min_headroom"] < 0.20:
            color_label = " ← WATCH"
        else:
            color_label = ""

        print(f"  {r['quarter']:<10} {bar:<40} "
              f"{r['min_headroom']:>6.1%}{color_label}")

        # Trend arrow
        if i > 0:
            prev = results[i-1]["min_headroom"]
            curr = r["min_headroom"]
            change = curr - prev
            if change < -0.05:
                print(f"  {'':10} ↓ Headroom falling "
                      f"{abs(change):.1%} — investigate")

    # Breach analysis
    breaches = [r for r in results if not r["all_pass"]]
    watches   = [r for r in results
                 if r["all_pass"] and r["min_headroom"] < 0.15]

    print(f"\n  {'─'*68}")
    print(f"  SUMMARY")
    print(f"  Quarters tested:  {len(results)}")
    print(f"  Compliant:        {len(results) - len(breaches)}")
    print(f"  Breaches:         {len(breaches)}")
    print(f"  On watch (<15%):  {len(watches)}")

    if breaches:
        print(f"\n  ⚠  ACTION REQUIRED:")
        for b in breaches:
            print(f"  → {b['quarter']}: breach detected — "
                  f"review amendment options")

    print(f"{sep}\n")
    return results


# ── Run the model ──────────────────────────────────────────

if __name__ == "__main__":

    # Define covenant package for this deal
    covenants = CovenantPackage(
        max_leverage=5.5,
        min_coverage=2.0,
        min_fccr=1.1,
    )

    # Quarterly data — showing a company trending toward breach
    # Change these numbers for any real company
    quarters = [
        QuarterlyData("Q1 FY24", ebitda_ltm=100, total_debt=380,
                      cash_interest=25, mandatory_principal=8),
        QuarterlyData("Q2 FY24", ebitda_ltm=98,  total_debt=385,
                      cash_interest=25, mandatory_principal=8),
        QuarterlyData("Q3 FY24", ebitda_ltm=93,  total_debt=388,
                      cash_interest=26, mandatory_principal=8),
        QuarterlyData("Q4 FY24", ebitda_ltm=88,  total_debt=390,
                      cash_interest=26, mandatory_principal=8),
        QuarterlyData("Q1 FY25", ebitda_ltm=82,  total_debt=392,
                      cash_interest=26, mandatory_principal=8),
        QuarterlyData("Q2 FY25", ebitda_ltm=75,  total_debt=394,
                      cash_interest=26, mandatory_principal=8),
        QuarterlyData("Q3 FY25", ebitda_ltm=70,  total_debt=396,
                      cash_interest=27, mandatory_principal=8),
        QuarterlyData("Q4 FY25", ebitda_ltm=64,  total_debt=398,
                      cash_interest=27, mandatory_principal=8),
    ]

    run_covenant_tracker(quarters, covenants,
                         company_name="MidCo Holdings Pvt Ltd")

    # ── The CA student exercise ──
    # Pull any listed company's quarterly results from their
    # investor presentations. Estimate EBITDA, debt, and interest.
    # Run this tracker to see if they would breach a standard
    # 5.5x leverage covenant — even if they are not PE-backed.
    # The exercise builds credit instinct fast.
