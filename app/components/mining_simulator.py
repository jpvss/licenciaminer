"""Simulador de KPIs operacionais de mineradora modelo (5.0 MTPA).

Gera 24 meses de dados simulados para 7 setores organizacionais
usando seed fixa para reproducibilidade. Todos os benchmarks são
baseados em referências da indústria de mineração de ferro.

IMPORTANTE: 100% dados fictícios — ferramenta de demonstração comercial.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

SEED = 42
MONTHS = 24


@dataclass
class KPI:
    """Definição de um KPI operacional."""

    nome: str
    unidade: str
    target: float
    min_val: float
    max_val: float
    trend: float = 0.0  # tendência mensal (+/-)
    seasonality: float = 0.0  # amplitude sazonal
    noise: float = 0.05  # ruído relativo


# ── Definições por setor ──

SETORES: dict[str, list[KPI]] = {
    "Planejamento de Mina": [
        KPI("Aderência ao Plano", "%", 95.0, 85.0, 99.0, 0.1, 2.0, 0.03),
        KPI("REM (Relação Estéril/Minério)", ":1", 2.5, 1.5, 3.5, 0.0, 0.3, 0.05),
        KPI("Conformidade de Cava", "%", 96.0, 90.0, 99.0, 0.05, 1.5, 0.02),
    ],
    "Operação de Mina": [
        KPI("Produtividade da Frota", "t/h", 320.0, 250.0, 400.0, 0.5, 15.0, 0.04),
        KPI("Ciclo de Transporte", "min", 25.0, 15.0, 35.0, -0.1, 2.0, 0.06),
        KPI("Consumo de Diesel", "L/t", 1.1, 0.8, 1.5, -0.005, 0.05, 0.04),
        KPI("Disponibilidade Física", "%", 88.0, 82.0, 95.0, 0.1, 1.5, 0.03),
        KPI("Utilização Física", "%", 75.0, 65.0, 85.0, 0.15, 3.0, 0.04),
    ],
    "Processamento Mineral": [
        KPI("Recuperação Metalúrgica", "%", 85.0, 75.0, 92.0, 0.1, 1.0, 0.02),
        KPI("Utilização de Planta", "%", 92.0, 85.0, 98.0, 0.05, 2.0, 0.03),
        KPI("Teor do Concentrado", "% Fe", 65.0, 63.0, 67.0, 0.0, 0.3, 0.01),
        KPI("Throughput", "t/h", 580.0, 500.0, 650.0, 0.5, 20.0, 0.03),
    ],
    "Rejeitos e Meio Ambiente": [
        KPI("Volume Disposto", "mil m³", 120.0, 50.0, 200.0, 1.0, 15.0, 0.06),
        KPI("Recirculação de Água", "%", 85.0, 70.0, 95.0, 0.2, 3.0, 0.04),
        KPI("Fator de Segurança", "", 1.40, 1.30, 1.50, 0.0, 0.02, 0.01),
    ],
    "Manutenção": [
        KPI("MTBF", "h", 350.0, 150.0, 500.0, 1.0, 20.0, 0.05),
        KPI("MTTR", "h", 4.5, 2.0, 8.0, -0.05, 0.5, 0.06),
        KPI("Disponibilidade Física", "%", 90.0, 82.0, 95.0, 0.1, 1.5, 0.03),
        KPI("Custo por Tonelada", "R$/t", 4.50, 2.0, 8.0, -0.02, 0.3, 0.05),
    ],
    "Logística e Supply Chain": [
        KPI("Giro de Estoque", "x/ano", 8.0, 4.0, 12.0, 0.05, 1.0, 0.06),
        KPI("Lead Time Médio", "dias", 35.0, 15.0, 60.0, -0.3, 3.0, 0.05),
        KPI("Demurrage", "R$ mil", 150.0, 0.0, 500.0, -2.0, 30.0, 0.10),
    ],
    "SSMA / ESG": [
        KPI("TRIFR", "por mi h", 1.5, 0.5, 3.0, -0.02, 0.2, 0.08),
        KPI("Investimento Social", "R$ mil", 800.0, 100.0, 2000.0, 5.0, 100.0, 0.06),
    ],
}


def gerar_serie_kpi(kpi: KPI, rng: np.random.Generator) -> pd.DataFrame:
    """Gera série temporal de 24 meses para um KPI."""
    t = np.arange(MONTHS)

    # Base + tendência + sazonalidade + ruído
    base = kpi.target + kpi.trend * t
    seasonal = kpi.seasonality * np.sin(2 * np.pi * t / 12)
    noise = rng.normal(0, kpi.noise * kpi.target, MONTHS)

    values = base + seasonal + noise
    values = np.clip(values, kpi.min_val, kpi.max_val)

    # Datas mensais
    dates = pd.date_range(
        end=pd.Timestamp.now().normalize(),
        periods=MONTHS,
        freq="MS",
    )

    return pd.DataFrame({
        "data": dates,
        "valor": values,
        "target": kpi.target,
        "min": kpi.min_val,
        "max": kpi.max_val,
    })


def gerar_dados_setor(setor: str) -> dict[str, pd.DataFrame]:
    """Gera dados simulados para todos os KPIs de um setor.

    Returns:
        Dict {nome_kpi: DataFrame com colunas [data, valor, target, min, max]}.
    """
    rng = np.random.default_rng(SEED)
    kpis = SETORES.get(setor, [])
    return {kpi.nome: gerar_serie_kpi(kpi, rng) for kpi in kpis}


def gerar_todos_os_dados() -> dict[str, dict[str, pd.DataFrame]]:
    """Gera dados simulados para todos os setores.

    Returns:
        Dict {setor: {nome_kpi: DataFrame}}.
    """
    rng = np.random.default_rng(SEED)
    result = {}
    for setor, kpis in SETORES.items():
        result[setor] = {kpi.nome: gerar_serie_kpi(kpi, rng) for kpi in kpis}
    return result


def get_kpi_info(setor: str) -> list[KPI]:
    """Retorna definições de KPIs para um setor."""
    return SETORES.get(setor, [])
