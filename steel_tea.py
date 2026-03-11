"""
steel_tea.py
============
Techno-Economic Analysis — Steel Reheating Furnace
Compares gas burners vs HyperHeat electric heating system.

Industry  : Steel (Reheating Furnace)
Plant size: 500,000 tonnes/year
Data year : 2025 actuals

Run:
    python models/steel_tea.py
"""

# ─────────────────────────────────────────────
# ASSUMPTIONS  (all sourced — see data_sources.csv)
# ─────────────────────────────────────────────

PLANT = {
    "annual_production_tonnes": 500_000,    # World Steel Association
    "heat_demand_gj_per_tonne": 1.2,        # IEA Iron & Steel 2023
    "operating_hours_per_year": 7_000,      # Industry avg ~80% utilisation
    "installed_gas_power_mw":   120,        # Derived from heat demand
}

GAS = {
    "efficiency":           0.60,           # IEA / Eurofer — 40% lost as exhaust
    "price_eur_per_kwh":    0.045,          # Eurostat + TTF H1 2025
    "co2_kg_per_kwh":       0.202,          # IPCC AR6 / GHG Protocol
}

ELECTRIC = {
    "efficiency":           0.95,           # HyperHeat spec
    "price_eur_per_kwh":    0.12,           # Eurostat H1 2025 — large industrial
    "co2_kg_per_kwh":       0.095,          # EEA 2025 EU grid mix
}

CARBON = {
    "ets_price_2025":       70,             # ICE EU ETS market 2025
    "ets_price_2030":       126,            # BNEF / GMK Center consensus Dec 2025
}

CAPEX = {
    "eur_per_kw":           500,            # Deep-tech electrification benchmark
    "decommission_eur":     200_000,        # One-time removal of gas burners
    "om_pct":               0.02,           # Industry standard 2% of CAPEX/year
}

FINANCE = {
    "wacc":                 0.08,           # Industrial project benchmark
    "lifetime_years":       15,             # HyperHeat design life
    "price_escalation":     0.02,           # IEA long-term energy outlook
}

GJ_TO_KWH = 277.78  # 1 GJ = 277.78 kWh


# ─────────────────────────────────────────────
# CORE CALCULATIONS
# ─────────────────────────────────────────────

def total_heat_kwh():
    """Total useful heat the furnace must deliver per year (kWh)."""
    return PLANT["annual_production_tonnes"] * PLANT["heat_demand_gj_per_tonne"] * GJ_TO_KWH


def energy_input_kwh(scenario: dict) -> float:
    """
    Energy INPUT to buy — always more than useful heat due to losses.
    Analogy: leaky bucket. Less efficient = more to pour in.
    """
    return total_heat_kwh() / scenario["efficiency"]


def electric_capacity_mw() -> float:
    """Electric capacity needed (MW). Less than gas because efficiency is higher."""
    return PLANT["installed_gas_power_mw"] * (GAS["efficiency"] / ELECTRIC["efficiency"])


def annual_energy_cost(scenario: dict) -> float:
    return energy_input_kwh(scenario) * scenario["price_eur_per_kwh"]


def annual_co2_tonnes(scenario: dict) -> float:
    return energy_input_kwh(scenario) * scenario["co2_kg_per_kwh"] / 1000


def annual_carbon_cost(scenario: dict, ets_price: float) -> float:
    return annual_co2_tonnes(scenario) * ets_price


def annual_om_cost(scenario_label: str) -> float:
    if scenario_label == "electric":
        return electric_capacity_mw() * 1000 * CAPEX["eur_per_kw"] * CAPEX["om_pct"]
    return PLANT["installed_gas_power_mw"] * 1000 * CAPEX["eur_per_kw"] * CAPEX["om_pct"]


def total_annual_cost(scenario: dict, label: str, ets_price: float) -> float:
    return (annual_energy_cost(scenario)
            + annual_carbon_cost(scenario, ets_price)
            + annual_om_cost(label))


def total_capex() -> float:
    return electric_capacity_mw() * 1000 * CAPEX["eur_per_kw"] + CAPEX["decommission_eur"]


def annual_savings(ets_price: float) -> float:
    return (total_annual_cost(GAS, "gas", ets_price)
            - total_annual_cost(ELECTRIC, "electric", ets_price))


