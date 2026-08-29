import os
import shutil

# 1. COLE AQUI o array/lista de IDs que você copiou do console do navegador
modelos_para_mover = ["c010","c010_01","c010_02","c011","c011_01","c012","c013","c020","c022","c022_01",
"c030","c030_01","c032","c040","c060","c061","c070","c070_01","c071","c072","c072_01","c080","c080_01",
"c082","c090","c090_01","c091","c092","c100","c101","c102","c102_01","c110","c111","c112","c112_01","c120",
"c121","c130","c131","c140","c140_01","c141","c141_01","c150","c150_01","c160_01","c170","c170_01","c171",
"c172","c180","c181","c181_01","c190","c191","c191_01","c193","c200","c201","c202","c202_01","c203","c210",
"c210_01","c212","c212_01","c220","c230","c231","c232","c233","c241","c242","c250","c251","c252","c253",
"c254","c255","c260","c261","c282","c291","c300","c301","c302","c303","c304","c305","c306","c307","c308",
"c311","c312","c350_old","c352","c352_01","c381","c392","c400","c401","c402","c430","c430_01","c431","c432",
"c570","c570_99","c800","c800_01","c801","c802","c803","c803_01","c804","c812","c813","c853","c900","c902",
"c902_01","c903","c903_01","c904","c905","c907","c907_01","c908","c910","c910_01","c911","c912","c914","c915",
"c916","c917","c918","c919","c920","c921","c922","c923","c924","c925","c928","c929","c930","c931","c931_01",
"c932","c933","c934","c935","c936","c937","c939","c940","c941","c942","c947","c948","c951","c952","c961",
"c961_01","c962","c963","c964","c967","c968","c969","c970","c974","c974_01","c975","c976","c985","c988",
"c989","c992","c993","c996","c8006","c997","c998","c9000","c9000_01","c9000_02","c9000_03","c9000_05",
"c9000_06","c9000_07","c9001","c9002","c9005","c9005_01","c9008","c9010","c9011","c9015","c9018","c9019",
"c9022","c9023","c9028","c9034","c9035","c9036","c9037","whitememory1","bowwowparadise","777","maidinvalentine",
"nyanyaparadise","goldenship","seayouagain","outerautomata","nocallerid","schooloflock","dazzlingcupid_naga","redash1",
"miraclesnow","neverland","newyearnewsword","lionheart","perfectmaid","recipeforyou","lastkingdom","darkhero","hightechtoy",
"goldencoinrush","claymore","aegisthediver","beautyfullshot","juveniledays","colorless","evangelion","phantomthief","lifeagain",
"secretgarden","icedragonsaga","footstepwalkrun","romanticvalentine","secondquest1","secondquest2","forrest","newflavor","trueflavor",
"unbreakablesphere","arcanearchive","lordforjustice","memoriesteller_1","memoriesteller_2","rebornevil","goninjathief","blankticket",
"terminusticket","arkguardian","sineditor","fatalmaid","liecauserecoil","enterheaven","twoxtwo1","twoxtwo2","goodworld","staranis",
"bsideidol","bitterspice","arkranger","smol_ade","smol_anchor","smol_anchor_pirate","smol_bolt","smol_frima","smol_helm","smol_liter",
"smol_mary","smol_mast","smol_mast_pirate","piratecafe","smol_pepper","smol_mpriv","smol_sin_pirate","smol_rapi","smol_yan","smol_rem",
"smol_ram","smol_emilia","smol_anis","smol_mint","smol_prika","azxservicetime_1","azxservicetime_2","azxservicetime_3","azxservicetime_4",
"azxservicetime_5","azxservicetime_6","azxservicetime_7","azxservicetime_8","azxservicetime_9","bba001","bbg001","bbg002","bbg003","eba001",
"eba003","eba003_green","eba003_hsta","ebg001","ebg002","mba002","mbg001","mbg002","mbg004","mbg004_appearance","favorite_c030","favorite_c210",
"story0001_2","story0002","story0002_2","story0003","story0201","story0401","story0401_2","story0401_3","story0405","story0702","story1201",
"story1302","story1303","story1401","story1403","story1405","story1501","story1902","story2002","story2101","story2201","story2202","story2206",
"story2501","story2602","c010","c010_01","c010_02"]

# 2. CONFIGURAÇÃO DE DIRETÓRIOS
# Define o diretório atual onde o script está rodando como ponto de partida
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))

# Nome da pasta de destino para os modelos não funcionais
PASTA_DESTINO_NOME = "noFunctionalModels"
caminho_destino_pai = os.path.join(DIRETORIO_ATUAL, PASTA_DESTINO_NOME)

def mover_pastas():
    # Garante que a pasta 'noFunctionalModels' exista
    if not os.path.exists(caminho_destino_pai):
        os.makedirs(caminho_destino_pai)
        print(f"📁 Pasta de destino criada: '{PASTA_DESTINO_NOME}'\n")

    sucessos = 0
    erros = 0
    nao_encontrados = 0

    # Remove duplicatas da sua lista por segurança
    lista_limpa = list(set(modelos_para_mover))

    print(f"🚀 Iniciando movimentação de {len(lista_limpa)} modelos...\n")

    for model_id in lista_limpa:
        # Caminho da pasta de origem (ex: ./c010)
        caminho_origem = os.path.join(DIRETORIO_ATUAL, model_id)
        
        # Caminho final na pasta de destino (ex: ./noFunctionalModels/c010)
        caminho_destino_final = os.path.join(caminho_destino_pai, model_id)

        # 1. Verifica se a pasta existe na origem
        if os.path.exists(caminho_origem) and os.path.isdir(caminho_origem):
            try:
                # Se já existir uma pasta com o mesmo nome no destino, removemos para evitar conflitos
                if os.path.exists(caminho_destino_final):
                    shutil.rmtree(caminho_destino_final)
                
                # Move a pasta fisicamente
                shutil.move(caminho_origem, caminho_destino_final)
                print(f"✅ [SUCESSO] Movido: {model_id} -> {PASTA_DESTINO_NOME}/{model_id}")
                sucessos += 1
            except Exception as e:
                print(f"❌ [ERRO] Falha ao mover '{model_id}': {e}")
                erros += 1
        else:
            print(f"⚠️  [AVISO] Pasta não encontrada localmente: '{model_id}'")
            nao_encontrados += 1

    # Resumo final da operação no terminal
    print("\n" + "="*40)
    print("📊 RESUMO DA OPERAÇÃO:")
    print(f"   - Movidos com sucesso: {sucessos}")
    print(f"   - Não encontrados: {nao_encontrados}")
    print(f"   - Erros: {erros}")
    print("="*40)

if __name__ == "__main__":
    mover_pastas()