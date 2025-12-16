// C:\wamp64\www\ImobCloud\frontend\src\utils\formatters.ts

import { format } from 'date-fns';

/**
 * Formata uma string de data para o formato brasileiro DD/MM/YYYY.
 * @param dateString - Data a ser formatada (string ou Date).
 * @returns String formatada ou 'N/A'
 */
export const formatDate = (dateString: string | Date | null | undefined): string => {
    if (!dateString) {
        return 'N/A';
    }
    try {
        // Tenta criar um objeto Date. Se for inválido, cai no catch.
        const dateObj = typeof dateString === 'string' ? new Date(dateString) : dateString;
        
        // Verifica se a data é válida
        if (isNaN(dateObj.getTime())) {
             return 'Data Inválida';
        }
        
        // Retorna a data formatada
        return format(dateObj, 'dd/MM/yyyy');
    } catch (e) {
        return 'Erro de Formatação';
    }
}

/**
 * Adicione aqui outras funções de formatação que você precise (ex: formatCurrency)
 */
export const formatCurrency = (value: number | string | null | undefined): string => {
    if (value === null || value === undefined) {
        return 'R$ 0,00';
    }
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 2,
    }).format(numValue);
}

// Se você estiver usando export default, o erro seria diferente.
// É altamente recomendável usar ES Modules (export const) para utilitários.
// Se você só tem a função formatDate, garanta que ela use "export".