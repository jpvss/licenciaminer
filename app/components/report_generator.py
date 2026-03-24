"""Gerador de relatórios PDF — Inteligência Ambiental Minerária.

Produz relatórios profissionais de análise ambiental a partir de dados
consolidados por CNPJ, usando fpdf2 com formatação brasileira.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from io import BytesIO

from fpdf import FPDF

from app.components.report_data import ReportData

# ── Brand colors (print-friendly: white bg) ──
COLOR_BG = (255, 255, 255)
COLOR_TEXT = (28, 32, 42)
COLOR_TEXT_DIM = (108, 117, 125)
COLOR_AMBER = (180, 142, 50)       # Gold accent (print-safe)
COLOR_MALACHITE = (72, 140, 100)   # Green — deferido
COLOR_OXIDE = (175, 70, 62)        # Red — indeferido
COLOR_RISK_LOW = (72, 140, 100)
COLOR_RISK_MED = (180, 142, 50)
COLOR_RISK_HIGH = (175, 70, 62)
COLOR_TABLE_HEADER = (40, 46, 58)
COLOR_TABLE_ALT = (245, 243, 238)
COLOR_BORDER = (200, 196, 186)

RISK_COLORS = {
    "BAIXO": COLOR_RISK_LOW,
    "MODERADO": COLOR_RISK_MED,
    "ALTO": COLOR_RISK_HIGH,
}
DECISION_COLORS = {
    "deferido": COLOR_MALACHITE,
    "indeferido": COLOR_OXIDE,
    "arquivamento": COLOR_TEXT_DIM,
}


def format_brl(value: float | None) -> str:
    """Formata valor em reais brasileiro."""
    if value is None or value != value:  # NaN check
        return "—"
    formatted = f"{value:,.2f}"
    return "R$ " + formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def format_cnpj(cnpj: str) -> str:
    """Formata CNPJ: XX.XXX.XXX/XXXX-XX."""
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj


def _sanitize_text(text: str) -> str:
    """Sanitiza texto para compatibilidade com fontes Latin-1.

    Substitui caracteres Unicode problemáticos por equivalentes ASCII.
    Usado como fallback quando fontes Unicode TTF não estão disponíveis.
    """
    replacements = {
        "\u2014": "-",   # em-dash
        "\u2013": "-",   # en-dash
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2026": "...", # ellipsis
        "\u2022": "*",   # bullet
        "\u00b7": ".",   # middle dot
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


class LicenciaMinerReport(FPDF):
    """Relatório profissional de inteligência ambiental."""

    def __init__(self) -> None:
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)
        self.report_id = str(uuid.uuid4())[:8].upper()
        self.generated_at = datetime.now()
        self._use_unicode = False
        self._font_family = "Helvetica"

        # Try to load a Unicode TTF font for proper Portuguese support
        import platform
        font_candidates = []
        if platform.system() == "Darwin":
            font_candidates = [
                ("/System/Library/Fonts/Supplemental/Arial.ttf",
                 "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                 "/System/Library/Fonts/Supplemental/Arial Italic.ttf"),
            ]
        elif platform.system() == "Linux":
            font_candidates = [
                ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
                ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"),
            ]

        for regular, bold, italic in font_candidates:
            from pathlib import Path
            if Path(regular).exists():
                try:
                    self.add_font("UniFont", "", regular, uni=True)
                    self.add_font("UniFont", "B", bold, uni=True)
                    self.add_font("UniFont", "I", italic, uni=True)
                    self._use_unicode = True
                    self._font_family = "UniFont"
                    break
                except Exception:
                    pass

    def _t(self, text: str) -> str:
        """Processa texto: mantém Unicode se fonte suporta, senão sanitiza."""
        if self._use_unicode:
            return text
        return _sanitize_text(text)

    def header(self) -> None:
        """Cabeçalho padrão de todas as páginas (exceto capa)."""
        if self.page_no() <= 1:
            return
        self.set_font(self._font_family, "I", 7)
        self.set_text_color(*COLOR_TEXT_DIM)
        self.cell(
            0, 6,
            self._t("CONFIDENCIAL - LicenciaMiner - Relatorio de Inteligencia Ambiental"),
            align="L",
        )
        self.cell(
            0, 6, self._t(f"Pag. {self.page_no()}"),
            align="R", new_x="LMARGIN", new_y="NEXT",
        )
        self.set_draw_color(*COLOR_BORDER)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self) -> None:
        """Rodapé com ID do relatório e data."""
        self.set_y(-15)
        self.set_font(self._font_family, "I", 7)
        self.set_text_color(*COLOR_TEXT_DIM)
        date_str = self.generated_at.strftime("%d/%m/%Y %H:%M")
        self.cell(
            0, 8,
            f"ID: {self.report_id}  |  Gerado em: {date_str}  |  "
            f"LicenciaMiner v0.2.0  |  Pág. {self.page_no()}/{{nb}}",
            align="C",
        )

    # ── Section helpers ──

    def section_title(self, number: int, title: str) -> None:
        """Renderiza título de seção numerada."""
        self.set_font(self._font_family, "B", 13)
        self.set_text_color(*COLOR_AMBER)
        self.cell(0, 10, self._t(f"{number}. {title}"), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*COLOR_AMBER)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(4)
        self.set_text_color(*COLOR_TEXT)

    def subsection_title(self, title: str) -> None:
        """Subtítulo dentro de uma seção."""
        self.set_font(self._font_family, "B", 10)
        self.set_text_color(*COLOR_TEXT)
        self.cell(0, 8, self._t(title), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text: str) -> None:
        """Parágrafo de corpo."""
        self.set_font(self._font_family, "", 9)
        self.set_text_color(*COLOR_TEXT)
        self.multi_cell(0, 5, self._t(text))
        self.ln(2)

    def dim_text(self, text: str) -> None:
        """Texto de metadados/fonte."""
        self.set_font(self._font_family, "I", 7.5)
        self.set_text_color(*COLOR_TEXT_DIM)
        self.multi_cell(0, 4, self._t(text))
        self.ln(2)

    def source_badge(self, source: str, url: str = "") -> None:
        """Badge de fonte de dados."""
        date_str = self.generated_at.strftime("%d/%m/%Y")
        text = f"Fonte: {source} | Consulta: {date_str}"
        if url:
            text += f" | {url}"
        self.dim_text(text)

    def risk_badge(self, level: str) -> None:
        """Badge colorida de nível de risco."""
        color = RISK_COLORS.get(level, COLOR_TEXT_DIM)
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font(self._font_family, "B", 10)
        w = self.get_string_width(f"  {level}  ") + 4
        self.cell(w, 8, f"  {level}  ", fill=True, align="C")
        self.set_text_color(*COLOR_TEXT)
        self.ln(6)

    def kpi_row(self, kpis: list[tuple[str, str, str]]) -> None:
        """Linha de KPI cards. Cada tupla: (label, value, sublabel)."""
        col_w = (self.w - 20) / len(kpis)
        y_start = self.get_y()

        for label, value, sublabel in kpis:
            x = self.get_x()

            # Card background
            self.set_fill_color(*COLOR_TABLE_ALT)
            self.set_draw_color(*COLOR_BORDER)
            self.rect(x, y_start, col_w - 2, 22, style="DF")

            # Value
            self.set_xy(x + 2, y_start + 2)
            self.set_font(self._font_family, "B", 14)
            self.set_text_color(*COLOR_TEXT)
            self.cell(col_w - 6, 8, self._t(value), align="C")

            # Label
            self.set_xy(x + 2, y_start + 10)
            self.set_font(self._font_family, "", 7.5)
            self.set_text_color(*COLOR_TEXT_DIM)
            self.cell(col_w - 6, 5, self._t(label), align="C")

            # Sublabel
            self.set_xy(x + 2, y_start + 15)
            self.set_font(self._font_family, "I", 6.5)
            self.cell(col_w - 6, 4, self._t(sublabel), align="C")

            self.set_xy(x + col_w, y_start)

        self.set_xy(10, y_start + 26)

    def decision_badge_text(self, decisao: str) -> str:
        """Texto formatado para decisão."""
        labels = {
            "deferido": "DEFERIDO",
            "indeferido": "INDEFERIDO",
            "arquivamento": "ARQUIVADO",
        }
        return labels.get(decisao, decisao.upper() if decisao else "-")

    def simple_table(
        self,
        headers: list[str],
        rows: list[list[str]],
        col_widths: list[float] | None = None,
    ) -> None:
        """Tabela simples com cabeçalho colorido e linhas alternadas."""
        if not col_widths:
            col_widths = [(self.w - 20) / len(headers)] * len(headers)

        # Header
        self.set_font(self._font_family, "B", 8)
        self.set_fill_color(*COLOR_TABLE_HEADER)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, self._t(h), border=0, fill=True, align="C")
        self.ln()

        # Rows
        self.set_font(self._font_family, "", 8)
        self.set_text_color(*COLOR_TEXT)
        for row_idx, row in enumerate(rows):
            if row_idx % 2 == 0:
                self.set_fill_color(*COLOR_TABLE_ALT)
            else:
                self.set_fill_color(*COLOR_BG)

            for i, cell_text in enumerate(row):
                self.cell(col_widths[i], 6, self._t(cell_text), border=0, fill=True, align="C")
            self.ln()

        self.ln(3)


def generate_report(data: ReportData) -> bytes:
    """Gera relatório PDF completo a partir de ReportData.

    Retorna bytes do PDF pronto para download.
    """
    pdf = LicenciaMinerReport()
    pdf.alias_nb_pages()

    # ── CAPA ──
    pdf.add_page()
    pdf.ln(30)

    # Título
    pdf.set_font(pdf._font_family, "B", 24)
    pdf.set_text_color(*COLOR_AMBER)
    pdf.cell(0, 12, "LICENCIAMINER", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font(pdf._font_family, "", 11)
    pdf.set_text_color(*COLOR_TEXT_DIM)
    pdf.cell(
        0, 7, pdf._t("Relatorio de Inteligencia Ambiental"),
        align="C", new_x="LMARGIN", new_y="NEXT",
    )
    pdf.ln(8)

    # Linha decorativa
    pdf.set_draw_color(*COLOR_AMBER)
    pdf.set_line_width(0.5)
    pdf.line(70, pdf.get_y(), 140, pdf.get_y())
    pdf.ln(12)

    # Empresa
    pdf.set_font(pdf._font_family, "B", 16)
    pdf.set_text_color(*COLOR_TEXT)
    empresa_name = data.razao_social or data.cnpj
    pdf.multi_cell(0, 9, pdf._t(empresa_name), align="C")
    pdf.ln(3)

    pdf.set_font(pdf._font_family, "", 10)
    pdf.set_text_color(*COLOR_TEXT_DIM)
    pdf.cell(0, 7, f"CNPJ: {format_cnpj(data.cnpj)}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # Risk badge
    pdf.set_font(pdf._font_family, "B", 9)
    pdf.set_text_color(*COLOR_TEXT_DIM)
    pdf.cell(0, 6, pdf._t("NIVEL DE RISCO"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    risk_color = RISK_COLORS.get(data.risk_level, COLOR_TEXT_DIM)
    badge_w = 50
    badge_x = (pdf.w - badge_w) / 2
    pdf.set_fill_color(*risk_color)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(pdf._font_family, "B", 14)
    pdf.set_x(badge_x)
    pdf.cell(badge_w, 12, data.risk_level, fill=True, align="C")
    pdf.ln(20)

    # Metadados da capa
    pdf.set_text_color(*COLOR_TEXT_DIM)
    pdf.set_font(pdf._font_family, "", 8)
    date_str = data.generated_at.strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 5, f"Gerado em: {date_str}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(
        0, 5, pdf._t(f"ID do Relatorio: {pdf.report_id}"),
        align="C", new_x="LMARGIN", new_y="NEXT",
    )
    pdf.cell(0, 5, "CONFIDENCIAL", align="C", new_x="LMARGIN", new_y="NEXT")

    # ── 1. SUMÁRIO EXECUTIVO ──
    pdf.add_page()
    pdf.section_title(1, "Sumário Executivo")

    # KPI row
    risk_label = data.risk_level
    inf_label = str(data.total_infracoes) if data.total_infracoes else "0"
    cfem_label = format_brl(data.cfem_total_pago) if data.cfem_total_pago else "—"

    pdf.kpi_row([
        ("Risco Geral", risk_label, "calculado"),
        ("Taxa Aprovação", f"{data.taxa_aprovacao:.0f}%", f"N={data.total_decisoes}"),
        ("Infrações IBAMA", inf_label, f"{data.anos_com_infracao} anos"),
        ("CFEM Total", cfem_label, f"{data.cfem_meses_pagamento} meses"),
    ])

    # Achados principais
    pdf.subsection_title("Principais Achados")
    if data.findings:
        for i, finding in enumerate(data.findings, 1):
            pdf.set_font(pdf._font_family, "", 9)
            pdf.set_text_color(*COLOR_TEXT)
            pdf.cell(6, 5, f"{i}.")
            pdf.multi_cell(0, 5, pdf._t(finding))
            pdf.ln(1)
    else:
        pdf.body_text("Dados insuficientes para gerar achados automatizados.")

    pdf.ln(2)
    pdf.source_badge(
        "SEMAD MG, IBAMA, ANM, Receita Federal",
        "dadosabertos.ibama.gov.br | geo.anm.gov.br",
    )

    # ── 2. PERFIL DA EMPRESA ──
    pdf.add_page()
    pdf.section_title(2, "Perfil da Empresa")

    fields = [
        ("Razão Social", data.razao_social or "—"),
        ("CNPJ", format_cnpj(data.cnpj)),
        ("CNAE", f"{data.cnae_fiscal} — {data.cnae_descricao}" if data.cnae_fiscal else "—"),
        ("Porte", data.porte or "—"),
        ("Data de Abertura", data.data_abertura or "—"),
        ("Situação Cadastral", data.situacao or "—"),
    ]

    for label, value in fields:
        pdf.set_font(pdf._font_family, "B", 9)
        pdf.set_text_color(*COLOR_TEXT_DIM)
        pdf.cell(45, 6, pdf._t(label))
        pdf.set_font(pdf._font_family, "", 9)
        pdf.set_text_color(*COLOR_TEXT)
        pdf.cell(0, 6, pdf._t(str(value)), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)
    pdf.source_badge("Receita Federal via BrasilAPI", "brasilapi.com.br")

    # ── 3. HISTÓRICO DE LICENCIAMENTO ──
    pdf.section_title(3, "Histórico de Licenciamento")

    if data.decisoes:
        # Summary
        n_def = sum(1 for d in data.decisoes if d.get("decisao") == "deferido")
        n_ind = sum(1 for d in data.decisoes if d.get("decisao") == "indeferido")
        n_arq = sum(1 for d in data.decisoes if d.get("decisao") == "arquivamento")
        pdf.body_text(
            f"Total de {len(data.decisoes)} decisões registradas: "
            f"{n_def} deferimento(s), {n_ind} indeferimento(s), {n_arq} arquivamento(s)."
        )

        # Table
        headers = ["Ano", "Atividade", "Classe", "Modalidade", "Decisão"]
        col_widths = [18, 55, 18, 45, 30]
        rows = []
        for d in data.decisoes[:30]:  # Limit to 30 for readability
            rows.append([
                str(d.get("ano", "—")),
                str(d.get("atividade", "—"))[:30],
                str(d.get("classe", "—")),
                str(d.get("modalidade", "—"))[:25],
                pdf.decision_badge_text(d.get("decisao", "")),
            ])

        pdf.simple_table(headers, rows, col_widths)

        if len(data.decisoes) > 30:
            pdf.dim_text(f"Mostrando 30 de {len(data.decisoes)} decisões.")
    else:
        pdf.body_text("Nenhuma decisão de licenciamento encontrada para este CNPJ.")

    pdf.source_badge(
        "SEMAD MG",
        "sistemas.meioambiente.mg.gov.br/licenciamento",
    )

    # ── 4. ANÁLISE COMPARATIVA ──
    pdf.add_page()
    pdf.section_title(4, "Análise Comparativa")

    # Comparison text
    if data.taxa_aprovacao > 0 and data.taxa_aprovacao_geral > 0:
        diff = data.taxa_aprovacao - data.taxa_aprovacao_geral
        direction = "acima" if diff > 0 else "abaixo"

        pdf.body_text(
            f"A taxa de aprovação desta empresa ({data.taxa_aprovacao:.1f}%) está "
            f"{abs(diff):.1f} pontos percentuais {direction} da média estadual "
            f"para mineração ({data.taxa_aprovacao_geral:.1f}%)."
        )

        if data.taxa_aprovacao_filtrada > 0:
            diff2 = data.taxa_aprovacao - data.taxa_aprovacao_filtrada
            dir2 = "acima" if diff2 > 0 else "abaixo"
            pdf.body_text(
                f"Para a atividade {data.atividade_principal}, a taxa média é "
                f"{data.taxa_aprovacao_filtrada:.1f}% (N={data.total_filtrado}). "
                f"Esta empresa está {abs(diff2):.1f}pp {dir2} deste benchmark."
            )

        # Visual comparison bar (text-based)
        pdf.subsection_title("Comparação Visual")
        bars = [
            ("Esta empresa", data.taxa_aprovacao),
            ("Média estadual", data.taxa_aprovacao_geral),
        ]
        if data.taxa_aprovacao_filtrada > 0:
            bars.append((f"Média {data.atividade_principal[:7]}", data.taxa_aprovacao_filtrada))

        for label, rate in bars:
            pdf.set_font(pdf._font_family, "", 8)
            pdf.set_text_color(*COLOR_TEXT_DIM)
            pdf.cell(40, 5, pdf._t(label))

            # Bar
            bar_w = 100 * (rate / 100)
            bar_color = (
                COLOR_MALACHITE if rate >= 70
                else COLOR_AMBER if rate >= 50
                else COLOR_OXIDE
            )
            pdf.set_fill_color(*bar_color)
            pdf.cell(bar_w, 5, "", fill=True)

            pdf.set_font(pdf._font_family, "B", 8)
            pdf.set_text_color(*COLOR_TEXT)
            pdf.cell(20, 5, f" {rate:.0f}%", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(3)
    else:
        pdf.body_text("Dados insuficientes para análise comparativa.")

    # Similar cases
    if data.casos_similares:
        pdf.subsection_title("Casos Similares Recentes")
        headers = ["Ano", "Empreendimento", "Decisão"]
        col_widths = [18, 110, 35]
        rows = []
        for c in data.casos_similares[:5]:
            rows.append([
                str(c.get("ano", "—")),
                str(c.get("empreendimento", "—"))[:55],
                pdf.decision_badge_text(c.get("decisao", "")),
            ])
        pdf.simple_table(headers, rows, col_widths)

    pdf.source_badge("SEMAD MG", "sistemas.meioambiente.mg.gov.br/licenciamento")

    # ── 5. CONFORMIDADE — INFRAÇÕES IBAMA ──
    pdf.section_title(5, "Conformidade — Infrações IBAMA")

    if data.total_infracoes > 0:
        pdf.body_text(
            f"Registradas {data.total_infracoes} infração(ões) ambiental(is) "
            f"distribuídas em {data.anos_com_infracao} ano(s)."
        )

        # Context: how does this compare?
        if data.faixas_infracoes:
            pdf.subsection_title("Contexto Estatístico — Infrações vs. Aprovação")
            headers = ["Faixa de Infrações", "Decisões", "Taxa Aprovação"]
            col_widths = [60, 40, 50]
            rows = []
            for f in data.faixas_infracoes:
                rows.append([
                    str(f.get("faixa_infracoes", "—")),
                    str(f.get("total", 0)),
                    f"{f.get('taxa_aprovacao', 0):.1f}%",
                ])
            pdf.simple_table(headers, rows, col_widths)

            pdf.body_text(
                "Nota: A tabela acima mostra a correlação entre número de infrações "
                "IBAMA e taxa de aprovação de licenciamento em MG para empresas de mineração."
            )
    else:
        pdf.body_text(
            "Nenhuma infração ambiental IBAMA registrada para este CNPJ. "
            "Histórico limpo."
        )

    pdf.source_badge(
        "IBAMA Dados Abertos",
        "dadosabertos.ibama.gov.br/dataset/fiscalizacao-auto-de-infracao",
    )

    # ── 6. TÍTULOS MINERÁRIOS E CFEM ──
    pdf.add_page()
    pdf.section_title(6, "Títulos Minerários e CFEM")

    # ANM Titles
    pdf.subsection_title("Processos ANM")
    if data.titulos_anm:
        headers = ["Processo", "Fase", "Substância", "Área (ha)", "Ano"]
        col_widths = [35, 45, 40, 25, 20]
        rows = []
        for t in data.titulos_anm[:15]:
            area = t.get("AREA_HA")
            area_str = f"{area:,.1f}" if isinstance(area, (int, float)) and area == area else "—"
            rows.append([
                str(t.get("PROCESSO", "—")),
                str(t.get("FASE", "—"))[:25],
                str(t.get("SUBS", "—"))[:20],
                area_str,
                str(t.get("ANO", "—")),
            ])
        pdf.simple_table(headers, rows, col_widths)
    else:
        pdf.body_text("Nenhum título minerário ANM encontrado vinculado a esta empresa.")

    pdf.source_badge("ANM SIGMINE", "geo.anm.gov.br")

    # CFEM
    pdf.subsection_title("Pagamentos CFEM (Royalties)")
    if data.cfem_meses_pagamento > 0:
        pdf.body_text(
            f"Total pago: {format_brl(data.cfem_total_pago)} em "
            f"{data.cfem_meses_pagamento} meses de recolhimento (período 2022-2026)."
        )
    else:
        pdf.body_text("Sem pagamentos CFEM registrados no período analisado (2022-2026).")

    pdf.source_badge("ANM Arrecadação", "app.anm.gov.br/dadosabertos/ARRECADACAO")

    # ── 7. RESTRIÇÕES ESPACIAIS ──
    pdf.section_title(7, "Restrições Espaciais")

    if data.analise_espacial:
        pdf.body_text(
            "Análise de correlação entre sobreposições espaciais (Unidades de Conservação, "
            "Terras Indígenas, biomas) e taxa de aprovação de licenciamento em MG."
        )

        headers = ["Análise", "Categoria", "Decisões", "Taxa Aprovação"]
        col_widths = [45, 35, 30, 35]
        rows = []
        for a in data.analise_espacial:
            if a.get("total_decisoes"):
                rows.append([
                    str(a.get("analise", "—")),
                    str(a.get("categoria", "—")),
                    str(a.get("total_decisoes", 0)),
                    f"{a.get('taxa_aprovacao', 0):.1f}%",
                ])

        if rows:
            pdf.simple_table(headers, rows, col_widths)
        else:
            pdf.body_text("Dados espaciais insuficientes para análise.")
    else:
        pdf.body_text(
            "Análise espacial não disponível. Execute `licenciaminer collect spatial` "
            "para gerar dados de sobreposição."
        )

    pdf.source_badge("ICMBio, FUNAI, IBGE, ANM", "geo.anm.gov.br | icmbio.gov.br")

    # ── 8. AVISO LEGAL ──
    pdf.add_page()
    pdf.section_title(8, "Aviso Legal e Limitações")

    disclaimer_sections = [
        (
            "Natureza do Relatório",
            "Este relatório foi gerado automaticamente pela plataforma LicenciaMiner "
            "com base em dados públicos oficiais disponibilizados por órgãos "
            "governamentais brasileiros. Não constitui parecer jurídico, parecer "
            "técnico ambiental, nem substitui a análise de profissional habilitado."
        ),
        (
            "Fontes de Dados",
            "As informações foram obtidas exclusivamente de bases de dados públicas: "
            "SEMAD/MG, IBAMA, ANM, Receita Federal, ICMBio, FUNAI e IBGE. A precisão "
            "dos dados depende da atualização e correção das fontes originais."
        ),
        (
            "Limitações Conhecidas",
            "Dados do IBAMA SISLIC incluem apenas licenças emitidas, não incluindo "
            "indeferimentos federais. Decisões SEMAD/MG cobrem o período disponível "
            "no portal. Análises estatísticas baseadas em amostras pequenas (N < 10) "
            "devem ser interpretadas com cautela. Sobreposições espaciais são calculadas "
            "com base em geometrias oficiais e podem conter imprecisões."
        ),
        (
            "Proteção de Dados (LGPD)",
            "Este relatório processa dados pessoais de acesso público "
            "(Art. 7, §3º e §4º da Lei 13.709/2018). Os dados foram tratados para "
            "finalidade legítima de análise de conformidade ambiental."
        ),
        (
            "Isenção de Responsabilidade",
            "A LicenciaMiner não se responsabiliza por decisões de investimento, "
            "aquisição ou desinvestimento tomadas com base exclusivamente nas "
            "informações deste relatório. Recomenda-se a verificação nas fontes "
            "originais e a consulta a profissionais habilitados."
        ),
    ]

    for title, text in disclaimer_sections:
        pdf.set_font(pdf._font_family, "B", 9)
        pdf.set_text_color(*COLOR_TEXT)
        pdf.cell(0, 6, pdf._t(title), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(pdf._font_family, "", 8)
        pdf.set_text_color(*COLOR_TEXT_DIM)
        pdf.multi_cell(0, 4.5, pdf._t(text))
        pdf.ln(3)

    # Report metadata
    pdf.ln(5)
    pdf.set_draw_color(*COLOR_BORDER)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    pdf.set_font(pdf._font_family, "", 7.5)
    pdf.set_text_color(*COLOR_TEXT_DIM)
    date_full = data.generated_at.strftime("%d/%m/%Y às %H:%M")
    pdf.cell(0, 4, pdf._t(f"Gerado em: {date_full}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 4, pdf._t("Versao do sistema: 0.2.0"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 4, pdf._t(f"ID do relatorio: {pdf.report_id}"), new_x="LMARGIN", new_y="NEXT")

    # ── Output ──
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