def npv(ets_price: float) -> float:
    """Net Present Value over project lifetime at given ETS price."""
    pv = sum(
        annual_savings(ets_price) * (1 + FINANCE["price_escalation"]) ** yr
        / (1 + FINANCE["wacc"]) ** (yr + 1)
        for yr in range(FINANCE["lifetime_years"])
    )
    return pv - total_capex()


def payback(ets_price: float):
    s = annual_savings(ets_price)
    return total_capex() / s if s > 0 else None


def co2_reduction_tonnes() -> float:
    return annual_co2_tonnes(GAS) - annual_co2_tonnes(ELECTRIC)


# ─────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────

def fmt_eur(n):
    if abs(n) >= 1_000_000:
        return f"€{n/1_000_000:,.2f}M"
    return f"€{n:,.0f}"


def print_scenario(label: str, ets_price: float, elec_price: float = None):
    """Print results for a given scenario."""
    if elec_price:
        ELECTRIC["price_eur_per_kwh"] = elec_price

    sep = "─" * 62
    s = annual_savings(ets_price)
    pb = payback(ets_price)
    n = npv(ets_price)

    print(f"\n  {'─'*58}")
    print(f"  SCENARIO: {label}")
    print(f"  ETS: €{ets_price}/t  |  Electricity: €{ELECTRIC['price_eur_per_kwh']}/kWh")
    print(sep)
    print(f"  {'Item':<35} {'Gas':>12} {'Electric':>12}")
    print(sep)
    print(f"  {'Energy Cost/year':<35} {fmt_eur(annual_energy_cost(GAS)):>12} {fmt_eur(annual_energy_cost(ELECTRIC)):>12}")
    print(f"  {'CO₂ Emissions':<35} {annual_co2_tonnes(GAS):>10,.0f}t {annual_co2_tonnes(ELECTRIC):>10,.0f}t")
    print(f"  {'Carbon Fine/year':<35} {fmt_eur(annual_carbon_cost(GAS,ets_price)):>12} {fmt_eur(annual_carbon_cost(ELECTRIC,ets_price)):>12}")
    print(f"  {'O&M/year':<35} {fmt_eur(annual_om_cost('gas')):>12} {fmt_eur(annual_om_cost('electric')):>12}")
    print(sep)
    print(f"  {'TOTAL ANNUAL COST':<35} {fmt_eur(total_annual_cost(GAS,'gas',ets_price)):>12} {fmt_eur(total_annual_cost(ELECTRIC,'electric',ets_price)):>12}")
    print(f"  {'Annual Saving':<35} {fmt_eur(s):>12}")
    print(f"  {'CAPEX':<35} {fmt_eur(total_capex()):>12}")
    print(f"  {'Payback Period':<35} {f'{pb:.1f} years' if pb else '❌ Not viable':>12}")
    print(f"  {'NPV (15yr)':<35} {fmt_eur(n):>12}  {'✅ INVEST' if n>0 else '❌ NOT VIABLE'}")


if __name__ == "__main__":
    print("\n" + "═" * 62)
    print("  HYPERHEAT TEA — STEEL REHEATING FURNACE")
    print("  500,000 t/year  |  2025 Data")
    print("═" * 62)

    # Current case
    print_scenario(
        "CURRENT CASE  (2025 grid prices)",
        ets_price=CARBON["ets_price_2025"],
        elec_price=0.12
    )

    # Best case
    print_scenario(
        "BEST CASE  (PPA + ETS 2030 + Green premium effect)",
        ets_price=CARBON["ets_price_2030"],
        elec_price=0.07
    )

    print(f"\n  CO₂ IMPACT")
    print(f"  {'─'*62}")
    ELECTRIC["price_eur_per_kwh"] = 0.07  # reset to best case for CO2 calc
    print(f"  Annual CO₂ saved      : {co2_reduction_tonnes():,.0f} tonnes/year")
    print(f"  Lifetime CO₂ saved    : {co2_reduction_tonnes()*15:,.0f} tonnes")
    print(f"  Equiv. cars off road  : {co2_reduction_tonnes()/1.2:,.0f} cars/year")
    print(f"\n{'═'*62}\n")
