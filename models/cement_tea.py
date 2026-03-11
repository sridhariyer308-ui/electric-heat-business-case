"""
cement_tea.py  —  HyperHeat TEA: Cement Rotary Kiln
KEY: 60% of cement CO2 is from calcination (unavoidable chemistry).
     HyperHeat only eliminates the 40% from fuel combustion.
Run: python models/cement_tea.py
"""

PLANT = {
    "cement_output_tonnes":      1_000_000,
    "clinker_ratio":             0.75,
    "heat_gj_per_tonne_clinker": 3.5,
    "operating_hours_per_year":  8_000,
    "installed_gas_power_mw":    120,
}
GAS      = {"efficiency": 0.55, "price_eur_per_kwh": 0.045, "co2_kg_per_kwh": 0.202}
ELECTRIC = {"efficiency": 0.90, "price_eur_per_kwh": 0.12,  "co2_kg_per_kwh": 0.095}
CO2_SPLIT = {"total": 0.65, "calcination": 0.53, "fuel": 0.12}
CARBON   = {"ets_price_2025": 70, "ets_price_2030": 126}
CAPEX    = {"eur_per_kw": 500, "om_pct": 0.02}
FINANCE  = {"wacc": 0.08, "lifetime_years": 15, "price_escalation": 0.02}
GJ_TO_KWH = 277.78

def clinker():          return PLANT["cement_output_tonnes"] * PLANT["clinker_ratio"]
def heat_kwh():         return clinker() * PLANT["heat_gj_per_tonne_clinker"] * GJ_TO_KWH
def energy_in(s):       return heat_kwh() / s["efficiency"]
def elec_mw():          return PLANT["installed_gas_power_mw"] * (GAS["efficiency"] / ELECTRIC["efficiency"])
def energy_cost(s):     return energy_in(s) * s["price_eur_per_kwh"]
def fuel_co2(s):        return energy_in(s) * s["co2_kg_per_kwh"] / 1000
def carbon_fine(s, ets): return fuel_co2(s) * ets
def capex():            return elec_mw() * 1000 * CAPEX["eur_per_kw"]
def savings(ets):       return (energy_cost(GAS) - energy_cost(ELECTRIC)) + (carbon_fine(GAS,ets) - carbon_fine(ELECTRIC,ets))
def payback(ets):       return capex() / savings(ets) if savings(ets) > 0 else None
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
    print(f"   Fuel CO₂: Gas {fuel_co2(GAS):,.0f}t  vs  Electric {fuel_co2(ELECTRIC):,.0f}t")
    print(f"   Carbon fine: Gas {fmt(carbon_fine(GAS,ets))}  vs  Electric {fmt(carbon_fine(ELECTRIC,ets))}")
    print(f"   Annual saving: {fmt(s)}")
    print(f"   CAPEX: {fmt(capex())}  |  Payback: {f'{pb:.1f} yrs' if pb else '❌ Not viable'}  |  NPV: {fmt(n)}  {'✅' if n>0 else '❌'}")

if __name__ == "__main__":
    print("═"*62)
    print("  CEMENT ROTARY KILN TEA  —  2025 Data")
    print("═"*62)
    print(f"\n  CO₂ split: Calcination {CO2_SPLIT['calcination']}t/t (unavoidable) + Fuel {CO2_SPLIT['fuel']}t/t (electric eliminates this)")
    run("CURRENT CASE (grid prices)", CARBON["ets_price_2025"], 0.12)
    run("BEST CASE (PPA + ETS 2030)", CARBON["ets_price_2030"], 0.07)
    ELECTRIC["price_eur_per_kwh"] = 0.07
    saved = fuel_co2(GAS) - fuel_co2(ELECTRIC)
    pct = saved / (PLANT["cement_output_tonnes"] * CO2_SPLIT["total"]) * 100
    print(f"\n── CO₂ IMPACT")
    print(f"   Fuel CO₂ saved: {saved:,.0f} t/year ({pct:.1f}% of total plant CO₂)")
    print(f"   Rest ({100-pct:.1f}%) needs CCS to eliminate calcination CO₂")
    print("═"*62)
```

**Commit changes** karo.

---

## Step 4 — `data/data_sources.csv` banao

**Add file → Create new file → naam: `data/data_sources.csv`**
```
parameter,value,unit,source,url,year
Gas Price,0.045,EUR/kWh,Eurostat + TTF H1 2025,https://ec.europa.eu/eurostat,2025
Electricity Price,0.12,EUR/kWh,Eurostat H1 2025 large industrial,https://ec.europa.eu/eurostat,2025
Electricity PPA Best Case,0.07,EUR/kWh,BNEF PPA Tracker 2025,https://about.bnef.com,2025
EU ETS 2025,70,EUR/tonne CO2,ICE EU ETS market,https://tradingeconomics.com/commodity/carbon,2025
EU ETS 2030 Forecast,126,EUR/tonne CO2,GMK Center / BNEF / S&P Global,https://gmk.center,2025
Steel Heat Demand,1.2,GJ/tonne,IEA Iron & Steel Report 2023,https://iea.org/reports/iron-and-steel,2023
Cement Heat Demand,3.5,GJ/tonne clinker,IEA Cement Report 2023,https://iea.org/reports/cement,2023
Gas CO2 Factor,0.202,kg CO2/kWh,IPCC AR6 / GHG Protocol,https://ghgprotocol.org,2023
Grid CO2 Factor,0.095,kg CO2/kWh,European Environment Agency 2025,https://eea.europa.eu,2025
Cement Calcination CO2,0.53,t CO2/t cement,IPCC AR6,https://ghgprotocol.org/cement,2023
CAPEX,500,EUR/kW,Deep-tech electrification benchmark,,2025
