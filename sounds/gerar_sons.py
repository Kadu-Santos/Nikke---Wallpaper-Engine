import os
import json

PASTA_GENERICO = "generic"
PASTA_ESPECIAL = "especial"
ARQUIVO_SAIDA = "sounds.json"

def gerar_json_sons():
    # Estrutura base do nosso JSON
    mapa_sons = {
        "generico": {},
        "especial": {}
    }

    # 1. Processar a pasta 'generico'
    if os.path.exists(PASTA_GENERICO):
        for arquivo in os.listdir(PASTA_GENERICO):
            # Pega o nome sem a extensão (ex: 'ar.wav' vira 'ar')
            nome_base, ext = os.path.splitext(arquivo)
            
            # Limpa o nome para evitar problemas de maiúsculas/minúsculas
            arma_key = nome_base.lower().strip()
            
            # Monta o caminho do arquivo usando '/' para compatibilidade com web
            caminho_relativo = f"{PASTA_GENERICO}/{arquivo}"
            
            mapa_sons["generico"][arma_key] = caminho_relativo
    else:
        print(f"⚠️ Aviso: A pasta '{PASTA_GENERICO}' não foi encontrada.")

    # 2. Processar a pasta 'especial'
    if os.path.exists(PASTA_ESPECIAL):
        for arquivo in os.listdir(PASTA_ESPECIAL):
            # Garante que o arquivo tem tamanho suficiente para extrair o ID
            if len(arquivo) >= 4:
                # O ID da personagem são os 4 primeiros caracteres (ex: 'c500')
                id_personagem = arquivo[:4].lower()
                caminho_relativo = f"{PASTA_ESPECIAL}/{arquivo}"
                
                # Como uma personagem pode ter mais de um som especial, criamos uma lista
                if id_personagem not in mapa_sons["especial"]:
                    mapa_sons["especial"][id_personagem] = []
                
                mapa_sons["especial"][id_personagem].append(caminho_relativo)
    else:
        print(f"⚠️ Aviso: A pasta '{PASTA_ESPECIAL}' não foi encontrada.")

    # 3. Salvar o resultado no sounds.json
    with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
        json.dump(mapa_sons, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Sucesso! O arquivo '{ARQUIVO_SAIDA}' foi gerado e está pronto para uso.")

if __name__ == "__main__":
    gerar_json_sons()