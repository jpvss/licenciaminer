"""LicenciaMiner — Sistema de design 'Geological Editorial'.

Tema inspirado em cartografia geológica e publicações de survey mineral.
Cores derivadas de minerais: âmbar, cobre oxidado, quartzo, basalto.
"""


def get_fonts_css() -> str:
    """Retorna link tags para Google Fonts."""
    return """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Instrument+Sans:ital,wght@0,400..700;1,400..700&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet">
    """


def get_theme_css() -> str:
    """Retorna o CSS completo do tema Geological Editorial."""
    return """
    <style>
    /* ══════════════════════════════════════════════
       DESIGN TOKENS — Geological Editorial
       ══════════════════════════════════════════════ */
    :root {
        --substrate: #0C0E12;
        --stratum-1: #12151B;
        --stratum-2: #1A1E28;
        --stratum-3: #242935;
        --stratum-4: #2E3442;
        --amber: #D4A847;
        --amber-dim: rgba(212, 168, 71, 0.15);
        --amber-glow: rgba(212, 168, 71, 0.08);
        --copper: #C17F59;
        --copper-dim: rgba(193, 127, 89, 0.15);
        --quartz: #E8E4DC;
        --slate: #8B9BB4;
        --slate-dim: #5E6B80;
        --malachite: #5BA77D;
        --malachite-dim: rgba(91, 167, 125, 0.15);
        --oxide: #C45B52;
        --oxide-dim: rgba(196, 91, 82, 0.15);
        --link: #7B9FD4;

        --font-display: 'DM Serif Display', Georgia, serif;
        --font-body: 'Instrument Sans', -apple-system, sans-serif;
        --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 14px;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
        --shadow-md: 0 4px 16px rgba(0,0,0,0.35);
        --shadow-lg: 0 8px 32px rgba(0,0,0,0.4);
        --shadow-glow: 0 0 20px rgba(212, 168, 71, 0.06);
    }

    /* ── Global resets ── */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
        max-width: 1200px !important;
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: var(--font-body) !important;
        color: var(--quartz) !important;
    }

    h1, h2, h3 {
        font-family: var(--font-display) !important;
        color: var(--quartz) !important;
        font-weight: 400 !important;
    }

    /* ── Animations ── */
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 4px rgba(91, 167, 125, 0.3); }
        50% { box-shadow: 0 0 12px rgba(91, 167, 125, 0.6); }
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    .animate-in {
        animation: fadeSlideUp 0.4s ease-out forwards;
    }
    .animate-in-d1 { animation: fadeSlideUp 0.4s ease-out 0.05s forwards; opacity: 0; }
    .animate-in-d2 { animation: fadeSlideUp 0.4s ease-out 0.1s forwards; opacity: 0; }
    .animate-in-d3 { animation: fadeSlideUp 0.4s ease-out 0.15s forwards; opacity: 0; }
    .animate-in-d4 { animation: fadeSlideUp 0.4s ease-out 0.2s forwards; opacity: 0; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--stratum-1); }
    ::-webkit-scrollbar-thumb {
        background: var(--stratum-4);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--amber); }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--stratum-1) !important;
        border-right: 1px solid var(--stratum-3) !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 1rem !important;
    }

    .sidebar-brand {
        padding: 0.8rem 0 1.2rem 0;
        border-bottom: 1px solid var(--stratum-3);
        margin-bottom: 1rem;
    }
    .sidebar-brand h2 {
        font-family: var(--font-display) !important;
        font-size: 1.4rem !important;
        color: var(--quartz) !important;
        margin: 0 !important;
        letter-spacing: -0.01em;
    }
    .sidebar-brand p {
        font-family: var(--font-body) !important;
        font-size: 0.75rem;
        color: var(--slate-dim);
        margin: 4px 0 0 0;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .sidebar-freshness {
        display: flex; align-items: center; gap: 6px;
        padding: 0.5rem 0;
        font-size: 0.72rem;
        color: var(--slate-dim);
        font-family: var(--font-mono);
        border-top: 1px solid var(--stratum-3);
        margin-top: 1rem;
    }
    .sidebar-freshness .dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        background: var(--malachite);
        animation: pulseGlow 2s ease-in-out infinite;
        flex-shrink: 0;
    }

    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: var(--stratum-2) !important;
        border: 1px solid var(--stratum-3) !important;
        border-top: 2px solid var(--amber) !important;
        border-radius: var(--radius-md) !important;
        padding: 1rem 1.2rem !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        border-top-color: var(--amber) !important;
        box-shadow: var(--shadow-md), var(--shadow-glow) !important;
        transform: translateY(-1px);
    }
    [data-testid="stMetricValue"] {
        font-family: var(--font-display) !important;
        font-size: 1.7rem !important;
        color: var(--amber) !important;
        font-weight: 400 !important;
    }
    [data-testid="stMetricLabel"] {
        font-family: var(--font-body) !important;
        font-size: 0.78rem !important;
        color: var(--slate) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }

    /* Variant: copper accent */
    .metric-copper [data-testid="stMetric"] {
        border-top-color: var(--copper) !important;
    }
    .metric-copper [data-testid="stMetricValue"] {
        color: var(--copper) !important;
    }
    /* Variant: slate accent */
    .metric-slate [data-testid="stMetric"] {
        border-top-color: var(--slate) !important;
    }
    .metric-slate [data-testid="stMetricValue"] {
        color: var(--slate) !important;
    }
    /* Variant: malachite accent */
    .metric-malachite [data-testid="stMetric"] {
        border-top-color: var(--malachite) !important;
    }
    .metric-malachite [data-testid="stMetricValue"] {
        color: var(--malachite) !important;
    }

    /* ── Section headers ── */
    .geo-section {
        font-family: var(--font-body);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: var(--slate-dim);
        margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid var(--stratum-3);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .geo-section::before {
        content: '';
        width: 3px; height: 12px;
        background: var(--amber);
        border-radius: 1px;
        flex-shrink: 0;
    }

    /* ── Insight cards ── */
    .geo-insight {
        background: var(--stratum-2);
        border: 1px solid var(--stratum-3);
        border-left: 3px solid var(--amber);
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.6rem;
        transition: all 0.2s ease;
    }
    .geo-insight:hover {
        border-left-color: var(--amber);
        background: var(--stratum-3);
    }
    .geo-insight.positive { border-left-color: var(--malachite); }
    .geo-insight.negative { border-left-color: var(--oxide); }
    .geo-insight.neutral { border-left-color: var(--slate); }

    .geo-insight .insight-label {
        font-family: var(--font-body);
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--slate-dim);
        margin: 0 0 2px 0;
    }
    .geo-insight .insight-value {
        font-family: var(--font-display);
        font-size: 1.35rem;
        color: var(--quartz);
        margin: 0;
        line-height: 1.2;
    }
    .geo-insight .insight-context {
        font-family: var(--font-body);
        font-size: 0.8rem;
        color: var(--slate);
        margin: 4px 0 0 0;
    }

    /* ── Source table ── */
    .geo-source-grid {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 0.5fr;
        gap: 0;
        font-family: var(--font-body);
        font-size: 0.82rem;
    }
    .geo-source-header {
        padding: 0.5rem 0.6rem;
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--slate-dim);
        border-bottom: 1px solid var(--stratum-4);
    }
    .geo-source-cell {
        padding: 0.55rem 0.6rem;
        border-bottom: 1px solid var(--stratum-2);
        display: flex;
        align-items: center;
        transition: background 0.15s ease;
    }
    .geo-source-row:hover .geo-source-cell {
        background: var(--stratum-2);
    }
    .geo-source-name { color: var(--quartz); font-weight: 500; }
    .geo-source-count {
        color: var(--amber);
        font-family: var(--font-mono);
        font-weight: 500;
        font-size: 0.8rem;
    }
    .geo-source-date {
        font-family: var(--font-mono);
        font-size: 0.75rem;
    }
    .geo-source-link a {
        color: var(--link);
        text-decoration: none;
        font-size: 0.75rem;
        opacity: 0.7;
        transition: opacity 0.15s ease;
    }
    .geo-source-link a:hover { opacity: 1; }

    .status-dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        flex-shrink: 0;
    }
    .status-fresh { background: var(--malachite); }
    .status-stale { background: var(--oxide); }

    /* ── Case cards ── */
    .geo-case {
        background: var(--stratum-2);
        border: 1px solid var(--stratum-3);
        border-radius: var(--radius-md);
        padding: 1rem 1.2rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }
    .geo-case:hover {
        border-color: var(--stratum-4);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    .geo-case .case-icon {
        font-size: 1.5rem;
        flex-shrink: 0;
        line-height: 1;
        margin-top: 2px;
    }
    .geo-case .case-body { flex: 1; min-width: 0; }
    .geo-case .case-title {
        font-family: var(--font-body);
        font-weight: 600;
        color: var(--quartz);
        font-size: 0.9rem;
        margin: 0 0 4px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .geo-case .case-meta {
        font-family: var(--font-mono);
        font-size: 0.72rem;
        color: var(--slate-dim);
        margin: 0;
    }
    .geo-case .case-badge {
        flex-shrink: 0;
        padding: 3px 10px;
        border-radius: 20px;
        font-family: var(--font-mono);
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 0.03em;
    }
    .badge-deferido {
        background: var(--malachite-dim);
        color: var(--malachite);
    }
    .badge-indeferido {
        background: var(--oxide-dim);
        color: var(--oxide);
    }
    .badge-arquivamento {
        background: rgba(139, 155, 180, 0.15);
        color: var(--slate);
    }

    /* ── Detail record card ── */
    .geo-detail {
        background: var(--stratum-2);
        border: 1px solid var(--stratum-3);
        border-left: 3px solid var(--amber);
        border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
        padding: 1.3rem 1.5rem;
        margin: 0.5rem 0;
        animation: fadeSlideUp 0.3s ease-out;
    }
    .geo-detail .detail-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1rem;
    }
    .geo-detail .detail-title {
        font-family: var(--font-display);
        font-size: 1.15rem;
        color: var(--quartz);
        margin: 0;
        flex: 1;
    }
    .geo-detail .detail-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.8rem 2rem;
        margin-bottom: 1rem;
    }
    .geo-detail .detail-field {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .geo-detail .detail-label {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--slate-dim);
        font-family: var(--font-body);
    }
    .geo-detail .detail-value {
        font-size: 0.88rem;
        color: var(--quartz);
        font-family: var(--font-body);
    }
    .geo-detail .detail-value.mono {
        font-family: var(--font-mono);
        font-size: 0.82rem;
    }
    .geo-detail .detail-actions {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 0.8rem;
        padding-top: 0.8rem;
        border-top: 1px solid var(--stratum-3);
    }
    .geo-detail .detail-actions a {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 5px 12px;
        border-radius: var(--radius-sm);
        font-size: 0.78rem;
        font-family: var(--font-body);
        text-decoration: none;
        transition: all 0.15s ease;
        border: 1px solid var(--stratum-4);
        color: var(--slate);
        background: transparent;
    }
    .geo-detail .detail-actions a:hover {
        border-color: var(--amber);
        color: var(--amber);
        background: var(--amber-glow);
    }

    /* ── Company dossier ── */
    .geo-dossier {
        background: var(--stratum-2);
        border: 1px solid var(--stratum-3);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin: 0.5rem 0;
    }
    .geo-dossier .dossier-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid var(--stratum-3);
    }
    .geo-dossier .dossier-name {
        font-family: var(--font-display);
        font-size: 1.2rem;
        color: var(--quartz);
        margin: 0;
    }
    .geo-dossier .dossier-cnae {
        font-family: var(--font-mono);
        font-size: 0.72rem;
        color: var(--slate);
        background: var(--stratum-3);
        padding: 2px 8px;
        border-radius: var(--radius-sm);
    }

    .geo-kpi-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.8rem;
        margin: 0.8rem 0;
    }
    .geo-kpi {
        background: var(--stratum-3);
        border-radius: var(--radius-sm);
        padding: 0.7rem 0.9rem;
        text-align: center;
    }
    .geo-kpi .kpi-value {
        font-family: var(--font-display);
        font-size: 1.1rem;
        color: var(--amber);
        margin: 0;
    }
    .geo-kpi .kpi-label {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--slate-dim);
        margin: 2px 0 0 0;
    }

    /* ── Navigation cards (landing) ── */
    .geo-nav-card {
        background: var(--stratum-2);
        border: 1px solid var(--stratum-3);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        transition: all 0.25s ease;
        cursor: pointer;
        text-decoration: none !important;
        display: block;
    }
    .geo-nav-card:hover {
        border-color: var(--amber);
        box-shadow: var(--shadow-lg), var(--shadow-glow);
        transform: translateY(-3px);
    }

    /* Style page_link elements as nav cards */
    [data-testid="stPageLink-nav"] a {
        background: var(--stratum-2) !important;
        border: 1px solid var(--stratum-3) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.5rem !important;
        transition: all 0.25s ease !important;
        min-height: 180px;
        display: flex !important;
        flex-direction: column;
        justify-content: flex-start;
        text-decoration: none !important;
        white-space: normal !important;
    }
    [data-testid="stPageLink-nav"] a:hover {
        border-color: var(--amber) !important;
        box-shadow: var(--shadow-lg), var(--shadow-glow) !important;
        transform: translateY(-3px);
    }
    [data-testid="stPageLink-nav"] a p {
        font-family: var(--font-body);
        font-size: 0.85rem;
        color: var(--slate);
        line-height: 1.45;
        margin: 0;
    }
    [data-testid="stPageLink-nav"] a p strong {
        font-family: var(--font-display);
        font-size: 1.1rem;
        color: var(--quartz);
        display: block;
        margin-bottom: 0.4rem;
    }
    [data-testid="stPageLink-nav"] a p code {
        font-family: var(--font-mono);
        font-size: 0.75rem;
        color: var(--amber);
        padding: 3px 8px;
        background: var(--amber-dim);
        border-radius: var(--radius-sm);
        display: inline-block;
        margin-top: 0.6rem;
    }
    .geo-nav-card .nav-icon {
        font-size: 1.8rem;
        margin-bottom: 0.6rem;
        display: block;
    }
    .geo-nav-card .nav-title {
        font-family: var(--font-display);
        font-size: 1.15rem;
        color: var(--quartz);
        margin: 0 0 6px 0;
    }
    .geo-nav-card .nav-desc {
        font-size: 0.82rem;
        color: var(--slate);
        margin: 0 0 0.8rem 0;
        line-height: 1.45;
    }
    .geo-nav-card .nav-stat {
        font-family: var(--font-mono);
        font-size: 0.75rem;
        color: var(--amber);
        padding: 3px 8px;
        background: var(--amber-dim);
        border-radius: var(--radius-sm);
        display: inline-block;
    }

    /* ── Donut chart (SVG) ── */
    .geo-donut {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        gap: 4px;
    }
    .geo-donut svg { filter: drop-shadow(0 2px 8px rgba(0,0,0,0.3)); }
    .geo-donut .donut-label {
        font-family: var(--font-body);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--slate-dim);
        margin-top: 4px;
    }

    /* ── Hero section ── */
    .geo-hero {
        padding: 2rem 0 1.5rem 0;
        position: relative;
        margin-bottom: 1rem;
    }
    .geo-hero h1 {
        font-family: var(--font-display) !important;
        font-size: 2.2rem !important;
        color: var(--quartz) !important;
        margin: 0 0 6px 0 !important;
        line-height: 1.1 !important;
    }
    .geo-hero .hero-sub {
        font-family: var(--font-body);
        font-size: 0.88rem;
        color: var(--slate);
        margin: 0;
        letter-spacing: 0.01em;
    }
    .geo-hero .hero-rule {
        width: 50px; height: 2px;
        background: var(--amber);
        margin: 1rem 0 0 0;
        border-radius: 1px;
    }

    /* ── Filter chips ── */
    .geo-chip {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 10px;
        border-radius: 20px;
        font-family: var(--font-mono);
        font-size: 0.7rem;
        background: var(--amber-dim);
        color: var(--amber);
        margin: 0 4px 4px 0;
    }

    /* ── Comparison bar ── */
    .geo-compare-bar {
        background: var(--stratum-3);
        border-radius: 4px;
        height: 8px;
        overflow: hidden;
        position: relative;
    }
    .geo-compare-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.6s ease;
    }
    .geo-compare-marker {
        position: absolute;
        top: -3px;
        width: 2px;
        height: 14px;
        background: var(--quartz);
        border-radius: 1px;
    }

    /* ── Empty states ── */
    .geo-empty {
        text-align: center;
        padding: 2.5rem 1rem;
        color: var(--slate-dim);
    }
    .geo-empty .empty-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .geo-empty .empty-text {
        font-size: 0.85rem;
        font-family: var(--font-body);
    }

    /* ── Source attribution ── */
    .geo-source {
        font-family: var(--font-mono);
        font-size: 0.68rem;
        color: var(--slate-dim);
        letter-spacing: 0.02em;
        margin-top: 4px;
    }

    /* ── DataFrames ── */
    [data-testid="stDataFrame"] {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--stratum-3) !important;
    }

    /* ── Expanders ── */
    [data-testid="stExpander"] {
        border: 1px solid var(--stratum-3) !important;
        border-radius: var(--radius-md) !important;
        background: var(--stratum-2) !important;
    }

    /* ── Buttons ── */
    .stButton > button[kind="primary"] {
        background: var(--amber) !important;
        color: var(--substrate) !important;
        font-family: var(--font-body) !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        letter-spacing: 0.02em;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 4px 16px rgba(212, 168, 71, 0.25) !important;
        transform: translateY(-1px);
    }
    .stDownloadButton > button {
        border: 1px solid var(--stratum-4) !important;
        border-radius: var(--radius-sm) !important;
        font-family: var(--font-body) !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton > button:hover {
        border-color: var(--amber) !important;
        color: var(--amber) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        border-bottom: 1px solid var(--stratum-3);
    }
    .stTabs [data-baseweb="tab"] {
        font-family: var(--font-body) !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.02em;
        padding: 0.6rem 1.2rem !important;
        border-bottom: 2px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        border-bottom-color: var(--amber) !important;
        color: var(--amber) !important;
    }

    /* ── Warning/Info boxes ── */
    [data-testid="stAlert"] {
        border-radius: var(--radius-md) !important;
        font-family: var(--font-body) !important;
    }

    /* ── Text inputs ── */
    .stTextInput > div > div > input {
        font-family: var(--font-body) !important;
        border-radius: var(--radius-sm) !important;
    }
    .stSelectbox > div > div {
        border-radius: var(--radius-sm) !important;
    }
    </style>
    """


