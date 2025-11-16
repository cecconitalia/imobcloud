import locale
# =================================================================
# === CORREÇÃO 1: Adicionar a importação do num2words ===
# =================================================================
from num2words import num2words 


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
            # Tentar um locale comum que possa estar presente
            try:
                locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
            except locale.Error:
                try:
                    locale.setlocale(locale.LC_ALL, '') # Usa o default do sistema
                except locale.Error:
                    pass # Continua mesmo assim


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
        except (locale.Error, TypeError):
            pass # Ignora se o locale original for nulo/inválido

# =================================================================
# === CORREÇÃO 2: Adicionar a função 'valor_por_extenso' que faltava ===
# =================================================================
def valor_por_extenso(valor: float) -> str:
    """
    Converte um valor monetário (float) para seu valor por extenso em Reais (pt-BR).
    Ex: 1250.50 -> "mil duzentos e cinquenta reais e cinquenta centavos"
    
    Args:
        valor: O número float (ex: 1250.50)
        
    Returns:
        O valor por extenso como string (ex: "mil duzentos e cinquenta reais e cinquenta centavos")
    """
    if valor is None:
        return ""
        
    try:
        # Arredonda para 2 casas decimais para evitar problemas de precisão de float
        valor_arredondado = round(float(valor), 2)
        
        # Separa reais e centavos
        reais = int(valor_arredondado)
        # Multiplica por 100 e arredonda para pegar os centavos de forma segura
        centavos = int(round((valor_arredondado - reais) * 100))
        
        # Converte Reais
        extenso_reais = num2words(reais, lang='pt_BR')
        if reais == 1:
            extenso_reais_str = f"{extenso_reais} real"
        else:
            extenso_reais_str = f"{extenso_reais} reais"
        
        # Converte Centavos (se houver)
        extenso_centavos_str = ""
        if centavos > 0:
            extenso_centavos = num2words(centavos, lang='pt_BR')
            if centavos == 1:
                extenso_centavos_str = f" e {extenso_centavos} centavo"
            else:
                extenso_centavos_str = f" e {extenso_centavos} centavos"
        
        # Retorna a string final capitalizada
        return (f"{extenso_reais_str}{extenso_centavos_str}").capitalize()
    
    except Exception as e:
        print(f"Erro ao converter valor por extenso para {valor}: {e}")
        return "(Erro ao gerar valor por extenso)"
# =================================================================
# === FIM DA CORREÇÃO 2 ===
# =================================================================


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

    # Teste da nova função
    print("-" * 20)
    print(f"Valor por extenso (1250.50): {valor_por_extenso(1250.50)}")
    print(f"Valor por extenso (1.00): {valor_por_extenso(1.00)}")
    print(f"Valor por extenso (0.75): {valor_por_extenso(0.75)}")
    print(f"Valor por extenso (890000.00): {valor_por_extenso(890000.00)}")
    
    # Saída esperada:
    # Valor por extenso (1250.50): Mil duzentos e cinquenta reais e cinquenta centavos
    # Valor por extenso (1.00): Um real
    # Valor por extenso (0.75): Zero reais e setenta e cinco centavos
    # Valor por extenso (890000.00): Oitocentos e noventa mil reais