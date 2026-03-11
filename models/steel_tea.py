"""
steel_tea.py  —  HyperHeat TEA: Steel Reheating Furnace
Run: python models/steel_tea.py
"""

PLANT = {
    "annual_production_tonnes": 500_000,
    "heat_demand_gj_per_tonne": 1.2,
    "operating_hours_per_year": 7_000,
    "installed_gas_power_mw":   120,
}
GAS      = {"efficiency": 0.60, "price_eur_per_kwh": 0.045, "co2_kg_per_kwh": 0.202}
ELECTRIC = {"efficiency": 0.95, "price_eur_per_kwh": 0.12,  "co2_kg_per_kwh": 0.095}
CARBON   = {"ets_price_2025": 70, "ets_price_2030": 126}
CAPEX    = {"eur_per_kw": 500, "decommission_eur": 200_000, "om_pct": 0.02}
FINANCE  = {"wacc": 0.08, "lifetime_years": 15, "price_escalation": 0.02}
GJ_TO_KWH = 277.78

def total_heat_kwh():
    return PLANT["annual_production_tonnes"] * PLANT["heat_demand_gj_per_tonne"] * GJ_TO_KWH

def energy_input_kwh(s):   return total_heat_kwh() / s["efficiency"]
def electric_mw():         return PLANT["installed_gas_power_mw"] * (GAS["efficiency"] / ELECTRIC["efficiency"])
def energy_cost(s):        return energy_input_kwh(s) * s["price_eur_per_kwh"]
def co2_tonnes(s):         return energy_input_kwh(s) * s["co2_kg_per_kwh"] / 1000
def carbon_cost(s, ets):   return co2_tonnes(s) * ets
def om_cost(label):        return (electric_mw() if label=="electric" else PLANT["installed_gas_power_mw"]) * 1000 * CAPEX["eur_per_kw"] * CAPEX["om_pct"]
def total_cost(s, lbl, ets): return energy_cost(s) + carbon_cost(s, ets) + om_cost(lbl)
def capex():               return electric_mw() * 1000 * CAPEX["eur_per_kw"] + CAPEX["decommission_eur"]
def savings(ets):          return total_cost(GAS,"gas",ets) - total_cost(ELECTRIC,"electric",ets)
def payback(ets):          return capex() / savings(ets) if savings(ets) > 0 else None
def npv(ets):
    pv = sum(savings(ets)*(1+FINANCE["price_escalation"])**y / (1+FINANCE["wacc"])**(y+1) for y in range(FINANCE["lifetime_years"]))
    return pv - capex()
def fmt(n): return f"€{n/1e6:,.2f}M" if abs(n)>=1e6 else f"€{n:,.0f}"

def run(label, ets, elec):
    ELECTRIC["price_eur_per_kwh"] = elec
    s, pb, n = savings(ets), payback(ets), npv(ets)
    print(f"\n── {label}")
    print(f"   ETS €{ets}/t  |  Electricity €{elec}/kWh")
    print(f"   Energy:  Gas {fmt(energy_cost(GAS))}  vs  Electric {fmt(energy_cost(ELECTRIC))}")
    print(f"   CO₂:     Gas {co2_tonnes(GAS):,.0f}t  vs  Electric {co2_tonnes(ELECTRIC):,.0f}t")
    print(f"   Carbon fine: Gas {fmt(carbon_cost(GAS,ets))}  vs  Electric {fmt(carbon_cost(ELECTRIC,ets))}")
    print(f"   Annual saving: {fmt(s)}")
    print(f"   CAPEX: {fmt(capex())}  |  Payback: {f'{pb:.1f} yrs' if pb else '❌ Not viable'}  |  NPV: {fmt(n)}  {'✅' if n>0 else '❌'}")

if __name__ == "__main__":
    print("═"*60)
    print("  STEEL REHEATING FURNACE TEA  —  2025 Data")
    print("═"*60)
    run("CURRENT CASE (grid prices)", CARBON["ets_price_2025"], 0.12)
    run("BEST CASE (PPA + ETS 2030)", CARBON["ets_price_2030"], 0.07)
    ELECTRIC["price_eur_per_kwh"] = 0.07
    print(f"\n── CO₂ IMPACT")
    print(f"   Annual saved: {co2_tonnes(GAS)-co2_tonnes(ELECTRIC):,.0f} t/year")
    print(f"   Equiv cars off road: {(co2_tonnes(GAS)-co2_tonnes(ELECTRIC))/1.2:,.0f}")
    print("═"*60)
