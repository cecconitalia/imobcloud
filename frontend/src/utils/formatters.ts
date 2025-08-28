/**
 * Formata um valor numérico para a moeda brasileira (BRL).
 * @param value O valor a ser formatado.
 * @returns O valor formatado como string.
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
  }).format(value);
}

/**
 * Formata uma string de status (ex: 'A_VENDA') para um formato legível (ex: 'À Venda').
 * @param status A string de status a ser formatada.
 * @returns O status formatado.
 */
export function formatStatus(status: string): string {
  return status.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}