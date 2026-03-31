"""
Day 02/30 — Private Credit Series
Capital Structure Visualiser

What this does:
  Takes any capital structure as input and outputs:
  - A clean text diagram of the debt building
  - Recovery analysis at different enterprise values
  - Who is the fulcrum security at each EV level

For CA students: this is the balance sheet borrowings note
— but with every layer's risk and return made explicit.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Tranche:
    name: str
    amount: float        # in crore
    rate: float          # annual interest rate
    lien: str            # "Senior Secured", "Mezzanine", "Equity"
    priority: int        # 1 = paid first, higher = paid later


@dataclass
class CapitalStructure:
    company_name: str
    tranches: List[Tranche] = field(default_factory=list)

    def total_debt(self):
        return sum(t.amount for t in self.tranches if t.lien != "Equity")

    def total_value(self):
        return sum(t.amount for t in self.tranches)

    def annual_interest(self):
        return sum(t.amount * t.rate
                   for t in self.tranches if t.lien != "Equity")


def print_building(cs: CapitalStructure):
    """Print the debt building — senior at bottom, equity at top."""

    sep = "=" * 60
    print(f"\n{sep}")
    print(f"  CAPITAL STRUCTURE — {cs.company_name.upper()}")
    print(sep)

    sorted_tranches = sorted(cs.tranches,
                             key=lambda x: x.priority, reverse=True)

    floors = {1: "Ground Floor", 2: "Middle Floor",
              3: "Upper Floor",  4: "Top Floor"}

    for t in sorted_tranches:
        floor = floors.get(t.priority, f"Floor {t.priority}")
        width = int(t.amount / cs.total_value() * 40)
        bar = "█" * width

        print(f"\n  {floor} — {t.lien}")
        print(f"  {bar}")
        print(f"  {t.name}")
        print(f"  ₹{t.amount:.0f} crore | "
              f"{t.rate*100:.1f}% rate | "
              f"Priority: {t.priority}")

    print(f"\n  {'─'*40}")
    print(f"  Total Value:         ₹{cs.total_value():.0f} crore")
    print(f"  Total Debt:          ₹{cs.total_debt():.0f} crore")
    print(f"  Annual Interest:     ₹{cs.annual_interest():.1f} crore")
    print(f"  Debt/Total Value:    "
          f"{cs.total_debt()/cs.total_value():.1%}")
    print(sep)


def recovery_waterfall(cs: CapitalStructure,
                       enterprise_values: List[float]):
    """
    For each EV scenario — who gets paid, who gets wiped out,
    and who is the fulcrum security (where value breaks).
    """

    print(f"\n{'='*60}")
    print(f"  RECOVERY WATERFALL — {cs.company_name.upper()}")
    print(f"{'='*60}")

    sorted_tranches = sorted(cs.tranches, key=lambda x: x.priority)

    col_w = 10
    header = f"  {'Tranche':<24}"
    for ev in enterprise_values:
        header += f"{'₹'+str(int(ev))+'cr':>{col_w}}"
    print(header)
    print(f"  {'─'*60}")

    for t in sorted_tranches:
        row = f"  {t.name:<24}"
        for ev in enterprise_values:
            remaining = ev
            recovery = 0
            for tranche in sorted_tranches:
                if tranche.priority < t.priority:
                    remaining = max(0, remaining - tranche.amount)
                elif tranche.priority == t.priority:
                    recovery = min(remaining, t.amount)
                    break
            pct = recovery / t.amount if t.amount > 0 else 0
            flag = "✓" if pct >= 0.999 else ("~" if pct > 0.5 else "✗")
            cell = f"{pct:.0%}{flag}"
            row += f"{cell:>{col_w}}"
        print(row)

    print(f"\n  Fulcrum security at each EV:")
    for ev in enterprise_values:
        remaining = ev
        fulcrum = None
        for t in sorted_tranches:
            if t.lien == "Equity":
                continue
            if remaining >= t.amount:
                remaining -= t.amount
            else:
                fulcrum = t.name
                break
        print(f"  EV = ₹{ev:.0f}cr → Fulcrum: "
              f"{fulcrum or 'Equity (fully covered)'}")

    print(f"{'='*60}\n")


# ── Run the model ──────────────────────────────────────────

if __name__ == "__main__":

    # Example: PE-backed mid-market company
    # Change these numbers to model any deal

    cs = CapitalStructure(
        company_name="MidCo Holdings Pvt Ltd",
        tranches=[
            Tranche("Senior Secured TL",  400, 0.10, "Senior Secured", 1),
            Tranche("Mezzanine Debt",      150, 0.15, "Mezzanine",      2),
            Tranche("PE Sponsor Equity",   200, 0.00, "Equity",         3),
        ]
    )

    # Print the building
    print_building(cs)

    # Recovery at different enterprise values
    # Bear = company value collapsed
    # Base = moderate stress
    # Good = business performing well
    recovery_waterfall(
        cs,
        enterprise_values=[350, 450, 560, 750, 900]
    )

    # ── Try your own structure ──
    # Uncomment and modify to model a different deal

    # cs2 = CapitalStructure(
    #     company_name="YourCo Ltd",
    #     tranches=[
    #         Tranche("Revolver",        50,  0.095, "Senior Secured", 1),
    #         Tranche("Term Loan A",    300,  0.100, "Senior Secured", 1),
    #         Tranche("Term Loan B",    200,  0.105, "Senior Secured", 1),
    #         Tranche("Second Lien TL", 100,  0.130, "Second Lien",    2),
    #         Tranche("Mezz Note",       75,  0.150, "Mezzanine",      3),
    #         Tranche("Equity",         250,  0.000, "Equity",         4),
    #     ]
    # )
    # print_building(cs2)
    # recovery_waterfall(cs2, [400, 550, 700, 900, 1100])