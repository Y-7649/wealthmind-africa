"""
data/kenya_macro.py
WealthMind Africa — Kenya Macroeconomic Data

Static macro data for the public Kenya Economic Context page.
All figures sourced from World Bank, KNBS, CBK, GSMA, IMF.
Sources and years noted inline for academic transparency.
"""

# ── KENYA MACRO INDICATORS ────────────────────────────────────────────────────
# Each indicator: value, unit, trend direction, source, year, CBK/KNBS target
# Trend: "up", "down", "stable"

KENYA_INDICATORS = [
    {
        "id": "inflation",
        "label": "Headline Inflation",
        "flag": "🇰🇪",
        "value": 4.0,
        "unit": "%",
        "display": "4.0%",
        "trend": "down",
        "trend_label": "↓ Easing from 9.6% peak (2023)",
        "source": "KNBS, May 2025",
        "target": "CBK target: 2.5–7.5%",
        "colour": "#00C49F",
        "short_explanation": (
            "Kenya's consumer price inflation — the rate at which the general price level "
            "is rising. After peaking at 9.6% in mid-2023 driven by global food and energy "
            "price shocks, inflation has returned within the Central Bank of Kenya's target band."
        ),
        "why_matters": (
            "Inflation is the invisible tax on savings. At 4%, a household's real purchasing "
            "power falls by roughly 4% every year. For low-income households — which spend "
            "~55% of income on food (KNBS, 2021) — food inflation above 8% in 2023 was "
            "equivalent to a sharp income cut. The Fisher equation shows why: "
            "real returns = nominal returns − inflation."
        ),
    },
    {
        "id": "gdp_growth",
        "label": "GDP Growth Rate",
        "flag": "📈",
        "value": 5.4,
        "unit": "%",
        "display": "5.4%",
        "trend": "stable",
        "trend_label": "→ Consistent above SSA average",
        "source": "World Bank, 2024",
        "target": "SSA average: 3.5%",
        "colour": "#00C49F",
        "short_explanation": (
            "Kenya's real GDP growth rate. Kenya has consistently grown above the "
            "Sub-Saharan Africa average, driven by services (ICT, finance, telecoms), "
            "agriculture, and infrastructure investment."
        ),
        "why_matters": (
            "GDP growth determines whether rising national income translates into "
            "individual opportunity. Kenya's structural transformation — from agriculture "
            "toward services and manufacturing — mirrors the development paths of "
            "South Korea and Taiwan in earlier decades. The composition matters as much "
            "as the rate: ICT-driven growth (Safaricom contributes ~10% of NSE market cap) "
            "creates different labour market outcomes than commodity-driven growth."
        ),
    },
    {
        "id": "cbk_rate",
        "label": "CBK Policy Rate",
        "flag": "🏦",
        "value": 9.75,
        "unit": "%",
        "display": "9.75%",
        "trend": "down",
        "trend_label": "↓ Down from 13.0% peak (2024)",
        "source": "Central Bank of Kenya, 2025",
        "target": "Neutral rate est. 7–8%",
        "colour": "#FF8800",
        "short_explanation": (
            "The Central Bank Rate (CBR) — Kenya's benchmark monetary policy rate. "
            "The CBK raised rates aggressively through 2023–2024 to combat inflation, "
            "and began easing in 2025 as inflation returned to target."
        ),
        "why_matters": (
            "The CBR is the transmission mechanism of monetary policy. When the CBK raises "
            "rates, commercial bank lending rates follow — making mortgages, business loans, "
            "and consumer credit more expensive. This reduces aggregate demand, cooling "
            "inflation but also slowing growth. The classic Taylor Rule trade-off. "
            "Kenya's relatively high real rate (nominal − inflation ≈ 5.75%) reflects "
            "the premium investors demand for emerging market risk."
        ),
    },
    {
        "id": "unemployment",
        "label": "Unemployment Rate",
        "flag": "👥",
        "value": 12.7,
        "unit": "%",
        "display": "12.7%",
        "trend": "stable",
        "trend_label": "→ Youth unemployment ~35%",
        "source": "KNBS Labour Force Survey, 2023",
        "target": "Youth unemployment: ~35%",
        "colour": "#FF8800",
        "short_explanation": (
            "Kenya's headline unemployment rate. The more economically significant "
            "figure is youth unemployment (~35%), reflecting a structural challenge: "
            "Kenya's working-age population grows by ~800,000 per year, creating "
            "persistent pressure on the formal labour market."
        ),
        "why_matters": (
            "Kenya has one of Africa's youngest populations — median age 19. "
            "The demographic dividend — where a large youth cohort enters the workforce — "
            "can accelerate growth (as in East Asia), but only if the economy creates "
            "sufficient formal employment. Current evidence suggests Kenya's informal "
            "sector (jua kali) absorbs ~83% of employment. This structural underemployment "
            "is a development economics challenge distinct from cyclical unemployment."
        ),
    },
    {
        "id": "population",
        "label": "Population",
        "flag": "🌍",
        "value": 56.4,
        "unit": "M",
        "display": "56.4M",
        "trend": "up",
        "trend_label": "↑ Growing 2.2% per year",
        "source": "World Bank / UN, 2024",
        "target": "Median age: 19 years",
        "colour": "#4499FF",
        "short_explanation": (
            "Kenya's population of 56.4 million, growing at 2.2% annually. "
            "With a median age of 19, Kenya has one of the youngest populations "
            "globally — a defining structural feature of its economic development path."
        ),
        "why_matters": (
            "Population structure shapes everything: savings rates, consumption patterns, "
            "labour supply, and political economy of redistribution. "
            "A young population means lower current savings rates (fewer workers relative "
            "to dependents) but higher future productive capacity. Nairobi's tech startup "
            "ecosystem — Silicon Savannah — reflects what happens when a young, "
            "mobile-first population meets smartphones and M-Pesa."
        ),
    },
    {
        "id": "financial_inclusion",
        "label": "Financial Inclusion",
        "flag": "💳",
        "value": 83.7,
        "unit": "%",
        "display": "83.7%",
        "trend": "up",
        "trend_label": "↑ Up from 26.7% in 2006",
        "source": "FinAccess Household Survey, CBK/KNBS, 2021",
        "target": "Formal inclusion: 56.8%",
        "colour": "#00C49F",
        "short_explanation": (
            "The proportion of Kenyan adults with access to a financial service — "
            "including mobile money. Broad inclusion (83.7%) far exceeds formal bank "
            "inclusion (56.8%) because M-Pesa mobile wallets count as formal services. "
            "In 2006, only 26.7% of Kenyans had any financial service access."
        ),
        "why_matters": (
            "Financial inclusion is one of the most powerful levers in development economics. "
            "Dupas & Robinson (2013) found that access to a basic savings account increased "
            "women's investment in businesses by 40% in Kenya. "
            "Suri & Jack (2016, Science) showed M-Pesa lifted 2% of Kenyan households out "
            "of poverty — one of the most striking policy impact estimates in recent development "
            "economics. Financial access enables consumption smoothing, risk-sharing, and "
            "long-run capital accumulation in ways cash cannot."
        ),
    },
    {
        "id": "mobile_money",
        "label": "Mobile Money Penetration",
        "flag": "📱",
        "value": 75.0,
        "unit": "%",
        "display": "75%",
        "trend": "up",
        "trend_label": "↑ $100B+ transacted annually",
        "source": "GSMA Mobile Money Report, 2024",
        "target": "SSA average: ~25%",
        "colour": "#00C49F",
        "short_explanation": (
            "The proportion of Kenyan adults actively using mobile money services. "
            "Kenya pioneered mobile money with M-Pesa (Safaricom, 2007) and remains "
            "the global benchmark for mobile financial services. Over KES 36 trillion "
            "(≈$250B) flows through M-Pesa annually."
        ),
        "why_matters": (
            "Kenya's mobile money ecosystem is a natural experiment in financial innovation. "
            "M-Pesa solved the problem of formal banking infrastructure being too expensive "
            "to serve rural populations — building a parallel financial system on mobile "
            "network infrastructure instead. The economic implications are significant: "
            "M-Pesa remittances enable consumption smoothing across geographic shocks, "
            "M-Shwari provides credit to previously unbanked borrowers, and M-Akiba allows "
            "government bond investment from KES 3,000 (~$23). Kenya is 15 years ahead "
            "of most markets in mobile finance."
        ),
    },
    {
        "id": "debt_gdp",
        "label": "Public Debt / GDP",
        "flag": "📊",
        "value": 68.4,
        "unit": "%",
        "display": "68.4%",
        "trend": "down",
        "trend_label": "↓ Declining from 73% (2022)",
        "source": "World Bank / IMF, 2024 estimate",
        "target": "IMF sustainability threshold: 60%",
        "colour": "#FF8800",
        "short_explanation": (
            "Kenya's public debt as a percentage of GDP. After rising sharply through "
            "infrastructure investment (SGR railway, roads, energy), debt-to-GDP has "
            "begun declining as revenue collection improves. Kenya's eurobond refinancing "
            "in 2024 resolved a near-term debt rollover risk."
        ),
        "why_matters": (
            "High public debt constrains fiscal space — the government's ability to spend "
            "on health, education, and infrastructure without raising taxes or crowding out "
            "private investment. Kenya's debt is predominantly denominated in USD, creating "
            "foreign exchange risk: a weaker Kenya shilling makes the real debt burden grow. "
            "The debt-to-GDP ratio is a key variable in IMF debt sustainability analyses "
            "and affects Kenya's sovereign credit rating (currently B by S&P) — which in "
            "turn affects the cost of future borrowing."
        ),
    },
]

