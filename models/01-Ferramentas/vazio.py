import os
import json

def verificar_pastas_orfas():
    # 1. Carrega o arquivo de configuração de modelos
    # Ajuste o nome do arquivo se for 'models.json' ou outro
    arquivo_config = "models.json" 
    
    if not os.path.exists(arquivo_config):
        print(f"❌ Erro: O arquivo {arquivo_config} não foi encontrado.")
        return

    with open(arquivo_config, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Extrai uma lista de todos os IDs listados no JSON
        ids_no_json = {m['id'] for m in data.get('models', [])}

    print(f"✅ Arquivo carregado. {len(ids_no_json)} modelos mapeados no JSON.")
    print("-" * 40)

    # 2. Lista todas as pastas no diretório atual
    pastas_no_diretorio = [d for d in os.listdir(".") if os.path.isdir(d)]
    
    # Ignora pastas que começam com ponto (como .git, .vscode)
    pastas_reais = [p for p in pastas_no_diretorio if not p.startswith(".")]

    # 3. Compara
    encontrou_orfa = False
    for pasta in pastas_reais:
        # Se a pasta não estiver no conjunto de IDs, é órfã
        if pasta not in ids_no_json:
            print(f"⚠️ Pasta órfã encontrada: {pasta}")
            encontrou_orfa = True

    if not encontrou_orfa:
        print("🎉 Tudo certo! Não há pastas órfãs no diretório.")
    else:
        print("-" * 40)
        print("Estas pastas estão no disco, mas não estão declaradas no seu arquivo de configuração.")

if __name__ == "__main__":
    verificar_pastas_orfas()