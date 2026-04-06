"""
Day 08/30 — Private Credit Series
PIK Toggle Compounder

What this does:
    Models the compounding effect of PIK interest on a loan balance.
    Shows how debt grows vs enterprise value over time.
    Identifies the year where equity is effectively wiped out.
    Compares cash interest vs PIK scenarios side by side.

PIK = Payment in Kind. Instead of paying interest in cash,
the interest is added to the loan principal every quarter.
The loan grows. The borrower pays nothing until maturity.

For CA students:
    You already understand interest accrual and compounding.
    PIK is that same concept — but compounding against the borrower.
    The CA who understands the time value of money already
    understands exactly why PIK is structurally dangerous.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class PIKLoan:
    company_name: str
    principal: float          # Initial loan amount (crore)
    pik_rate: float          # Annual PIK interest rate
    cash_rate: float         # Annual cash interest rate (if any)
    tenor_years: int         # Loan term in years
    ev_at_close: float       # Enterprise value at deal close
    ev_growth_rate: float    # Annual EV growth assumption
    senior_debt: float       # Senior debt above this tranche


def model_pik(loan: PIKLoan) -> List[dict]:
    """Model PIK compounding year by year."""

    rows = []
    balance = loan.principal

    for yr in range(loan.tenor_years + 1):
        ev = loan.ev_at_close * ((1 + loan.ev_growth_rate) ** yr)
        total_debt = loan.senior_debt + balance
        equity_cushion = ev - total_debt
        equity_pct = equity_cushion / ev if ev > 0 else 0
        cushion_flag = (
            "✓ Healthy" if equity_pct > 0.40 else
            "~ Watch"   if equity_pct > 0.25 else
            "⚠ Tight"   if equity_pct > 0.10 else
            "✗ Danger"  if equity_cushion > 0 else
            "✗ WIPED OUT"
        )

        rows.append({
            "year": yr,
            "balance": balance,
            "ev": ev,
            "total_debt": total_debt,
            "equity_cushion": equity_cushion,
            "equity_pct": equity_pct,
            "flag": cushion_flag,
        })

        if yr < loan.tenor_years:
            pik_accrual = balance * loan.pik_rate
            balance += pik_accrual

    return rows


def compare_cash_vs_pik(loan: PIKLoan):
    """
    Side by side comparison:
    What the lender receives in cash vs PIK scenario.
    And what the borrower owes at maturity.
    """

    # Cash scenario: interest paid quarterly, principal at maturity
    cash_interest_pa = loan.principal * loan.cash_rate
    total_cash_received = (cash_interest_pa * loan.tenor_years
                           + loan.principal)
    total_cash_interest = cash_interest_pa * loan.tenor_years

    # PIK scenario: everything at maturity
    pik_balance = loan.principal * ((1 + loan.pik_rate)
                                    ** loan.tenor_years)
    pik_interest_earned = pik_balance - loan.principal

    sep = "=" * 60
    print(f"\n{sep}")
    print(f"  PIK ANALYSIS — {loan.company_name.upper()}")
    print(sep)

    print(f"\n  Initial Principal:    ₹{loan.principal:.0f} crore")
    print(f"  Cash Rate:           {loan.cash_rate:.0%} p.a.")
    print(f"  PIK Rate:            {loan.pik_rate:.0%} p.a.")
    print(f"  Tenor:               {loan.tenor_years} years")
    print(f"  Senior Debt:          ₹{loan.senior_debt} crore")
    
    print(f"\n  {'─'*55}")
    print(f"  COMPARISON: Cash Interest vs PIK")
    print(f"  {'─'*55}")
    print(f"  {'':30} {'Cash':>10} {'PIK':>12}")
    print(f"  {'─'*55}")
    print(f"  {'Annual cash to lender':<30} "
          f"₹{cash_interest_pa:>8.1f}cr  {'None':>10}")
    print(f"  {'Total interest earned':<30} "
          f"₹{total_cash_interest:>8.1f}cr  "
          f"₹{pik_interest_earned:>8.1f}cr")
    print(f"  {'Balance due at maturity':<30} "
          f"₹{loan.principal:>8.1f}cr  "
          f"₹{pik_balance:>8.1f}cr")
    print(f"  {'Debt growth':<30} {'0%':>10}  "
          f"{(pik_balance/loan.principal - 1):>10.0%}")
    print(f"\n  Lender's dilemma in PIK:")
    print(f"  Higher paper return (₹{pik_interest_earned:.0f}cr vs "
          f"₹{total_cash_interest:.0f}cr)")
    print(f"  But zero cash for {loan.tenor_years} years.")
    print(f"  All value depends on borrower surviving to maturity.")

    # Year by year compounding table
    print(f"\n  {'─'*55}")
    print(f"  PIK COMPOUNDING — DEBT vs ENTERPRISE VALUE")
    print(f"  {'─'*55}")
    print(f"  {'Year':<8} {'PIK Balance':>12} {'EV':>12} "
          f"{'Eq Cushion (EV- Senior Debt- PIK Balance)':>18} {'Status'}")
    print(f"  {'─'*55}")

    rows = model_pik(loan)
    for r in rows:
        print(f"  {r['year']:<8} "
              f"₹{r['balance']:>10.1f}cr "
              f"₹{r['ev']:>10.1f}cr "
              f"₹{r['equity_cushion']:>10.1f}cr "
              f"  {r['flag']}")

    # Key insight
    wipeout_year = None
    for r in rows:
        if r['equity_cushion'] <= 0:
            wipeout_year = r['year']
            break

    print(f"\n  {'─'*55}")
    if wipeout_year:
        print(f"  ⚠  Equity wiped out at Year {wipeout_year}")
        print(f"     At this point the lender owns the company")
        print(f"     in economic terms — even without a formal default.")
    else:
        print(f"  ✓  Equity cushion maintained through tenor")
        print(f"     But watch: EV must grow at {loan.ev_growth_rate:.0%}")
        print(f"     while PIK grows at {loan.pik_rate:.0%}.")
        print(f"     Any EV shortfall is magnified by PIK compounding.")

    # Stress test: what if EV grows slower
    print(f"\n  {'─'*55}")
    print(f"  STRESS: What if EV grows at 4% instead of "
          f"{loan.ev_growth_rate:.0%}?")
    print(f"  {'─'*55}")

    stressed = PIKLoan(
        company_name=loan.company_name,
        principal=loan.principal,
        pik_rate=loan.pik_rate,
        cash_rate=loan.cash_rate,
        tenor_years=loan.tenor_years,
        ev_at_close=loan.ev_at_close,
        ev_growth_rate=0.04,
        senior_debt=loan.senior_debt,
    )

    stressed_rows = model_pik(stressed)
    for r in stressed_rows:
        print(f"  Year {r['year']}: "
              f"PIK ₹{r['balance']:.0f}cr | "
              f"EV ₹{r['ev']:.0f}cr | "
              f"Cushion ₹{r['equity_cushion']:.0f}cr "
              f"{r['flag']}")

    print(f"\n{sep}\n")


# ── Run the model ──────────────────────────────────────────

if __name__ == "__main__":

    loan = PIKLoan(
        company_name="MidCo Holdings Pvt Ltd",
        principal=100.0,       # ₹100 crore PIK loan
        pik_rate=0.12,         # 12% PIK rate
        cash_rate=0.12,        # Same rate if cash
        tenor_years=5,
        ev_at_close=300.0,     # Company worth ₹300 crore
        ev_growth_rate=0.08,   # 8% annual growth assumed
        senior_debt=100.0,     # ₹100 crore senior debt above
    )

    compare_cash_vs_pik(loan)

    # ── The signal to watch in real portfolios ──
    # When a BDC portfolio company elects its PIK toggle:
    # 1. The loan balance starts growing instead of shrinking
    # 2. The company cannot afford cash interest — distress signal
    # 3. The equity cushion begins compressing
    # 4. If EV does not grow faster than PIK rate — equity gone
    #
    # This is why PIK election is tracked as a "shadow default"
    # even though the loan is technically still performing.
    # The 2025-2026 private credit market has seen PIK elections
    # triple year-on-year — a key signal of portfolio stress.
