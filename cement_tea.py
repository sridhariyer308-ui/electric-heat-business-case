"""
cement_tea.py
=============
Techno-Economic Analysis — Cement Rotary Kiln
Compares gas burners vs HyperHeat electric heating system.

Industry  : Cement (Rotary Kiln)
Plant size: 1,000,000 tonnes cement/year
Data year : 2025 actuals

Key difference from steel:
    60% of cement CO₂ comes from calcination (limestone chemistry).
    This CO₂ is UNAVOIDABLE regardless of heat source.
    HyperHeat can only eliminate the remaining 40% (fuel combustion CO₂).

Run:
    python models/cement_tea.py
"""

# ─────────────────────────────────────────────
# ASSUMPTIONS  (all sourced — see data_sources.csv)
# ─────────────────────────────────────────────

PLANT = {
    "cement_output_tonnes":     1_000_000,  # Typical large EU cement plant
    "clinker_ratio":            0.75,        # Cembureau 2024 EU avg (0.75t clinker/t cement)
    "heat_gj_per_tonne_clinker":3.5,         # IEA Cement 2023 — modern dry kiln
    "operating_hours_per_year": 8_000,       # Kilns run near-continuously (91% uptime)
    "installed_gas_power_mw":   120,         # Derived from heat demand
}

GAS = {
    "efficiency":           0.55,           # IEA / Cembureau — 45% lost as exhaust
    "price_eur_per_kwh":    0.045,          # Eurostat + TTF H1 2025
    "co2_kg_per_kwh":       0.202,          # IPCC AR6 / GHG Protocol
}

ELECTRIC = {
    "efficiency":           0.90,           # HyperHeat spec for large rotary kiln
    "price_eur_per_kwh":    0.12,           # Eurostat H1 2025 — large industrial
    "co2_kg_per_kwh":       0.095,          # EEA 2025 EU grid mix
}

# Cement-specific CO2 split
CO2_PER_TONNE_CEMENT = {
    "total":        0.65,   # S&P Global / IEA 2024 — total avg
    "calcination":  0.53,   # IPCC — fixed chemistry, unavoidable
    "fuel":         0.12,   # Total minus calcination — what electric eliminates
}

CARBON = {
    "ets_price_2025":   70,     # ICE EU ETS market 2025
    "ets_price_2030":   126,    # BNEF / GMK Center consensus Dec 2025
}

CAPEX = {
    "eur_per_kw":   500,        # Deep-tech electrification benchmark
    "om_pct":       0.02,       # Industry standard 2% of CAPEX/year
}

FINANCE = {
    "wacc":             0.08,   # Industrial project benchmark
    "lifetime_years":   15,     # HyperHeat design life
    "price_escalation": 0.02,   # IEA long-term outlook
}

GJ_TO_KWH = 277.78


# ─────────────────────────────────────────────
# CORE CALCULATIONS
# ─────────────────────────────────────────────

def clinker_per_year() -> float:
    return PLANT["cement_output_tonnes"] * PLANT["clinker_ratio"]


def total_heat_kwh() -> float:
    """Total useful heat the kiln must deliver (kWh/year)."""
    return clinker_per_year() * PLANT["heat_gj_per_tonne_clinker"] * GJ_TO_KWH


def energy_input_kwh(scenario: dict) -> float:
    """Energy to BUY = useful heat / efficiency."""
    return total_heat_kwh() / scenario["efficiency"]


def electric_capacity_mw() -> float:
    return PLANT["installed_gas_power_mw"] * (GAS["efficiency"] / ELECTRIC["efficiency"])


def annual_energy_cost(scenario: dict) -> float:
    return energy_input_kwh(scenario) * scenario["price_eur_per_kwh"]


def fuel_co2_tonnes(scenario: dict) -> float:
    """CO₂ from burning fuel only (NOT calcination)."""
    return energy_input_kwh(scenario) * scenario["co2_kg_per_kwh"] / 1000


def calcination_co2_tonnes() -> float:
    """
    CO₂ from limestone chemistry — SAME in both scenarios.
    Cannot be avoided without CCS. Not affected by electrification.
    """
    return PLANT["cement_output_tonnes"] * CO2_PER_TONNE_CEMENT["calcination"]


def annual_carbon_cost_fuel_only(scenario: dict, ets_price: float) -> float:
    """Carbon fine on fuel CO₂ only (calcination fine is same in both — cancels out)."""
    return fuel_co2_tonnes(scenario) * ets_price


def annual_om_cost() -> float:
    return electric_capacity_mw() * 1000 * CAPEX["eur_per_kw"] * CAPEX["om_pct"]


def total_capex() -> float:
    return electric_capacity_mw() * 1000 * CAPEX["eur_per_kw"]