def inject_theme(st_module) -> None:
    """Injeta fontes e CSS do tema na página Streamlit."""
    st_module.markdown(get_fonts_css(), unsafe_allow_html=True)
    st_module.markdown(get_theme_css(), unsafe_allow_html=True)


# ── HTML component helpers ──

def hero_html(title: str, subtitle: str) -> str:
    """Retorna HTML do hero section."""
    return f"""
    <div class="geo-hero animate-in">
        <h1>{title}</h1>
        <p class="hero-sub">{subtitle}</p>
        <div class="hero-rule"></div>
    </div>
    """


def section_header(text: str) -> str:
    """Retorna HTML de section header."""
    return f'<div class="geo-section">{text}</div>'


def insight_card(label: str, value: str, context: str,
                 tone: str = "neutral") -> str:
    """Retorna HTML de insight card. tone: neutral, positive, negative."""
    return f"""
    <div class="geo-insight {tone}">
        <p class="insight-label">{label}</p>
        <p class="insight-value">{value}</p>
        <p class="insight-context">{context}</p>
    </div>
    """


def case_card_html(icon: str, title: str, meta: str,
                   badge_text: str, badge_class: str) -> str:
    """Retorna HTML de case card."""
    return f"""
    <div class="geo-case">
        <span class="case-icon">{icon}</span>
        <div class="case-body">
            <p class="case-title">{title}</p>
            <p class="case-meta">{meta}</p>
        </div>
        <span class="case-badge {badge_class}">{badge_text}</span>
    </div>
    """


