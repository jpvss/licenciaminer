"""Summo Quartile — Design system 'Consultoria Estratégica'.

Tema inspirado na identidade visual da apresentação do Produto Ambiental.
Paleta: azul-marinho institucional, laranja de destaque, fundo claro premium.
Tipografia profissional com hierarquia clara e espaçamentos generosos.
"""


def get_fonts_css() -> str:
    """Retorna link tags para Google Fonts."""
    return """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Serif+Display:ital@0;1&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet">
    """


def get_theme_css() -> str:
    """Retorna o CSS completo do tema Consultoria Estratégica."""
    return """
    <style>
    /* ── Hide Streamlit chrome (keep header for sidebar toggle) ── */
    .stDeployButton, footer, #MainMenu {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    /* ══════════════════════════════════════════════
       DESIGN TOKENS — Consultoria Estratégica
       Inspired by Apresentação Produto Ambiental
       ══════════════════════════════════════════════ */
    :root {
        /* ── Core brand palette ── */
        --navy: #1A2C42;
        --navy-deep: #0F1A2A;
        --navy-light: #243B55;
        --charcoal: #2C3E50;
        --teal: #156082;
        --teal-light: #1B7BA3;
        --blue: #2980B9;
        --blue-light: #3498DB;
        --orange: #FF5F00;
        --orange-soft: #FF7A2E;
        --orange-dim: rgba(255, 95, 0, 0.08);
        --orange-glow: rgba(255, 95, 0, 0.12);
        --gold: #FFC000;
        --gold-dim: rgba(255, 192, 0, 0.10);

        /* ── Semantic colors ── */
        --success: #27AE60;
        --success-dim: rgba(39, 174, 96, 0.08);
        --success-light: #2ECC71;
        --warning: #F39C12;
        --warning-dim: rgba(243, 156, 18, 0.08);
        --danger: #E74C3C;
        --danger-dim: rgba(231, 76, 60, 0.08);
        --info: #2980B9;
        --info-dim: rgba(41, 128, 185, 0.08);

        /* ── Surface system (light mode) ── */
        --bg: #F8F9FB;
        --surface: #FFFFFF;
        --surface-raised: #FFFFFF;
        --surface-hover: #F1F3F7;
        --surface-muted: #F0F2F6;
        --border: #E2E6ED;
        --border-light: #EDF0F5;
        --border-focus: #2980B9;

        /* ── Text hierarchy ── */
        --text-primary: #1A2C42;
        --text-secondary: #4A5568;
        --text-tertiary: #8896A6;
        --text-muted: #A0AEC0;
        --text-inverse: #FFFFFF;

        /* ── Typography ── */
        --font-display: 'DM Serif Display', Georgia, serif;
        --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

        /* ── Spacing & Radius ── */
        --radius-xs: 4px;
        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 14px;
        --radius-xl: 20px;

        /* ── Shadows ── */
        --shadow-xs: 0 1px 2px rgba(26, 44, 66, 0.04);
        --shadow-sm: 0 1px 3px rgba(26, 44, 66, 0.06), 0 1px 2px rgba(26, 44, 66, 0.04);
        --shadow-md: 0 4px 12px rgba(26, 44, 66, 0.08), 0 2px 4px rgba(26, 44, 66, 0.04);
        --shadow-lg: 0 10px 30px rgba(26, 44, 66, 0.10), 0 4px 8px rgba(26, 44, 66, 0.04);
        --shadow-xl: 0 20px 50px rgba(26, 44, 66, 0.12);
        --shadow-orange: 0 4px 16px rgba(255, 95, 0, 0.15);
        --shadow-blue: 0 4px 16px rgba(41, 128, 185, 0.15);
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
        0%, 100% { box-shadow: 0 0 4px rgba(39, 174, 96, 0.3); }
        50% { box-shadow: 0 0 12px rgba(39, 174, 96, 0.6); }
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-16px); }
        to { opacity: 1; transform: translateX(0); }
    }

    .animate-in { animation: fadeSlideUp 0.4s ease-out forwards; }
    .animate-in-d1 { animation: fadeSlideUp 0.4s ease-out 0.05s forwards; opacity: 0; }
    .animate-in-d2 { animation: fadeSlideUp 0.4s ease-out 0.10s forwards; opacity: 0; }
    .animate-in-d3 { animation: fadeSlideUp 0.4s ease-out 0.15s forwards; opacity: 0; }
    .animate-in-d4 { animation: fadeSlideUp 0.4s ease-out 0.20s forwards; opacity: 0; }

    /* ── Global resets ── */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
        max-width: 1280px !important;
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: var(--font-body) !important;
        color: var(--text-primary) !important;
        background-color: var(--bg) !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        background-color: var(--bg) !important;
    }

    h1, h2, h3 {
        font-family: var(--font-display) !important;
        color: var(--navy) !important;
        font-weight: 400 !important;
    }

    h4, h5, h6 {
        font-family: var(--font-body) !important;
        color: var(--charcoal) !important;
        font-weight: 600 !important;
    }

    p, li, span, label, .stMarkdown {
        color: var(--text-secondary) !important;
    }

    strong, b {
        color: var(--text-primary) !important;
    }

    a {
        color: var(--blue) !important;
        text-decoration: none !important;
        transition: color 0.15s ease;
    }
    a:hover {
        color: var(--teal) !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-tertiary); }

    /* ══════════════════════════════════════════════
       SIDEBAR — Navy professional look
       ══════════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--navy-deep) 0%, var(--navy) 100%) !important;
        border-right: none !important;
        box-shadow: 2px 0 20px rgba(15, 26, 42, 0.15);
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 0.5rem !important;
    }

    /* Sidebar text overrides — everything white/light */
    [data-testid="stSidebar"] * {
        color: rgba(255, 255, 255, 0.85) !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: rgba(255, 255, 255, 0.65) !important;
    }
    [data-testid="stSidebar"] .stCaption p {
        color: rgba(255, 255, 255, 0.45) !important;
    }

    /* Sidebar navigation links */
    [data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a {
        color: rgba(255, 255, 255, 0.75) !important;
        border-radius: var(--radius-sm);
        transition: all 0.15s ease;
        padding: 0.35rem 0.75rem !important;
        margin: 1px 0;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a[aria-current="page"],
    [data-testid="stSidebar"] [data-testid="stSidebarNavItems"] li[data-active="true"] a {
        background: rgba(255, 95, 0, 0.15) !important;
        color: #FFFFFF !important;
        border-left: 3px solid var(--orange) !important;
        font-weight: 500;
    }

    /* Sidebar section headers */
    [data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] {
        color: rgba(255, 255, 255, 0.35) !important;
        font-size: 0.68rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
        padding: 0.8rem 0.75rem 0.2rem !important;
    }

    /* Sidebar button */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: rgba(255, 255, 255, 0.8) !important;
        border-radius: var(--radius-sm) !important;
        font-size: 0.82rem !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.12) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
        color: #FFFFFF !important;
    }

    .sidebar-brand {
        padding: 1.2rem 0.5rem 1rem 0.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 0.8rem;
        text-align: center;
    }
    .sidebar-brand h2 {
        font-family: var(--font-body) !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        margin: 0 !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .sidebar-brand .brand-accent {
        display: block;
        width: 32px;
        height: 3px;
        background: var(--orange);
        margin: 8px auto 6px auto;
        border-radius: 2px;
    }
    .sidebar-brand p {
        font-family: var(--font-body) !important;
        font-size: 0.68rem;
        color: rgba(255, 255, 255, 0.45) !important;
        margin: 0;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .sidebar-freshness {
        display: flex; align-items: center; gap: 6px;
        padding: 0.5rem 0.5rem;
        font-size: 0.72rem;
        color: rgba(255, 255, 255, 0.4) !important;
        font-family: var(--font-mono);
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        margin-top: 1rem;
    }
    .sidebar-freshness .dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        background: var(--success);
        animation: pulseGlow 2s ease-in-out infinite;
        flex-shrink: 0;
    }

    /* ══════════════════════════════════════════════
       METRIC CARDS — Clean with colored top bar
       ══════════════════════════════════════════════ */
    [data-testid="stMetric"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-top: 3px solid var(--teal) !important;
        border-radius: var(--radius-md) !important;
        padding: 1rem 1.2rem !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.25s ease;
    }
    [data-testid="stMetric"]:hover {
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-2px);
    }
    [data-testid="stMetricValue"] {
        font-family: var(--font-body) !important;
        font-size: 1.8rem !important;
        color: var(--navy) !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        font-family: var(--font-body) !important;
        font-size: 0.75rem !important;
        color: var(--text-tertiary) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        font-weight: 500 !important;
    }
    [data-testid="stMetricDelta"] {
        font-family: var(--font-mono) !important;
        font-size: 0.78rem !important;
    }

    /* Metric color variants */
    .metric-orange [data-testid="stMetric"] {
        border-top-color: var(--orange) !important;
    }
    .metric-orange [data-testid="stMetricValue"] {
        color: var(--orange) !important;
    }
    .metric-blue [data-testid="stMetric"] {
        border-top-color: var(--blue) !important;
    }
    .metric-blue [data-testid="stMetricValue"] {
        color: var(--blue) !important;
    }
    .metric-success [data-testid="stMetric"] {
        border-top-color: var(--success) !important;
    }
    .metric-success [data-testid="stMetricValue"] {
        color: var(--success) !important;
    }
    .metric-danger [data-testid="stMetric"] {
        border-top-color: var(--danger) !important;
    }
    .metric-danger [data-testid="stMetricValue"] {
        color: var(--danger) !important;
    }

    /* ══════════════════════════════════════════════
       SECTION HEADERS — Bold, clear hierarchy
       ══════════════════════════════════════════════ */
    .geo-section {
        font-family: var(--font-body);
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--text-tertiary);
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .geo-section::before {
        content: '';
        width: 3px; height: 14px;
        background: var(--orange);
        border-radius: 2px;
        flex-shrink: 0;
    }

    /* ══════════════════════════════════════════════
       INSIGHT CARDS — Crisp with status bars
       ══════════════════════════════════════════════ */
    .geo-insight {
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: 4px solid var(--teal);
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-xs);
    }
    .geo-insight:hover {
        box-shadow: var(--shadow-sm);
        transform: translateX(2px);
    }
    .geo-insight.positive { border-left-color: var(--success); }
    .geo-insight.negative { border-left-color: var(--danger); }
    .geo-insight.neutral  { border-left-color: var(--text-tertiary); }

    .geo-insight .insight-label {
        font-family: var(--font-body);
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-tertiary);
        font-weight: 500;
        margin: 0 0 4px 0;
    }
    .geo-insight .insight-value {
        font-family: var(--font-body);
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--navy);
        margin: 0;
        line-height: 1.2;
    }
    .geo-insight .insight-context {
        font-family: var(--font-body);
        font-size: 0.82rem;
        color: var(--text-secondary);
        margin: 4px 0 0 0;
    }

    /* ══════════════════════════════════════════════
       HERO SECTION — Professional masthead
       ══════════════════════════════════════════════ */
    .geo-hero {
        padding: 1.5rem 0 1.2rem 0;
        position: relative;
        margin-bottom: 0.5rem;
    }
    .geo-hero h1 {
        font-family: var(--font-display) !important;
        font-size: 2rem !important;
        color: var(--navy) !important;
        margin: 0 0 6px 0 !important;
        line-height: 1.15 !important;
    }
    .geo-hero .hero-sub {
        font-family: var(--font-body);
        font-size: 0.92rem;
        color: var(--text-secondary);
        margin: 0;
        letter-spacing: 0.01em;
        font-weight: 400;
    }
    .geo-hero .hero-rule {
        width: 48px; height: 3px;
        background: var(--orange);
        margin: 0.8rem 0 0 0;
        border-radius: 2px;
    }

    /* ══════════════════════════════════════════════
       CASE CARDS — List-style with status badge
       ══════════════════════════════════════════════ */
    .geo-case {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1rem 1.2rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        box-shadow: var(--shadow-xs);
    }
    .geo-case:hover {
        border-color: var(--border-focus);
        box-shadow: var(--shadow-sm);
        transform: translateY(-1px);
    }
    .geo-case .case-icon {
        font-size: 1.4rem;
        flex-shrink: 0;
        line-height: 1;
        margin-top: 2px;
    }
    .geo-case .case-body { flex: 1; min-width: 0; }
    .geo-case .case-title {
        font-family: var(--font-body);
        font-weight: 600;
        color: var(--navy);
        font-size: 0.9rem;
        margin: 0 0 4px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .geo-case .case-meta {
        font-family: var(--font-mono);
        font-size: 0.72rem;
        color: var(--text-tertiary);
        margin: 0;
    }
    .geo-case .case-badge {
        flex-shrink: 0;
        padding: 4px 12px;
        border-radius: var(--radius-xl);
        font-family: var(--font-body);
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        text-transform: capitalize;
    }
    .badge-deferido {
        background: var(--success-dim);
        color: var(--success);
    }
    .badge-indeferido {
        background: var(--danger-dim);
        color: var(--danger);
    }
    .badge-arquivamento {
        background: var(--surface-muted);
        color: var(--text-tertiary);
    }

    /* ══════════════════════════════════════════════
       DETAIL RECORD CARD
       ══════════════════════════════════════════════ */
    .geo-detail {
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: 4px solid var(--teal);
        border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
        padding: 1.3rem 1.5rem;
        margin: 0.5rem 0;
        animation: fadeSlideUp 0.3s ease-out;
        box-shadow: var(--shadow-sm);
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
        color: var(--navy);
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
        color: var(--text-tertiary);
        font-weight: 500;
        font-family: var(--font-body);
    }
    .geo-detail .detail-value {
        font-size: 0.88rem;
        color: var(--text-primary);
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
        border-top: 1px solid var(--border);
    }
    .geo-detail .detail-actions a {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 6px 14px;
        border-radius: var(--radius-sm);
        font-size: 0.78rem;
        font-family: var(--font-body);
        font-weight: 500;
        text-decoration: none;
        transition: all 0.15s ease;
        border: 1px solid var(--border);
        color: var(--text-secondary);
        background: transparent;
    }
    .geo-detail .detail-actions a:hover {
        border-color: var(--blue);
        color: var(--blue);
        background: var(--info-dim);
    }

    /* ══════════════════════════════════════════════
       COMPANY DOSSIER
       ══════════════════════════════════════════════ */
    .geo-dossier {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: var(--shadow-sm);
    }
    .geo-dossier .dossier-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid var(--border);
    }
    .geo-dossier .dossier-name {
        font-family: var(--font-display);
        font-size: 1.2rem;
        color: var(--navy);
        margin: 0;
    }
    .geo-dossier .dossier-cnae {
        font-family: var(--font-mono);
        font-size: 0.72rem;
        color: var(--text-secondary);
        background: var(--surface-muted);
        padding: 3px 10px;
        border-radius: var(--radius-sm);
    }

    .geo-kpi-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.8rem;
        margin: 0.8rem 0;
    }
    .geo-kpi {
        background: var(--surface-muted);
        border-radius: var(--radius-md);
        padding: 0.8rem 1rem;
        text-align: center;
        border: 1px solid var(--border-light);
    }
    .geo-kpi .kpi-value {
        font-family: var(--font-body);
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--navy);
        margin: 0;
    }
    .geo-kpi .kpi-label {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-tertiary);
        font-weight: 500;
        margin: 4px 0 0 0;
    }

    /* ══════════════════════════════════════════════
       NAVIGATION CARDS — Landing page
       ══════════════════════════════════════════════ */
    .geo-nav-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        transition: all 0.25s ease;
        cursor: pointer;
        text-decoration: none !important;
        display: block;
        box-shadow: var(--shadow-xs);
    }
    .geo-nav-card:hover {
        border-color: var(--blue);
        box-shadow: var(--shadow-lg), var(--shadow-blue);
        transform: translateY(-3px);
    }

    /* Page links styled as nav cards */
    [data-testid="stPageLink-nav"] a,
    [data-testid="stPageLink"] a,
    .stPageLink a {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.2rem 1.3rem !important;
        transition: all 0.25s ease !important;
        min-height: 160px;
        display: flex !important;
        flex-direction: column;
        justify-content: flex-start;
        text-decoration: none !important;
        white-space: normal !important;
        box-shadow: var(--shadow-xs) !important;
    }
    [data-testid="stPageLink-nav"] a:hover,
    [data-testid="stPageLink"] a:hover,
    .stPageLink a:hover {
        border-color: var(--teal) !important;
        box-shadow: var(--shadow-md), var(--shadow-blue) !important;
        transform: translateY(-3px);
    }
    [data-testid="stPageLink-nav"] a p,
    [data-testid="stPageLink"] a p,
    .stPageLink a p {
        font-family: var(--font-body);
        font-size: 0.85rem;
        color: var(--text-secondary) !important;
        line-height: 1.5;
        margin: 0;
        white-space: normal !important;
    }
    [data-testid="stPageLink-nav"] a p strong,
    [data-testid="stPageLink"] a p strong,
    .stPageLink a p strong {
        font-family: var(--font-body);
        font-weight: 700;
        font-size: 1rem;
        color: var(--navy) !important;
        display: block;
        margin-bottom: 0.4rem;
    }
    [data-testid="stPageLink-nav"] a p code,
    [data-testid="stPageLink"] a p code,
    .stPageLink a p code {
        font-family: var(--font-mono);
        font-size: 0.73rem;
        color: var(--teal) !important;
        padding: 3px 10px;
        background: var(--info-dim) !important;
        border: 1px solid rgba(41, 128, 185, 0.15);
        border-radius: var(--radius-xl);
        display: inline-block;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    .geo-nav-card .nav-icon {
        font-size: 1.8rem;
        margin-bottom: 0.6rem;
        display: block;
    }
    .geo-nav-card .nav-title {
        font-family: var(--font-body);
        font-weight: 700;
        font-size: 1rem;
        color: var(--navy);
        margin: 0 0 6px 0;
    }
    .geo-nav-card .nav-desc {
        font-size: 0.82rem;
        color: var(--text-secondary);
        margin: 0 0 0.8rem 0;
        line-height: 1.5;
    }
    .geo-nav-card .nav-stat {
        font-family: var(--font-mono);
        font-size: 0.73rem;
        font-weight: 500;
        color: var(--teal);
        padding: 3px 10px;
        background: var(--info-dim);
        border: 1px solid rgba(41, 128, 185, 0.15);
        border-radius: var(--radius-xl);
        display: inline-block;
    }

    /* ══════════════════════════════════════════════
       DONUT CHART (SVG)
       ══════════════════════════════════════════════ */
    .geo-donut {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        gap: 4px;
    }
    .geo-donut svg { filter: drop-shadow(0 2px 8px rgba(26, 44, 66, 0.12)); }
    .geo-donut .donut-label {
        font-family: var(--font-body);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-tertiary);
        font-weight: 500;
        margin-top: 4px;
    }

    /* ══════════════════════════════════════════════
       FILTER CHIPS
       ══════════════════════════════════════════════ */
    .geo-chip {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 12px;
        border-radius: var(--radius-xl);
        font-family: var(--font-mono);
        font-size: 0.72rem;
        font-weight: 500;
        background: var(--info-dim);
        color: var(--teal);
        border: 1px solid rgba(21, 96, 130, 0.15);
        margin: 0 4px 4px 0;
    }

    /* ══════════════════════════════════════════════
       COMPARISON BAR
       ══════════════════════════════════════════════ */
    .geo-compare-bar {
        background: var(--surface-muted);
        border: 1px solid var(--border-light);
        border-radius: 6px;
        height: 10px;
        overflow: hidden;
        position: relative;
    }
    .geo-compare-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.6s ease;
    }
    .geo-compare-marker {
        position: absolute;
        top: -3px;
        width: 2px;
        height: 16px;
        background: var(--navy);
        border-radius: 1px;
    }

    /* ══════════════════════════════════════════════
       EMPTY STATES
       ══════════════════════════════════════════════ */
    .geo-empty {
        text-align: center;
        padding: 3rem 1rem;
        color: var(--text-tertiary);
    }
    .geo-empty .empty-icon { font-size: 2.5rem; margin-bottom: 0.75rem; }
    .geo-empty .empty-text {
        font-size: 0.88rem;
        font-family: var(--font-body);
        color: var(--text-secondary);
    }

    /* ══════════════════════════════════════════════
       SOURCE ATTRIBUTION
       ══════════════════════════════════════════════ */
    .geo-source {
        font-family: var(--font-mono);
        font-size: 0.68rem;
        color: var(--text-muted);
        letter-spacing: 0.02em;
        margin-top: 4px;
    }

    .status-dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        flex-shrink: 0;
    }
    .status-fresh { background: var(--success); }
    .status-stale { background: var(--danger); }

    /* ══════════════════════════════════════════════
       STREAMLIT COMPONENT OVERRIDES
       ══════════════════════════════════════════════ */

    /* DataFrames */
    [data-testid="stDataFrame"] {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border) !important;
        box-shadow: var(--shadow-xs) !important;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        background: var(--surface) !important;
        box-shadow: var(--shadow-xs) !important;
    }
    [data-testid="stExpander"] summary {
        font-weight: 500 !important;
    }

    /* Buttons */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background: var(--orange) !important;
        color: #FFFFFF !important;
        font-family: var(--font-body) !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        letter-spacing: 0.02em;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {
        background: var(--orange-soft) !important;
        box-shadow: var(--shadow-orange) !important;
        transform: translateY(-1px);
    }

    .stButton > button[kind="secondary"],
    .stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]) {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        font-family: var(--font-body) !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        background: var(--surface) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="secondary"]:hover,
    .stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]):hover {
        border-color: var(--blue) !important;
        color: var(--blue) !important;
        background: var(--info-dim) !important;
    }

    .stDownloadButton > button {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        font-family: var(--font-body) !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton > button:hover {
        border-color: var(--teal) !important;
        color: var(--teal) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        border-bottom: 2px solid var(--border);
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: var(--font-body) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.01em;
        padding: 0.7rem 1.4rem !important;
        border-bottom: 2px solid transparent;
        color: var(--text-tertiary) !important;
        transition: all 0.15s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--navy) !important;
    }
    .stTabs [aria-selected="true"] {
        border-bottom-color: var(--orange) !important;
        color: var(--navy) !important;
        font-weight: 600 !important;
    }

    /* Warning/Info boxes */
    [data-testid="stAlert"] {
        border-radius: var(--radius-md) !important;
        font-family: var(--font-body) !important;
        border-left-width: 4px !important;
    }

    /* Text inputs & selects */
    .stTextInput > div > div > input {
        font-family: var(--font-body) !important;
        border-radius: var(--radius-sm) !important;
        border-color: var(--border) !important;
        transition: border-color 0.15s ease;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 1px var(--blue) !important;
    }
    .stSelectbox > div > div {
        border-radius: var(--radius-sm) !important;
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background-color: var(--teal) !important;
    }

    /* Divider */
    hr, [data-testid="stHorizontalBlock"] hr {
        border-color: var(--border) !important;
    }

    /* Toast */
    [data-testid="stToast"] {
        border-radius: var(--radius-md) !important;
        font-family: var(--font-body) !important;
    }

    /* ══════════════════════════════════════════════
       TRUST STRIP — Bottom of pages
       ══════════════════════════════════════════════ */
    .trust-strip {
        text-align: center;
        padding: 1.2rem 0;
        margin-top: 2rem;
        border-top: 2px solid var(--border);
    }
    .trust-strip span {
        font-family: var(--font-mono) !important;
        font-size: 0.72rem !important;
        color: var(--text-muted) !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    /* ══════════════════════════════════════════════
       STEP PROGRESS (Due Diligence)
       ══════════════════════════════════════════════ */
    .dd-stepper {
        display: flex;
        gap: 0;
        margin: 1rem 0 1.5rem 0;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }
    .dd-step {
        flex: 1;
        padding: 0.8rem 1rem;
        text-align: center;
        font-family: var(--font-body);
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--text-tertiary);
        background: var(--surface);
        position: relative;
        transition: all 0.2s ease;
    }
    .dd-step + .dd-step {
        border-left: 1px solid var(--border);
    }
    .dd-step.completed {
        background: var(--success-dim);
        color: var(--success);
    }
    .dd-step.active {
        background: var(--orange-dim);
        color: var(--orange);
        font-weight: 700;
    }
    .dd-step .step-number {
        display: inline-block;
        width: 22px; height: 22px;
        line-height: 22px;
        border-radius: 50%;
        background: var(--border);
        color: var(--text-tertiary);
        font-size: 0.72rem;
        font-weight: 700;
        margin-right: 6px;
        text-align: center;
    }
    .dd-step.completed .step-number {
        background: var(--success);
        color: #FFFFFF;
    }
    .dd-step.active .step-number {
        background: var(--orange);
        color: #FFFFFF;
    }

    /* ══════════════════════════════════════════════
       CONFORMITY SCORE GAUGE
       ══════════════════════════════════════════════ */
    .conformity-gauge {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-sm);
    }
    .conformity-gauge .gauge-score {
        font-family: var(--font-body);
        font-size: 3rem;
        font-weight: 800;
        line-height: 1;
        margin: 0.5rem 0;
    }
    .conformity-gauge .gauge-label {
        font-family: var(--font-body);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-tertiary);
        font-weight: 600;
    }
    .conformity-gauge .gauge-status {
        display: inline-block;
        padding: 4px 16px;
        border-radius: var(--radius-xl);
        font-size: 0.78rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }

    /* Source table */
    .source-table {
        width: 100%;
        border-collapse: collapse;
        font-family: var(--font-body);
        font-size: 0.84rem;
    }
    .source-table thead th {
        padding: 0.6rem 0.8rem;
        text-align: left;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-tertiary);
        font-weight: 600;
        border-bottom: 2px solid var(--border);
        background: var(--surface-muted);
    }
    .source-table thead th:nth-child(n+2) {
        text-align: right;
    }
    .source-table tbody tr {
        border-bottom: 1px solid var(--border-light);
        transition: background 0.15s ease;
    }
    .source-table tbody tr:hover {
        background: var(--surface-hover);
    }
    .source-table tbody td {
        padding: 0.6rem 0.8rem;
        color: var(--text-secondary);
    }
    .source-table tbody td:nth-child(n+2) {
        text-align: right;
    }
    .source-table .td-name {
        font-weight: 500;
        color: var(--text-primary);
    }
    .source-table .td-count {
        color: var(--teal);
        font-family: var(--font-mono);
        font-weight: 600;
        font-size: 0.82rem;
    }
    .source-table .td-date {
        font-family: var(--font-mono);
        font-size: 0.75rem;
        color: var(--text-tertiary);
    }
    .source-table .td-link a {
        color: var(--blue);
        text-decoration: none;
        font-size: 0.75rem;
        font-weight: 500;
        opacity: 0.7;
        transition: opacity 0.15s ease;
    }
    .source-table .td-link a:hover { opacity: 1; }
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
              color: str = "var(--teal)") -> str:
    """Retorna SVG de donut chart com percentual no centro."""
    radius = (size - stroke) / 2
    circumference = 2 * 3.14159 * radius
    filled = circumference * percentage / 100
    gap = circumference - filled

    return f"""
    <div class="geo-donut">
        <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
            <circle cx="{size/2}" cy="{size/2}" r="{radius}"
                fill="none" stroke="var(--border)" stroke-width="{stroke}"/>
            <circle cx="{size/2}" cy="{size/2}" r="{radius}"
                fill="none" stroke="{color}" stroke-width="{stroke}"
                stroke-dasharray="{filled} {gap}"
                stroke-linecap="round"
                transform="rotate(-90 {size/2} {size/2})"
                style="transition: stroke-dasharray 0.8s ease;"/>
            <text x="{size/2}" y="{size/2 + 1}"
                text-anchor="middle" dominant-baseline="middle"
                font-family="var(--font-body)" font-size="{size * 0.22}"
                font-weight="700"
                fill="var(--navy)">{percentage:.0f}%</text>
        </svg>
    </div>
    """


def stepper_html(steps: list[str], current: int) -> str:
    """Retorna HTML do stepper de etapas para Due Diligence."""
    html = '<div class="dd-stepper">'
    for i, label in enumerate(steps, 1):
        if i < current:
            cls = "completed"
            number = "&#10003;"
        elif i == current:
            cls = "active"
            number = str(i)
        else:
            cls = ""
            number = str(i)
        html += (
            f'<div class="dd-step {cls}">'
            f'<span class="step-number">{number}</span>'
            f'{label}</div>'
        )
    html += '</div>'
    return html


def conformity_gauge_html(score: float, label: str, color: str) -> str:
    """Retorna HTML do gauge de conformidade."""
    return f"""
    <div class="conformity-gauge">
        <p class="gauge-label">Conformidade Global</p>
        <p class="gauge-score" style="color: {color};">{score:.0%}</p>
        <span class="gauge-status" style="background: {color}15; color: {color};">
            {label}
        </span>
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


