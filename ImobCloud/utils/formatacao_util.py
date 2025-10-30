import locale

def formatar_valor_para_pt_br(valor_numerico: float) -> str:
    """
    Formata um valor float para uma string com padrão brasileiro (vírgula decimal, ponto milhar).
    Tenta definir o locale 'pt_BR' para garantir a formatação correta.

    Args:
        valor_numerico: O número float (ex: 75000.00) a ser formatado.

    Returns:
        O valor formatado como string (ex: "75.000,00").
    """
    
    # Lista de possíveis configurações de locale para Português do Brasil
    locales_para_tentar = ['pt_BR.UTF-8', 'Portuguese_Brazil.1252', 'pt_BR']
    
    # 1. Salva a configuração de locale original para restaurar depois
    locale_original = locale.getlocale(locale.LC_ALL)

    try:
        # 2. Tenta definir o locale do sistema para pt-BR
        locale_definido = False
        for loc in locales_para_tentar:
            try:
                # LC_ALL afeta todas as configurações de localização (moeda, número)
                locale.setlocale(locale.LC_ALL, loc) 
                locale_definido = True
                break
            except locale.Error:
                continue

        # 3. Fallback: Se não conseguir definir o pt-BR, usa um locale que use vírgula decimal (ex: Alemão)
        if not locale_definido:
            # Nota: O locale 'C' ou 'en_US' usaria ponto decimal.
            locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')


        # 4. Usa locale.format_string para formatar:
        # '%.2f' -> Define 2 casas decimais.
        # grouping=True -> Ativa o separador de milhar (que será o ponto no pt-BR).
        # O separador decimal (vírgula) é definido automaticamente pelo locale ativo.
        valor_formatado_string = locale.format_string('%.2f', valor_numerico, grouping=True)
        
        return valor_formatado_string

    except Exception as e:
        print(f"Alerta: Erro na formatação de locale ({e}). Retornando formato simples.")
        # 5. Em caso de falha total, retorna a formatação Python simples com a substituição manual (fallback)
        return str(round(valor_numerico, 2)).replace('.', ',')
        
    finally:
        # 6. RESTAURA o locale original para não afetar outras threads/chamadas na sua aplicação
        try:
            locale.setlocale(locale.LC_ALL, locale_original)
        except locale.Error:
            pass # Ignora se o locale original for nulo/inválido

# --- Exemplo de Uso (Você pode rodar este bloco para testar) ---
if __name__ == "__main__":
    
    # Valores de exemplo:
    preco_imovel_a = 75000.00
    preco_imovel_b = 1254321.75
    preco_imovel_c = 450.0

    # Chamada da função e saída:
    valor_a_final = formatar_valor_para_pt_br(preco_imovel_a)
    valor_b_final = formatar_valor_para_pt_br(preco_imovel_b)
    valor_c_final = formatar_valor_para_pt_br(preco_imovel_c)
    
    print(f"Preço 1 original (float): {preco_imovel_a}")
    print(f"Preço 1 formatado (string): {valor_a_final}")
    print("-" * 20)
    print(f"Preço 2 original (float): {preco_imovel_b}")
    print(f"Preço 2 formatado (string): {valor_b_final}")
    print("-" * 20)
    print(f"Preço 3 original (float): {preco_imovel_c}")
    print(f"Preço 3 formatado (string): {valor_c_final}")

    # Saída esperada:
    # Preço 1 formatado (string): 75.000,00
    # Preço 2 formatado (string): 1.254.321,75
    # Preço 3 formatado (string): 450,00