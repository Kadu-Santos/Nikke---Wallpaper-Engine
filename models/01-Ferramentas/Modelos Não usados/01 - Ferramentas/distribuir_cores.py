import os
import json
import random

ARQUIVO_CORES = "banco_de_cores.json"
ARQUIVO_L2D = "l2d.json"

def carregar_banco_cores():
    """Carrega o banco de cores gerado anteriormente."""
    if not os.path.exists(ARQUIVO_CORES):
        print(f"❌ Erro: O arquivo {ARQUIVO_CORES} não foi encontrado!")
        return {}
    with open(ARQUIVO_CORES, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f"❌ Erro ao decodificar {ARQUIVO_CORES}.")
            return {}

def carregar_l2d():
    """Carrega o l2d.json suportando diferentes estruturas."""
    if not os.path.exists(ARQUIVO_L2D):
        print(f"❌ Erro: O arquivo {ARQUIVO_L2D} não foi encontrado!")
        return []
    
    with open(ARQUIVO_L2D, 'r', encoding='utf-8') as f:
        dados = json.load(f)
        
        lista_personagens = []
        if isinstance(dados, dict):
            for k, v in dados.items():
                if isinstance(v, dict) and "name" in v:
                    lista_personagens.append({"id": k, "name": v["name"]})
                elif isinstance(v, str):
                    lista_personagens.append({"id": k, "name": v})
        elif isinstance(dados, list):
            for item in dados:
                if "id" in item and "name" in item:
                    lista_personagens.append(item)
        return lista_personagens

def extrair_base_nome(nome):
    """Extrai o nome base do personagem removendo subtítulos, hífens ou parênteses."""
    nome_lower = nome.lower().strip()
    for sep in [':', '-', '_', '(']:
        if sep in nome_lower:
            nome_lower = nome_lower.split(sep)[0].strip()
    # Retorna o primeiro termo principal (ex: 'rapi white promise' vira 'rapi')
    return nome_lower.split()[0] if nome_lower else ""

def buscar_cores_para_nome(nome_personagem, banco_cores):
    """Pesquisa inteligente de cores cruzando o nome do l2d com o banco de cores."""
    nome_lower = nome_personagem.lower().strip()
    
    # 1. Correspondência exata
    if nome_lower in banco_cores:
        return banco_cores[nome_lower]
    
    # 2. Pesquisa fatiando por separadores (ex: "Rapi: Pure Grace" -> "Rapi")
    for sep in [':', '-', '_', '(']:
        if sep in nome_lower:
            partes = nome_lower.split(sep)
            for i in range(len(partes), 0, -1):
                candidato = sep.join(partes[:i]).strip()
                if candidato in banco_cores:
                    return banco_cores[candidato]
                    
    # 3. Pesquisa pelo nome base genérico
    base = extrair_base_nome(nome_personagem)
    if base in banco_cores:
        return banco_cores[base]
        
    # 4. Procura se alguma chave do banco inicia o nome (ou vice-versa)
    for chave, cores in banco_cores.items():
        if nome_lower.startswith(chave) or chave.startswith(nome_lower):
            return cores
            
    return []

def atualizar_configs_com_cores():
    banco_cores = carregar_banco_cores()
    personagens_l2d = carregar_l2d()

    if not banco_cores or not personagens_l2d:
        print("❌ Dados insuficientes para realizar a operação.")
        return

    # Agrupa as variantes por nome base para tratar pools de cores compartilhadas
    grupos_por_base = {}
    for p in personagens_l2d:
        base = extrair_base_nome(p["name"])
        if base not in grupos_por_base:
            grupos_por_base[base] = []
        grupos_por_base[base].append(p)

    sucessos = 0
    ignorados = 0

    print("🚀 Iniciando a distribuição inteligente de cores...\n")

    for base, variantes in grupos_por_base.items():
        # Tenta encontrar o pool de cores para este grupo base
        cores_pool = []
        for var in variantes:
            cores_encontradas = buscar_cores_para_nome(var["name"], banco_cores)
            if cores_encontradas:
                cores_pool = cores_encontradas
                break
        
        if not cores_pool and base in banco_cores:
            cores_pool = banco_cores[base]

        # Se não encontrou nenhuma cor para este grupo, ignora
        if not cores_pool:
            ignorados += len(variantes)
            continue

        print(f"🎨 Grupo '{base}': {len(cores_pool)} cor(es) encontrada(s) para {len(variantes)} variante(s).")

        # Distribui as cores de forma aleatória entre as variantes encontradas
        for var in variantes:
            model_id = var["id"]
            char_name = var["name"]
            caminho_config = os.path.join(model_id, 'config.json')

            if not os.path.exists(caminho_config):
                print(f"   ⚠️ Pasta ou config.json não encontrado para ID: {model_id} ({char_name})")
                continue

            # Sorteia aleatoriamente uma cor do pool daquele personagem
            cor_escolhida = random.choice(cores_pool)

            try:
                with open(caminho_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except json.JSONDecodeError:
                print(f"   ❌ Erro ao ler JSON da pasta {model_id}.")
                continue

            # Atualiza o bloco appearance com a cor sorteada para color1 e color2
            if "appearance" not in config:
                config["appearance"] = {}

            config["appearance"]["color1"] = cor_escolhida
            config["appearance"]["color2"] = cor_escolhida

            with open(caminho_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
                sucessos += 1
                print(f"   ✅ Atualizado [{model_id}] {char_name} -> Cor: {cor_escolhida}")

    print("\n" + "="*50)
    print("📊 RESUMO FINAL DA DISTRIBUIÇÃO:")
    print(f"   - Arquivos config.json atualizados: {sucessos}")
    print(f"   - Personagens/Variantes ignorados (sem cor no banco): {ignorados}")
    print("="*50)

if __name__ == "__main__":
    atualizar_configs_com_cores()