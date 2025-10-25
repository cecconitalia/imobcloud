import os

def mostrar_estrutura_principal(caminho):
    try:
        itens = os.listdir(caminho)
    except PermissionError:
        print(f"[Sem permissão] {caminho}")
        return

    for item in itens:
        caminho_completo = os.path.join(caminho, item)
        if os.path.isdir(caminho_completo):
            print(f"📁 {item}")
            # Listar apenas subpastas diretas
            try:
                sub_itens = [p for p in os.listdir(caminho_completo) if os.path.isdir(os.path.join(caminho_completo, p))]
                for sub in sub_itens:
                    print(f"    📂 {sub}")
            except PermissionError:
                print("    [Sem permissão]")

if __name__ == "__main__":
    pasta_inicial = "."  # Caminho inicial
    print(f"Estrutura principal de: {os.path.abspath(pasta_inicial)}\n")
    mostrar_estrutura_principal(pasta_inicial)