def annual_savings(ets_price: float) -> float:
    """
    Net annual saving from switching to electric.
    = (Gas energy cost - Electric energy cost)
    + (Gas fuel CO2 fine - Electric grid CO2 fine)
    Note: calcination CO2 cost is same in both → ignored here.
    """
    energy_saving = annual_energy_cost(GAS) - annual_energy_cost(ELECTRIC)
    carbon_saving = (annual_carbon_cost_fuel_only(GAS, ets_price)
                     - annual_carbon_cost_fuel_only(ELECTRIC, ets_price))
    return energy_saving + carbon_saving  # O&M same, cancels out


def npv(ets_price: float) -> float:
    pv = sum(
        annual_savings(ets_price) * (1 + FINANCE["price_escalation"]) ** yr
        / (1 + FINANCE["wacc"]) ** (yr + 1)
        for yr in range(FINANCE["lifetime_years"])
    )
    return pv - total_capex()


def payback(ets_price: float):
    s = annual_savings(ets_price)
    return total_capex() / s if s > 0 else None


def fuel_co2_reduction() -> float:
    """Annual fuel CO₂ avoided — what HyperHeat actually eliminates."""
    return fuel_co2_tonnes(GAS) - fuel_co2_tonnes(ELECTRIC)


def pct_of_total_co2_saved() -> float:
    total = PLANT["cement_output_tonnes"] * CO2_PER_TONNE_CEMENT["total"]
    return fuel_co2_reduction() / total * 100


# ─────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────

def fmt(n):
    if abs(n) >= 1_000_000:
        return f"€{n/1_000_000:,.2f}M"
    return f"€{n:,.0f}"


def print_scenario(label: str, ets_price: float, elec_price: float = None):
    if elec_price:
        ELECTRIC["price_eur_per_kwh"] = elec_price

    sep = "─" * 64
    s  = annual_savings(ets_price)
    pb = payback(ets_price)
    n  = npv(ets_price)

    print(f"\n  {'─'*60}")
    print(f"  SCENARIO: {label}")
    print(f"  ETS: €{ets_price}/t  |  Electricity: €{ELECTRIC['price_eur_per_kwh']}/kWh")
    print(sep)
    print(f"  {'Item':<38} {'Gas':>12} {'Electric':>12}")
    print(sep)
    print(f"  {'Energy Cost/year':<38} {fmt(annual_energy_cost(GAS)):>12} {fmt(annual_energy_cost(ELECTRIC)):>12}")
    print(f"  {'Fuel CO₂ (tonnes)':<38} {fuel_co2_tonnes(GAS):>11,.0f}t {fuel_co2_tonnes(ELECTRIC):>11,.0f}t")
    print(f"  {'Carbon Fine on Fuel CO₂':<38} {fmt(annual_carbon_cost_fuel_only(GAS,ets_price)):>12} {fmt(annual_carbon_cost_fuel_only(ELECTRIC,ets_price)):>12}")
    print(sep)
    print(f"  {'Annual Saving (energy + carbon)':<38} {fmt(s):>12}")
    print(f"  {'Total CAPEX':<38} {fmt(total_capex()):>12}")
    print(f"  {'Payback':<38} {f'{pb:.1f} years' if pb else '❌ Not viable':>12}")
    print(f"  {'NPV (15yr)':<38} {fmt(n):>12}  {'✅ INVEST' if n>0 else '❌ NOT VIABLE'}")


if __name__ == "__main__":
    print("\n" + "═" * 64)
    print("  HYPERHEAT TEA — CEMENT ROTARY KILN")
    print("  1,000,000 t cement/year  |  2025 Data")
    print("═" * 64)

    # Important context
    print(f"\n  CO₂ BREAKDOWN (per tonne cement):")
    print(f"  Calcination (unavoidable chemistry) : {CO2_PER_TONNE_CEMENT['calcination']} t/t  ← same in both scenarios")
    print(f"  Fuel combustion (what electric fixes): {CO2_PER_TONNE_CEMENT['fuel']} t/t  ← HyperHeat eliminates this")
    print(f"  Total today                          : {CO2_PER_TONNE_CEMENT['total']} t/t")

    print_scenario(
        "CURRENT CASE  (2025 grid prices)",
        ets_price=CARBON["ets_price_2025"],
        elec_price=0.12
    )

    print_scenario(
        "BEST CASE  (PPA + ETS 2030 + green cement premium)",
        ets_price=CARBON["ets_price_2030"],
        elec_price=0.07
    )

    print(f"\n  CO₂ IMPACT OF ELECTRIFICATION")
    print(f"  {'─'*64}")
    ELECTRIC["price_eur_per_kwh"] = 0.07
    print(f"  Fuel CO₂ saved/year    : {fuel_co2_reduction():,.0f} tonnes")
    print(f"  As % of total plant CO₂: {pct_of_total_co2_saved():.1f}%  (rest is calcination)")
    print(f"  Lifetime fuel CO₂ saved: {fuel_co2_reduction()*15:,.0f} tonnes")
    print(f"  Equiv. cars off road   : {fuel_co2_reduction()/1.2:,.0f} cars/year")
    print(f"\n  NOTE: Full decarbonisation requires electrification + CCS")
    print(f"        CCS captures the remaining calcination CO₂ (~60%)")
    print(f"\n{'═'*64}\n")
