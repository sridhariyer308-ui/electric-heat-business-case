# Electric Heat Business Case — Industrial Decarbonisation TEA Models

A Techno-Economic Analysis (TEA) of replacing fossil fuel burners with high-temperature electric heating systems in heavy industry — modelled for [HyperHeat](https://hyperheat.com), a Cologne-based deep-tech startup electrifying industrial process heat.

---

## What is this?

Industrial process heat (steel, cement, glass, ceramics) is responsible for ~20% of global CO₂ emissions. Replacing gas burners with electric heating is one of the most impactful — and hardest — decarbonisation levers available.

This repo contains step-by-step Techno-Economic Analysis models for two industries:

| Industry | Temperature | Key Challenge |
|----------|-------------|---------------|
| 🔩 Steel (Reheating Furnace) | ~1200°C | High electricity cost vs gas |
| 🏗️ Cement (Rotary Kiln) | ~1450°C | 60% of CO₂ is unavoidable chemistry (calcination) |

Each model answers one question:

> *"Does it make financial sense to switch from gas burners to electric heating — and what levers make it work?"*

---

## Repository Structure

```
electric-heat-business-case/
│
├── README.md                        ← You are here
├── requirements.txt                 ← Python dependencies
│
├── models/
│   ├── steel_tea.py                 ← Steel plant TEA (current + best case)
│   └── cement_tea.py                ← Cement plant TEA (with calcination split)
│
├── data/
│   └── data_sources.csv             ← Every assumption with source + URL
│
├── excel/
│   ├── Steel_TEA_2025.xlsx          ← Step-by-step Excel model (steel)
│   └── Cement_TEA_2025.xlsx         ← Step-by-step Excel model (cement)
│
└── scripts/
    └── build_excel.py               ← Script to regenerate Excel files
```

---

## Key Findings

### Steel Plant (500,000 t/year)

| Scenario | Annual Cost | Payback |
|----------|-------------|---------|
| Current (grid €0.12/kWh) | Electric costs €6M MORE/year | ❌ Not viable |
| Best case (PPA + ETS 2030) | Electric saves €30M+/year | ✅ ~2 years |

### Cement Plant (1,000,000 t/year)

| Scenario | CO₂ Reduction | Payback |
|----------|---------------|---------|
| Current (grid €0.12/kWh) | 40% of fuel CO₂ | ❌ Not viable |
| Best case (PPA + ETS 2030 + green premium) | 40% fuel CO₂ + carbon savings | ✅ ~3 years |

> **Key Cement insight:** Unlike steel, ~60% of cement CO₂ comes from calcination (chemistry of limestone → lime). This CO₂ is unavoidable without CCS. HyperHeat addresses the remaining 40% from fuel combustion.

---

## The 3 Commercial Levers

Both models are currently NPV-negative at 2025 grid prices. Three levers flip this:

1. **Renewable PPA** — long-term power purchase agreement with wind/solar farm brings electricity from €0.12 → €0.07/kWh
2. **EU ETS Carbon Price** — consensus forecast: €70/tonne (2025) → €126/tonne (2030). Source: BloombergNEF / GMK Center
3. **Green product premium** — buyers paying extra for low-carbon steel/cement. HeidelbergMaterials, Volvo, BMW already active

---

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run Steel TEA
python models/steel_tea.py

# Run Cement TEA
python models/cement_tea.py

# Rebuild Excel files
python scripts/build_excel.py
```

---

## Data Sources

All assumptions are documented in `data/data_sources.csv`. Key sources:

| Parameter | Source |
|-----------|--------|
| Gas price €0.045/kWh | Eurostat + TTF H1 2025 |
| Electricity price €0.12/kWh | Eurostat H1 2025 (large industrial) |
| EU ETS €70/tonne | ICE EU ETS market 2025 |
| ETS 2030 forecast €126/tonne | BloombergNEF / GMK Center Dec 2025 |
| Steel heat demand 1.2 GJ/tonne | IEA Iron & Steel Report 2023 |
| Cement heat demand 3.5 GJ/tonne clinker | IEA Cement Report 2023 |
| Gas CO₂ factor 0.202 kg/kWh | IPCC AR6 / GHG Protocol |
| Grid CO₂ factor 0.095 kg/kWh | European Environment Agency 2025 |



---

## Context

Built as part of application research for the **Business Analyst (Market & Strategy)** role at [HyperHeat GmbH](https://hyperheat.com), Cologne.

HyperHeat builds high-temperature electric heating systems (up to 2000°C) for steel, cement, glass, ceramics and other energy-intensive industries — replacing fossil burners with solutions competitive on economics and performance.

---

## Author

**Sridhar Iyer**
MSc Supply Chain Management — Constructor University Bremen
[sridhariyer308@gmail.com](mailto:sridhariyer308@gmail.com)
[Portfolio](https://sridhariyer308-ui.github.io/portfolio/)
