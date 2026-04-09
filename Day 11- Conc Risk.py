"""
Day 11 — Concentration Risk Analyser
Private Credit Series

What it does:
  - Takes a company's customer revenue breakdown
  - Calculates concentration metrics (HHI, top-customer share)
  - Models the binary event: what happens to EBITDA and FCF if the top customer leaves
  - Stress tests FCF at different contribution margin assumptions
  - Flags whether the credit is safe to approve given concentration

CA student connection:
  In audit you verify revenue from major customers in related party notes.
  In credit you model what happens to cash flow if that customer disappears.
"""

def analyse_concentration(
    customers: dict,       # {customer_name: revenue_amount}
    total_revenue: float,
    ebitda: float,
    fixed_costs: float,    # costs that do not reduce if revenue falls
    variable_margin: float, # contribution margin as % of revenue (0.0 to 1.0)
    debt_interest: float,
    mandatory_repayment: float,
    capex: float,
    working_capital: float
):
    print("=" * 60)
    print("CONCENTRATION RISK ANALYSIS")
    print("=" * 60)

    # ── 1. Customer concentration ──────────────────────────────
    print("\n1. CUSTOMER BREAKDOWN")
    print(f"   {'Customer':<25} {'Revenue (cr)':>12} {'Share':>8} {'Flag':>6}")
    print("   " + "-" * 55)

    shares = {}
    for name, rev in sorted(customers.items(), key=lambda x: -x[1]):
        share = rev / total_revenue * 100
        shares[name] = share
        flag = " 🔴" if share >= 20 else (" 🟡" if share >= 15 else "")
        print(f"   {name:<25} {rev:>12,.1f} {share:>7.1f}%{flag}")

    top_name = max(customers, key=customers.get)
    top_rev = customers[top_name]
    top_share = shares[top_name]

    # Herfindahl-Hirschman Index (market concentration measure)
    hhi = sum((s / 100) ** 2 for s in shares.values()) * 10000
    print(f"\n   Total revenue:  ₹{total_revenue:,.1f} cr")
    print(f"   HHI score:      {hhi:.0f}  (>2500 = highly concentrated)")
    print(f"   Top customer:   {top_name} at {top_share:.1f}%")

    # ── 2. Base case FCF ──────────────────────────────────────
    print("\n2. BASE CASE FREE CASH FLOW")
    fcf_base = (ebitda
                - debt_interest
                - mandatory_repayment
                - capex
                - working_capital)
    print(f"   EBITDA:                   ₹{ebitda:>8,.1f} cr")
    print(f"   Less: interest:          -₹{debt_interest:>8,.1f} cr")
    print(f"   Less: debt repayment:    -₹{mandatory_repayment:>8,.1f} cr")
    print(f"   Less: capex:             -₹{capex:>8,.1f} cr")
    print(f"   Less: working capital:   -₹{working_capital:>8,.1f} cr")
    print(f"   ───────────────────────────────────────")
    print(f"   FREE CASH FLOW:           ₹{fcf_base:>8,.1f} cr")
    status = "✓ Positive" if fcf_base > 0 else "✗ Negative"
    print(f"   Status: {status}")

    # ── 3. Binary event — top customer leaves ────────────────
    print(f"\n3. BINARY EVENT — {top_name.upper()} LEAVES")
    print(f"   Revenue lost:  ₹{top_rev:,.1f} cr  ({top_share:.1f}% of total)")

    # Contribution margin lost = revenue × variable margin
    contribution_lost = top_rev * variable_margin
    # Fixed costs stay the same — only variable contribution disappears
    ebitda_stressed = ebitda - contribution_lost
    fcf_stressed = (ebitda_stressed
                    - debt_interest
                    - mandatory_repayment
                    - capex
                    - working_capital)

    print(f"   Contribution margin lost: ₹{contribution_lost:>8,.1f} cr")
    print(f"   EBITDA (stressed):        ₹{ebitda_stressed:>8,.1f} cr")
    print(f"   FCF (stressed):           ₹{fcf_stressed:>8,.1f} cr")

    ebitda_drop_pct = (contribution_lost / ebitda) * 100
    fcf_drop_pct = ((fcf_base - fcf_stressed) / abs(fcf_base)) * 100 if fcf_base != 0 else 0

    print(f"\n   EBITDA drops:  {ebitda_drop_pct:.1f}%")
    print(f"   FCF drops:     {fcf_drop_pct:.1f}%  ← this is the non-linear effect")

    if fcf_stressed < 0:
        print(f"\n   ⚠ FCF turns NEGATIVE in binary event scenario")
        print(f"   Company cannot service debt if {top_name} leaves")
    else:
        print(f"\n   ✓ FCF remains positive — manageable stress")

    # ── 4. Contribution margin sensitivity ───────────────────
    print("\n4. FCF SENSITIVITY TO CONTRIBUTION MARGIN ASSUMPTION")
    print(f"   {'Contribution margin':>20} {'EBITDA stressed':>16} {'FCF stressed':>13} {'Status':>10}")
    print("   " + "-" * 63)

    for margin in [0.25, 0.35, 0.45, 0.55, 0.65]:
        cl = top_rev * margin
        ebitda_s = ebitda - cl
        fcf_s = ebitda_s - debt_interest - mandatory_repayment - capex - working_capital
        status_s = "✓ OK" if fcf_s >= 0 else "✗ DEFAULT RISK"
        print(f"   {margin*100:>19.0f}%  ₹{ebitda_s:>12,.1f} cr  ₹{fcf_s:>10,.1f} cr  {status_s}")

    # ── 5. Credit decision ────────────────────────────────────
    print("\n5. CREDIT DECISION FRAMEWORK")
    print("   " + "-" * 55)

    issues = []
    if top_share >= 30:
        issues.append(f"CRITICAL: {top_name} at {top_share:.1f}% — single-name risk unacceptable")
    elif top_share >= 20:
        issues.append(f"WATCH: {top_name} at {top_share:.1f}% — binary scenario required in model")
    if fcf_stressed < 0:
        issues.append("Binary event produces negative FCF — covenant breach likely")
    if hhi > 2500:
        issues.append(f"HHI {hhi:.0f} — portfolio highly concentrated overall")

    if issues:
        print("   Issues flagged:")
        for i in issues:
            print(f"   → {i}")
    else:
        print("   No concentration flags — diversification is adequate")

    print("\n   Mitigants to seek if proceeding:")
    print("   → Multi-year contract with renewal evidence for top customer")
    print("   → Key customer concentration carve-out in covenant (cure period)")
    print("   → Revenue covenant: if top customer share exceeds 25%, trigger review")
    print("   → Require audited customer revenue breakdown in quarterly compliance")
    print("=" * 60)


# ── Run with example ──────────────────────────────────────────
if __name__ == "__main__":
    customers = {
        "MegaCorp Ltd":     420,   # 42% — red flag
        "Infra Services":   180,
        "TechPlatform Co":  140,
        "Regional Buyer":    80,
        "Others (combined)": 180,
    }

    analyse_concentration(
        customers           = customers,
        total_revenue       = 1000,
        ebitda              = 100,
        fixed_costs         = 55,
        variable_margin     = 0.45,   # 45 paise of every rupee is variable contribution
        debt_interest       = 25,
        mandatory_repayment = 5,
        capex               = 10,
        working_capital     = 10,
    )
