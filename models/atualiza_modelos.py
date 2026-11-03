import os
import json
import shutil
import requests

# ================= CONFIGURAÇÃO =================
URL_L2D_GITHUB = "https://raw.githubusercontent.com/Nikke-db/Nikke-db.github.io/main/js/json/l2d.json"
REPO_OWNER = "Nikke-db"
REPO_NAME = "Nikke-db.github.io"
BRANCH = "main"
DIRETORIO_ATUAL = os.getcwd()
ARQUIVO_SAIDA = "models.json"
PASTA_NOVOS = "novos_modelos"

MODELOS_IGNORADOS = "777; absolute; acpufreeze; aegisthediver; alonesurvivor; arcanearchive; arkguardian; arkranger; azxservicetime_1; azxservicetime_2; azxservicetime_3; azxservicetime_4; azxservicetime_5; azxservicetime_6; azxservicetime_7; azxservicetime_8; azxservicetime_9; bba001; bbg001; bbg002; bbg003; beautyfullshot; bitterspice; blankticket; bluewaterisland; boomsday; boomtheghost; bowwowparadise; brandnewyear; bsideidol; c010_01; c250; c251; c252; c253; c254; c255; c322; c530; c8006; c803; c803_01; c804; c812; c813; c853; c9000; c9000_01; c9000_02; c9000_03; c9000_05; c9000_06; c9000_07; c9001; c9002; c9005; c9005_01; c9008; c9010; c9011; c9015; c9019; c902; c9022; c9023; c9028; c902_01; c903; c9034; c9035; c9036; c9037; c903_01; c907_01; c910; c910_01; c911; c912; c914; c915; c916; c917; c918; c919; c920; c921; c922; c923; c924; c925; c930; c931; c931_01; c932; c933; c934; c935; c936; c937; c939; c942; c947; c948; c951; c952; c960; c961; c961_01; c962; c963; c964; c967; c968; c969; c974; c974_01; c975; c976; c985; c988; c992; c994; c996; c997; c998; cherryblossom; claymore; coinsinrush; colorless; darkhero; dazzlingcupid_naga; dazzlingcupid_tia; dirtybackyard; doutsider; eba001; eba003; eba003_green; eba003_hsta; ebg001; ebg002; enterheaven; evangelion; fatalmaid; favorite_c030; favorite_c032; favorite_c072; favorite_c100; favorite_c101; favorite_c112; favorite_c141; favorite_c142; favorite_c150; favorite_c192; favorite_c210; favorite_c352; favorite_c550; footstepwalkrun; forrest; goldencoinrush; goldenship; goninjathief; goodworld; hightechtoy; icedragonsaga; jinxplayer; juveniledays; killthelord; lastkingdom; liecauserecoil; lifeagain; lionheart; lordforjustice; ltk; maidinvalentine; mba002; mbg001; mbg002; mbg004; mbg004_appearance; memoriesteller_1; memoriesteller_2; miraclesnow; neverland; newflavor; newyearnewsword; nocallerid; nyanyaparadise; oldtales; onemoretime; outerautomata; overthehorizon; perfectmaid; phantomthief; piratecafe; queensorder; rebornevil; recipeforyou; redash1; redash2; romanticvalentine; schooloflock; seayouagain; secondquest1; secondquest2; secretgarden; sineditor; smol_ade; smol_anchor; smol_anchor_pirate; smol_anis; smol_bolt; smol_emilia; smol_frima; smol_helm; smol_liter; smol_mary; smol_mast; smol_mast_pirate; smol_mint; smol_mpriv; smol_pepper; smol_prika; smol_ram; smol_rapi; smol_rem; smol_sin_pirate; smol_yan; staranis; story0001; story0001_2; story0002; story0002_2; story0003; story0201; story0401; story0401_2; story0401_3; story0405; story0702; story1201; story1302; story1303; story1401; story1403; story1405; story1501; story1902; story2002; story2101; story2201; story2202; story2206; story2501; story2602; terminusticket; trueflavor; twoxtwo1; twoxtwo2; unbreakablesphere; whitememory1; whitememory2; wisdomspring;".split("; ")
# ================================================

