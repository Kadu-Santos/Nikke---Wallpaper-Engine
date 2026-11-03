import os
import json

# Defina os nomes dos arquivos de armas que o script deve procurar
ARQUIVOS_ARMAS = ["AR.txt", "RL.txt", "SR.txt", "SMG.txt", "SG.txt", "MG.txt"]

def carregar_armas():
    mapa_armas = {}
    for arquivo in ARQUIVOS_ARMAS:
        if os.path.exists(arquivo):
            tipo_arma = arquivo.replace(".txt", "")
            with open(arquivo, 'r', encoding='utf-8') as f:
                for linha in f:
                    nome_personagem = linha.strip()
                    if nome_personagem:
                        mapa_armas[nome_personagem.lower()] = tipo_arma
        else:
            print(f"⚠️ Aviso: Arquivo {arquivo} não encontrado no diretório. Ignorando...")
    return mapa_armas

def carregar_l2d():
    caminho_l2d = 'l2d.json'
    mapa_id_nome = {}
    
    if not os.path.exists(caminho_l2d):
        print(f"❌ Erro: O arquivo {caminho_l2d} não foi encontrado!")
        return mapa_id_nome

    with open(caminho_l2d, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    if isinstance(dados, dict):
        for chave, valor in dados.items():
            if isinstance(valor, dict) and "name" in valor:
                mapa_id_nome[chave] = valor["name"]
            elif isinstance(valor, str):
                mapa_id_nome[chave] = valor
    elif isinstance(dados, list):
        for item in dados:
            if "id" in item and "name" in item:
                mapa_id_nome[item["id"]] = item["name"]

    return mapa_id_nome

def buscar_arma(nome_personagem, mapa_armas):
    """
    Busca a arma de forma inteligente, lidando com variantes (ex: 'Rapi: Summer').
    """
    nome_lower = nome_personagem.lower().strip()
    
    # 1. Tenta a correspondência exata primeiro (ex: "Neon")
    if nome_lower in mapa_armas:
        return mapa_armas[nome_lower]
    
    # 2. Tenta separar por caracteres comuns em alts e buscar a base
    # Ex: "Rapi: Red Hood" -> pega só o "Rapi"
    for separador in [':', '-', '(']:
        if separador in nome_lower:
            nome_base = nome_lower.split(separador)[0].strip()
            if nome_base in mapa_armas:
                return mapa_armas[nome_base]
    
    # 3. Fallback final: verifica se o nome do personagem começa com algum nome base mapeado
    # Útil para casos sem separadores claros, ex: "Rapi Summer"
    for nome_base, arma in mapa_armas.items():
        if nome_lower.startswith(nome_base):
            return arma
            
    # Se realmente não encontrar nada, retorna vazio
    return ""

def atualizar_arquivos():
    mapa_armas = carregar_armas()
    mapa_id_nome = carregar_l2d()

    if not mapa_id_nome:
        print("Nenhum dado válido carregado do l2d.json. Encerrando operação.")
        return

    sucessos = 0

    for model_id, character_name in mapa_id_nome.items():
        caminho_config = os.path.join(model_id, 'config.json')

        if not os.path.exists(caminho_config):
            continue

        with open(caminho_config, 'r', encoding='utf-8') as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                print(f"❌ Erro ao ler o JSON da pasta {model_id}. Arquivo possivelmente corrompido.")
                continue

        novo_config = {}
        novo_config["id"] = model_id
        novo_config["name"] = config.get("name", character_name)

        variantes = config.get("variants", [])
        if len(variantes) > 1:
            # Chama a nossa nova função inteligente de busca
            tipo_arma = buscar_arma(character_name, mapa_armas)
            novo_config["weapon"] = tipo_arma

        for chave, valor in config.items():
            if chave not in novo_config:
                novo_config[chave] = valor

        with open(caminho_config, 'w', encoding='utf-8') as f:
            json.dump(novo_config, f, indent=4, ensure_ascii=False)
            sucessos += 1

    print(f"\n✅ Concluído! {sucessos} arquivos config.json foram atualizados com sucesso.")

if __name__ == "__main__":
    atualizar_arquivos()