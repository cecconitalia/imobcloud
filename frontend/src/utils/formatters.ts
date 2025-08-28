// Em frontend/src/utils/formatters.ts

/**
 * Formata um número ou string para uma moeda em BRL (Real Brasileiro).
 */
export function formatCurrency(value: number | string | null | undefined): string {
  if (value === null || value === undefined) {
    return 'N/A';
  }
  const numberValue = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(numberValue)) {
    return 'Valor inválido';
  }
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(numberValue);
}

/**
 * Converte o status do imóvel de uma chave para um texto legível.
 */
export function formatStatus(status: string | null | undefined): string {
  const statusMap: { [key: string]: string } = {
    A_VENDA: 'À Venda',
    PARA_ALUGAR: 'Para Alugar',
    VENDIDO: 'Vendido',
    ALUGADO: 'Alugado',
    EM_CONSTRUCAO: 'Em Construção',
    DESATIVADO: 'Desativado',
  };
  return status ? statusMap[status] || status : 'Não informado';
}