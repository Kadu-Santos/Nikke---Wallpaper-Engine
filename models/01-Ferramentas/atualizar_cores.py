import os
import json

ARQUIVO_CORES = 'cores.json'
ARQUIVO_L2D = 'l2d.json'

def carregar_cores():
    """Lê o arquivo cores.json e extrai o nome e a cor predominante."""
    mapa_cores = {}
    
    if not os.path.exists(ARQUIVO_CORES):
        print(f"❌ Erro: O arquivo {ARQUIVO_CORES} não foi encontrado!")
        return mapa_cores

    with open(ARQUIVO_CORES, 'r', encoding='utf-8') as f:
        try:
            dados_cores = json.load(f)
            for nome, info in dados_cores.items():
                cor = info.get("color", "").strip()
                if cor:
                    mapa_cores[nome.lower()] = cor
        except json.JSONDecodeError:
            print(f"❌ Erro ao decodificar {ARQUIVO_CORES}.")
            
    return mapa_cores

def carregar_l2d():
    """Lê o arquivo l2d.json para mapear ID -> Nome."""
    mapa_id_nome = {}
    
    if not os.path.exists(ARQUIVO_L2D):
        print(f"❌ Erro: O arquivo {ARQUIVO_L2D} não foi encontrado!")
        return mapa_id_nome

    with open(ARQUIVO_L2D, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    # Suporta diferentes formatos do l2d.json
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

def buscar_cor(nome_personagem, mapa_cores):
    """Busca a cor lidando com variantes e alts de personagens."""
    nome_lower = nome_personagem.lower().strip()
    
    # 1. Correspondência exata
    if nome_lower in mapa_cores:
        return mapa_cores[nome_lower]
    
    # 2. Separa por caracteres de variantes
    for separador in [':', '-', '(']:
        if separador in nome_lower:
            nome_base = nome_lower.split(separador)[0].strip()
            if nome_base in mapa_cores:
                return mapa_cores[nome_base]
    
    # 3. Fallback: verifica se começa com o nome base
    for nome_base, cor in mapa_cores.items():
        if nome_lower.startswith(nome_base):
            return cor
            
    return ""

def atualizar_arquivos():
    mapa_cores = carregar_cores()
    mapa_id_nome = carregar_l2d()

    if not mapa_cores:
        print("Nenhuma cor carregada. Encerrando operação.")
        return

    if not mapa_id_nome:
        print("Nenhum dado válido carregado do l2d.json. Encerrando operação.")
        return

    sucessos = 0
    ignorados = 0

    print("🚀 Iniciando a atualização de cores...\n")

    for model_id, character_name in mapa_id_nome.items():
        caminho_config = os.path.join(model_id, 'config.json')

        if not os.path.exists(caminho_config):
            continue

        with open(caminho_config, 'r', encoding='utf-8') as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                print(f"❌ Erro ao ler JSON da pasta {model_id}.")
                continue

        # Busca a cor inteligente baseada no nome
        cor_encontrada = buscar_cor(character_name, mapa_cores)

        # Se não encontrou a cor, apenas ignora e passa para o próximo (conforme solicitado)
        if not cor_encontrada:
            ignorados += 1
            continue

        # Atualiza o objeto appearance
        if "appearance" not in config:
            config["appearance"] = {}

        config["appearance"]["color1"] = cor_encontrada
        config["appearance"]["color2"] = cor_encontrada

        # Salva o arquivo preservando a ordem e formatação
        with open(caminho_config, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            sucessos += 1
            print(f"✅ Cores atualizadas em {model_id} ({character_name}) -> {cor_encontrada}")

    print("\n" + "="*40)
    print("📊 RESUMO DA OPERAÇÃO:")
    print(f"   - Atualizados com sucesso: {sucessos}")
    print(f"   - Ignorados (sem cor no cores.json): {ignorados}")
    print("="*40)

if __name__ == "__main__":
    atualizar_arquivos()