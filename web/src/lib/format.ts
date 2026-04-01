/**
 * Utilidades de formatacao brasileira (pt-BR).
 *
 * Backend retorna valores brutos — toda formatacao acontece no frontend.
 */

const ptBR = "pt-BR";

/** Numero com separador de milhares: 1.234.567 */
export function fmtBR(n: number, decimals = 0): string {
  return n.toLocaleString(ptBR, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/** Moeda brasileira: R$ 1.234,56 */
export function fmtReais(n: number): string {
  return n.toLocaleString(ptBR, { style: "currency", currency: "BRL" });
}

/** Porcentagem: 72,3% */
export function fmtPct(n: number): string {
  return `${n.toLocaleString(ptBR, {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  })}%`;
}

/** Data ISO -> DD/MM/YYYY */
export function fmtDate(d: string): string {
  const date = new Date(d);
  if (isNaN(date.getTime())) return d;
  return date.toLocaleDateString(ptBR);
}

/** Area em hectares: 1.234,5 ha */
export function fmtHa(n: number): string {
  return `${fmtBR(n, 1)} ha`;
}

/** Numero compacto: 1,2 mi / 45,3 mil */
export function fmtCompact(n: number): string {
  if (n >= 1_000_000) return `${fmtBR(n / 1_000_000, 1)} mi`;
  if (n >= 1_000) return `${fmtBR(n / 1_000, 1)} mil`;
  return fmtBR(n);
}

/** CNPJ formatado: 12.345.678/0001-90 */
export function fmtCNPJ(cnpj: string): string {
  const digits = cnpj.replace(/\D/g, "");
  if (digits.length !== 14) return cnpj;
  return `${digits.slice(0, 2)}.${digits.slice(2, 5)}.${digits.slice(5, 8)}/${digits.slice(8, 12)}-${digits.slice(12)}`;
}

/** Score badge color class based on value (0-100) */
export function scoreColor(score: number): string {
  if (score >= 70) return "text-green-700 bg-green-100";
  if (score >= 40) return "text-amber-700 bg-amber-100";
  return "text-red-700 bg-red-100";
}