def main():
    print("=== ETAPA 1: Baixando e processando l2d.json do GitHub ==~")
    try:
        response = requests.get(URL_L2D_GITHUB)
        if response.status_code != 200:
            print(f"Erro ao baixar o l2d.json. Status code: {response.status_code}")
            return
        modelos_github = response.json()
    except Exception as e:
        print(f"Erro ao processar o l2d.json do GitHub: {e}")
        return

    ids_no_github = [m.get("id") for m in modelos_github if m.get("id")]
    
    lista_modelos_index = []
    pastas_locais_existentes = []

    # Varre as pastas locais atuais para ver quais já existem
    for item in os.listdir(DIRETORIO_ATUAL):
        caminho_item = os.path.join(DIRETORIO_ATUAL, item)
        if os.path.isdir(caminho_item) and item not in [PASTA_NOVOS, '.git', '__pycache__']:
            pastas_locais_existentes.append(item)

    # Filtra e monta o models.json apenas com as pastas que já existem localmente (e não estão ignoradas)
    for id_modelo in ids_no_github:
        if id_modelo in MODELOS_IGNORADOS:
            continue
            
        caminho_pasta = os.path.join(DIRETORIO_ATUAL, id_modelo)
        if os.path.isdir(caminho_pasta):
            lista_modelos_index.append({
                "id": id_modelo,
                "config": f"{id_modelo}/config.json"
            })

    # Salva o models.json atualizado
    json_final = {"models": lista_modelos_index}
    try:
        with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f_out:
            json.dump(json_final, f_out, indent=4, ensure_ascii=False)
        print(f"Arquivo '{ARQUIVO_SAIDA}' gerado com sucesso! ({len(lista_modelos_index)} modelos indexados).\n")
    except Exception as e:
        print(f"Erro ao salvar o arquivo JSON: {e}")
        return

    print("=== ETAPA 2: Mapeando e baixando atualizações do GitHub ===")
    tree_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/trees/{BRANCH}?recursive=1"
    tree_resp = requests.get(tree_url)
    
    if tree_resp.status_code != 200:
        print("Erro ao acessar a API do GitHub para download:", tree_resp.text)
        return
    
    tree = tree_resp.json().get('tree', [])
    target_ids = [item['id'] for item in lista_modelos_index]

    for char_id in target_ids:
        if char_id in MODELOS_IGNORADOS:
            continue
            
        print(f"\n[{char_id}] Verificando arquivos no GitHub...")
        prefix = f"l2d/{char_id}/"
        files_to_download = [item for item in tree if item['type'] == 'blob' and item['path'].startswith(prefix)]
        
        if not files_to_download:
            continue
            
        for file_item in files_to_download:
            repo_path = file_item['path']
            local_path = repo_path.replace("l2d/", "", 1)
            
            # Protege o config.json local
            if os.path.basename(local_path).lower() == "config.json":
                continue
            
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            raw_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{repo_path}"
            
            if os.path.exists(local_path):
                continue
                
            print(f"  -> Baixando: {local_path} ...", end=" ")
            try:
                file_resp = requests.get(raw_url, stream=True)
                file_resp.raise_for_status()
                with open(local_path, 'wb') as lf:
                    for chunk in file_resp.iter_content(chunk_size=8192):
                        lf.write(chunk)
                print("OK")
            except Exception as e:
                print(f"ERRO: {e}")

    print("\n=== ETAPA 3: Organizando novos modelos ===")
    os.makedirs(PASTA_NOVOS, exist_ok=True)
    
    # Identifica pastas que estão no GitHub / diretório, mas não estavam na lista indexada oficial ou local configurada
    ids_indexados = set(target_ids)
    ids_ignorados_set = set(MODELOS_IGNORADOS)
    
    movidos_count = 0
    for item in os.listdir(DIRETORIO_ATUAL):
        caminho_item = os.path.join(DIRETORIO_ATUAL, item)
        # Se for diretório, não for a pasta de novos modelos, não for pasta oculta/sistema e não estiver indexado/ignorado
        if (os.path.isdir(caminho_item) 
            and item not in [PASTA_NOVOS, '.git', '__pycache__'] 
            and item not in ids_indexados 
            and item not in ids_ignorados_set):
            
            destino_novo = os.path.join(DIRETORIO_ATUAL, PASTA_NOVOS, item)
            if not os.path.exists(destino_novo):
                shutil.move(caminho_item, destino_novo)
                print(f"  -> Novo modelo não catalogado encontrado e movido para '{PASTA_NOVOS}/': {item}")
                movidos_count += 1

    print("\n" + "="*40)
    print("Processo concluído com sucesso!")
    if movidos_count > 0:
        print(f"Total de novos modelos movidos para configuração manual: {movidos_count}")
    else:
        print("Nenhum modelo novo pendente encontrado.")
    print("="*40)

if __name__ == "__main__":
    main()