def decision_badge(decisao: str) -> str:
    """Retorna badge HTML para uma decisão."""
    config = {
        "deferido": ("Deferido", "badge-deferido"),
        "indeferido": ("Indeferido", "badge-indeferido"),
        "arquivamento": ("Arquivamento", "badge-arquivamento"),
    }
    text, cls = config.get(decisao, (decisao, "badge-arquivamento"))
    return f'<span class="case-badge {cls}">{text}</span>'


def donut_svg(percentage: float, size: int = 90, stroke: int = 8,
              color: str = "var(--amber)") -> str:
    """Retorna SVG de donut chart com percentual no centro."""
    radius = (size - stroke) / 2
    circumference = 2 * 3.14159 * radius
    filled = circumference * percentage / 100
    gap = circumference - filled

    return f"""
    <div class="geo-donut">
        <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
            <circle cx="{size/2}" cy="{size/2}" r="{radius}"
                fill="none" stroke="var(--stratum-3)" stroke-width="{stroke}"/>
            <circle cx="{size/2}" cy="{size/2}" r="{radius}"
                fill="none" stroke="{color}" stroke-width="{stroke}"
                stroke-dasharray="{filled} {gap}"
                stroke-linecap="round"
                transform="rotate(-90 {size/2} {size/2})"
                style="transition: stroke-dasharray 0.8s ease;"/>
            <text x="{size/2}" y="{size/2 + 1}"
                text-anchor="middle" dominant-baseline="middle"
                font-family="var(--font-display)" font-size="{size * 0.22}"
                fill="var(--quartz)">{percentage:.0f}%</text>
        </svg>
    </div>
    """


def empty_state(icon: str, text: str) -> str:
    """Retorna HTML de empty state."""
    return f"""
    <div class="geo-empty">
        <div class="empty-icon">{icon}</div>
        <p class="empty-text">{text}</p>
    </div>
    """


def source_attribution(text: str) -> str:
    """Retorna HTML de fonte."""
    return f'<p class="geo-source">{text}</p>'