# ── SSA COMPARISON DATA ───────────────────────────────────────────────────────
# Used for Kenya vs Sub-Saharan Africa comparison charts.
# Source: World Bank World Development Indicators, IMF WEO, GSMA

SSA_COMPARISONS = [
    {
        "metric": "Headline Inflation",
        "kenya": 4.0,
        "ssa": 14.0,
        "unit": "%",
        "kenya_label": "Kenya 4.0%",
        "ssa_label": "SSA avg 14.0%",
        "note": "Kenya's inflation is 10pp below the SSA average, reflecting CBK's credible monetary policy framework.",
        "source": "IMF WEO, 2025 estimate",
    },
    {
        "metric": "GDP Growth",
        "kenya": 5.4,
        "ssa": 3.5,
        "unit": "%",
        "kenya_label": "Kenya 5.4%",
        "ssa_label": "SSA avg 3.5%",
        "note": "Kenya grows ~2pp faster than the SSA average — driven by services, ICT, and manufacturing.",
        "source": "World Bank, 2024",
    },
    {
        "metric": "Financial Inclusion",
        "kenya": 83.7,
        "ssa": 57.0,
        "unit": "%",
        "kenya_label": "Kenya 83.7%",
        "ssa_label": "SSA avg 57.0%",
        "note": "Kenya's financial inclusion rate exceeds the SSA average by 27pp, largely driven by M-Pesa.",
        "source": "World Bank Findex / FinAccess 2021",
    },
    {
        "metric": "Mobile Money Adoption",
        "kenya": 75.0,
        "ssa": 25.0,
        "unit": "%",
        "kenya_label": "Kenya 75%",
        "ssa_label": "SSA avg 25%",
        "note": "Kenya's mobile money penetration is 3× the SSA average — the legacy of M-Pesa's 2007 launch.",
        "source": "GSMA Mobile Money Report, 2024",
    },
]

