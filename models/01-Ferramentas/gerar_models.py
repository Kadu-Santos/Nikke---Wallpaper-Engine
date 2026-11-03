import os
import json

# ================= CONFIGURAÇÃO =================
ARQUIVO_L2D = "l2d.json"
DIRETORIO_ATUAL = os.getcwd()
ARQUIVO_SAIDA = "models.json"  # Nome do JSON que será gerado
# ================================================

def gerar_index():
    # 1. Verifica se o arquivo l2d.json existe no local
    if not os.path.exists(ARQUIVO_L2D):
        print(f"Erro: O arquivo '{ARQUIVO_L2D}' não foi encontrado no diretório atual.")
        return

    # 2. Carrega as informações do l2d.json
    try:
        with open(ARQUIVO_L2D, "r", encoding="utf-8-sig") as f:
            modelos = json.load(f)
    except Exception as e:
        print(f"Erro ao ler o arquivo '{ARQUIVO_L2D}': {e}")
        return

    lista_modelos = []

    print("Varrendo pastas e gerando index de configurações...\n")

    # 3. Verifica quais pastas de fato existem e monta a estrutura
    for modelo in modelos:
        id_modelo = modelo.get("id")

        if not id_modelo:
            continue

        caminho_pasta = os.path.join(DIRETORIO_ATUAL, id_modelo)

        # Se a pasta correspondente ao ID existir no diretório atual, monta o item
        if os.path.isdir(caminho_pasta):
            # No JSON, usamos barras normais (/) mesmo no Windows para caminhos relativos de web/assets
            lista_modelos.append({
                "id": id_modelo,
                "config": f"{id_modelo}/config.json"
            })

    # Estrutura final exatamente como você pediu
    json_final = {
        "models": lista_modelos
    }

    # 4. Grava o novo arquivo JSON bem formatado
    try:
        with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f_out:
            json.dump(json_final, f_out, indent=4, ensure_ascii=False)
        
        print("="*40)
        print("Arquivo JSON gerado com sucesso!")
        print(f"Total de modelos indexados: {len(lista_modelos)}")
        print(f"Salvo em: '{ARQUIVO_SAIDA}'")
        print("="*40)
        
    except Exception as e:
        print(f"Erro ao salvar o arquivo JSON: {e}")

if __name__ == "__main__":
    gerar_index()