"""
Day 09/30 — Private Credit Series
Dividend Recapitalisation Impact Model

What this does:
    Models the before and after of a dividend recapitalisation.
    Shows exactly how leverage changes, equity cushion shrinks,
    and covenant headroom compresses — all from one transaction
    that does nothing to improve the underlying business.

    The key insight: the company's EBITDA does not change.
    The company's assets do not change.
    Only the debt increases and the equity shrinks.
    The lender's risk increases. Their rate does not.

For CA students:
    In audit you flag related party transactions where a subsidiary
    pays unusual dividends to a parent entity.
    A dividend recap is that same transaction — structured through
    a PE sponsor, funded by new debt, borne by the lender.
"""

from dataclasses import dataclass


@dataclass
class DividendRecap:
    company_name: str

    # Pre-recap capital structure
    ebitda: float                    # LTM EBITDA
    existing_debt: float             # Existing senior debt
    existing_rate: float             # Existing debt rate
    equity_value: float              # Sponsor equity at cost

    # Recap details
    recap_amount: float              # New debt raised
    recap_rate: float                # Rate on new debt
    leverage_covenant: float         # Max Debt/EBITDA covenant

    # What goes to sponsor
    sponsor_distribution: float      # Cash extracted by sponsor


def run_recap_analysis(r: DividendRecap):
    """
    Full before/after analysis of a dividend recapitalisation.
    Shows impact on every credit metric that matters.
    """

    # Pre-recap metrics
    pre_total_debt     = r.existing_debt
    pre_leverage       = pre_total_debt / r.ebitda
    pre_interest       = r.existing_debt * r.existing_rate
    pre_coverage       = r.ebitda / pre_interest
    pre_lev_headroom   = (r.leverage_covenant - pre_leverage) / r.leverage_covenant
    pre_equity         = r.equity_value

    # Post-recap metrics
    post_total_debt    = r.existing_debt + r.recap_amount
    post_leverage      = post_total_debt / r.ebitda
    post_interest      = (r.existing_debt * r.existing_rate
                         + r.recap_amount * r.recap_rate)
    post_coverage      = r.ebitda / post_interest
    post_lev_headroom  = (r.leverage_covenant - post_leverage) / r.leverage_covenant
    post_equity        = r.equity_value - r.sponsor_distribution

    # Lender impact
    leverage_increase  = post_leverage - pre_leverage
    coverage_decline   = pre_coverage - post_coverage
    headroom_loss      = pre_lev_headroom - post_lev_headroom
    equity_cushion_loss = pre_equity - post_equity
    additional_interest = r.recap_amount * r.recap_rate

    sep = "=" * 62
    print(f"\n{sep}")
    print(f"  DIVIDEND RECAP ANALYSIS — {r.company_name.upper()}")
    print(sep)

    print(f"\n  {'Metric':<32} {'Before':>10} {'After':>10} {'Change':>10}")
    print(f"  {'─'*58}")
    print(f"  {'Total Debt':<32} "
          f"₹{pre_total_debt:>8.0f}cr "
          f"₹{post_total_debt:>8.0f}cr "
          f"₹{r.recap_amount:>+8.0f}cr")
    print(f"  {'Leverage (Debt/EBITDA)':<32} "
          f"{pre_leverage:>9.1f}x "
          f"{post_leverage:>9.1f}x "
          f"{leverage_increase:>+9.1f}x")
    print(f"  {'Interest Coverage':<32} "
          f"{pre_coverage:>9.1f}x "
          f"{post_coverage:>9.1f}x "
          f"{-coverage_decline:>+9.1f}x")
    print(f"  {'Covenant Headroom':<32} "
          f"{pre_lev_headroom:>9.1%} "
          f"{post_lev_headroom:>9.1%} "
          f"{-headroom_loss:>+9.1%}")
    print(f"  {'Sponsor Equity at Risk':<32} "
          f"₹{pre_equity:>8.0f}cr "
          f"₹{post_equity:>8.0f}cr "
          f"₹{-equity_cushion_loss:>+8.0f}cr")
    print(f"  {'Annual Cash Interest Burden':<32} "
          f"₹{pre_interest:>8.0f}cr "
          f"₹{post_interest:>8.0f}cr "
          f"₹{additional_interest:>+8.0f}cr")

    # Covenant check
    print(f"\n  {'─'*58}")
    print(f"  COVENANT CHECK (max leverage {r.leverage_covenant:.1f}x)")
    pre_ok  = "✓ COMPLIANT" if pre_leverage  <= r.leverage_covenant else "✗ BREACH"
    post_ok = "✓ COMPLIANT" if post_leverage <= r.leverage_covenant else "✗ BREACH"
    print(f"  Before recap: {pre_leverage:.1f}x — {pre_ok}")
    print(f"  After recap:  {post_leverage:.1f}x — {post_ok}")

    if post_leverage > r.leverage_covenant:
        print(f"\n  ⚠  RECAP BREACHES COVENANT")
        print(f"     This means lenders must have CONSENTED to the recap")
        print(f"     OR the covenant was amended before the transaction.")
        print(f"     Either way — lenders gave something up.")

    # Who won, who lost
    print(f"\n  {'─'*58}")
    print(f"  SCORECARD")
    print(f"\n  PE Sponsor:")
    print(f"  → Extracted ₹{r.sponsor_distribution:.0f} crore in cash")
    print(f"  → Recovered "
          f"{r.sponsor_distribution/r.equity_value:.0%} of original equity investment")
    print(f"  → Still owns the business")
    print(f"  → Equity at risk reduced from "
          f"₹{pre_equity:.0f}cr to ₹{post_equity:.0f}cr")

    print(f"\n  Lender:")
    print(f"  → Leverage increased by {leverage_increase:.1f}x")
    print(f"  → Coverage dropped by {coverage_decline:.1f}x")
    print(f"  → Covenant headroom lost: {headroom_loss:.0%}")
    print(f"  → Additional interest burden on borrower: "
          f"₹{additional_interest:.0f}cr/year")
    print(f"  → Rate on existing loan: unchanged")
    print(f"  → Risk increased. Compensation: zero.")

    # The signal
    print(f"\n  {'─'*58}")
    print(f"  THE SIGNAL")
    sponsor_recovery = r.sponsor_distribution / r.equity_value
    if sponsor_recovery > 0.75:
        signal = "HIGH RISK — Sponsor has largely exited economically"
    elif sponsor_recovery > 0.50:
        signal = "WATCH — Sponsor confidence declining"
    elif sponsor_recovery > 0.25:
        signal = "MONITOR — Partial cash-out, some skin still in game"
    else:
        signal = "LOWER RISK — Sponsor retaining majority of equity"

    print(f"  Sponsor recovery of original equity: "
          f"{sponsor_recovery:.0%}")
    print(f"  Signal: {signal}")
    print(f"\n  A sponsor who does a dividend recap is asking:")
    print(f"  'Can I take some money off the table while I still can?'")
    print(f"  That question tells you something about their conviction")
    print(f"  in the business going forward.")
    print(f"{sep}\n")


# ── Run the model ──────────────────────────────────────────

if __name__ == "__main__":

    recap = DividendRecap(
        company_name="MidCo Holdings Pvt Ltd",
        ebitda=100.0,
        existing_debt=400.0,         # ₹400cr existing loan
        existing_rate=0.10,          # 10% rate
        equity_value=200.0,          # ₹200cr sponsor equity
        recap_amount=150.0,          # ₹150cr new debt raised
        recap_rate=0.12,             # 12% on new debt
        leverage_covenant=5.5,       # Max 5.5x covenant
        sponsor_distribution=150.0,  # All recap proceeds to sponsor
    )

    run_recap_analysis(recap)

    # ── How to spot dividend recaps in real life ──
    # Search SEC EDGAR for 8-K filings containing
    # "special dividend" or "dividend recapitalization"
    # Pull the credit agreement filed alongside it
    # Check: what happened to leverage? What happened to covenants?
    # Did the lender grant an amendment to permit this?
    # If yes — what did they receive in exchange?
    # The amendment fee and rate increase tells you
    # how much the lender valued the additional risk.