# ── KENYA GDP GROWTH HISTORY ──────────────────────────────────────────────────
# For trend chart on the context page.
# Source: World Bank national accounts data.

GDP_GROWTH_HISTORY = [
    {"year": 2015, "growth": 5.7},
    {"year": 2016, "growth": 5.9},
    {"year": 2017, "growth": 4.9},
    {"year": 2018, "growth": 6.3},
    {"year": 2019, "growth": 5.4},
    {"year": 2020, "growth": -0.3},   # COVID-19 shock
    {"year": 2021, "growth": 7.5},    # Post-COVID rebound
    {"year": 2022, "growth": 4.8},
    {"year": 2023, "growth": 5.6},
    {"year": 2024, "growth": 5.4},
]

# ── KENYA INFLATION HISTORY ───────────────────────────────────────────────────
# For trend chart.  Source: KNBS CPI Monthly Reports.

INFLATION_HISTORY = [
    {"year": 2019, "rate": 5.2},
    {"year": 2020, "rate": 5.3},
    {"year": 2021, "rate": 6.1},
    {"year": 2022, "rate": 7.7},
    {"year": 2023, "rate": 7.9},   # Peak year average
    {"year": 2024, "rate": 5.5},
    {"year": 2025, "rate": 4.0},   # KNBS estimate
]


# ── HELPER FUNCTIONS ──────────────────────────────────────────────────────────

def get_macro_snapshot() -> list[dict]:
    """Return the list of Kenya macro indicators."""
    return KENYA_INDICATORS


def get_ssa_comparison() -> list[dict]:
    """Return Kenya vs SSA comparison data."""
    return SSA_COMPARISONS


def get_gdp_history() -> list[dict]:
    """Return GDP growth history list."""
    return GDP_GROWTH_HISTORY


def get_inflation_history() -> list[dict]:
    """Return CPI inflation history list."""
    return INFLATION_HISTORY