# ── Plotly theme helper ──

def get_plotly_layout(**overrides) -> dict:
    """Retorna layout base do Plotly alinhado ao tema.

    Dict-valued overrides (xaxis, yaxis, font, etc.) are deep-merged
    into the defaults so callers can add keys without losing the base
    grid/line colours.
    """
    layout = {
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "family": "Inter, -apple-system, sans-serif",
            "color": "#4A5568",
            "size": 12,
        },
        "title_font": {
            "family": "Inter, -apple-system, sans-serif",
            "color": "#1A2C42",
            "size": 14,
            "weight": 600,
        },
        "xaxis": {
            "gridcolor": "rgba(226, 230, 237, 0.6)",
            "linecolor": "#E2E6ED",
            "zerolinecolor": "#E2E6ED",
        },
        "yaxis": {
            "gridcolor": "rgba(226, 230, 237, 0.6)",
            "linecolor": "#E2E6ED",
            "zerolinecolor": "#E2E6ED",
        },
        "hoverlabel": {
            "bgcolor": "#FFFFFF",
            "bordercolor": "#E2E6ED",
            "font": {"family": "Inter", "size": 12, "color": "#1A2C42"},
        },
        "hovermode": "x unified",
        "margin": {"t": 30, "b": 35, "l": 50, "r": 20},
    }
    for key, val in overrides.items():
        if isinstance(val, dict) and isinstance(layout.get(key), dict):
            layout[key] = {**layout[key], **val}
        else:
            layout[key] = val
    return layout


# Plotly color sequences for charts
CHART_COLORS = {
    "primary": "#156082",
    "secondary": "#2980B9",
    "accent": "#FF5F00",
    "success": "#27AE60",
    "danger": "#E74C3C",
    "warning": "#F39C12",
    "neutral": "#8896A6",
    "sequence": ["#156082", "#2980B9", "#FF5F00", "#27AE60", "#F39C12", "#E74C3C",
                 "#1B7BA3", "#3498DB", "#FF7A2E", "#2ECC71"],
}
