import os
import json

# ================= CONFIGURAÇÃO =================
ARQUIVO_L2D = "l2d.json"
DIRETORIO_ATUAL = os.getcwd()
ARQUIVO_SAIDA = "lista_l2d_formatada.txt"
# ================================================

def gerar_lista_l2d():
    # 1. Verifica se o l2d.json existe
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

    itens_lista = []

    print("Varrendo diretórios e gerando lista...\n")

    # 3. Varre os modelos do JSON para verificar quais pastas realmente existem
    for modelo in modelos:
        nome_modelo = modelo.get("name")
        id_modelo = modelo.get("id")

        if not id_modelo or not nome_modelo:
            continue

        caminho_pasta = os.path.join(DIRETORIO_ATUAL, id_modelo)

        # Se a pasta do modelo existir no diretório atual, adicionamos na lista
        if os.path.isdir(caminho_pasta):
            itens_lista.append({
                "label": nome_modelo,
                "value": id_modelo
            })

    if not itens_lista:
        print("Nenhuma pasta correspondente aos IDs do l2d.json foi encontrada.")
        return

    # 4. Formata o texto exatamente com o recuo e estrutura que você pediu
    blocos = []
    total_itens = len(itens_lista)

    for i, item in enumerate(itens_lista):
        bloco = f'''                    {{
                        "label": "{item['label']}",
                        "value": "{item['value']}"
                    }}'''
        # Adiciona a vírgula em todos, exceto no último item
        if i < total_itens - 1:
            bloco += ","
            
        blocos.append(bloco)

    conteudo_final = "\n".join(blocos)

    # 5. Salva no arquivo TXT
    try:
        with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f_out:
            f_out.write(conteudo_final)
        print("\n" + "="*40)
        print("Lista gerada com sucesso!")
        print(f"Modelos válidos e listados: {total_itens}")
        print(f"Salvo em: '{ARQUIVO_SAIDA}'")
        print("="*40)
    except Exception as e:
        print(f"Erro ao salvar o arquivo de saída: {e}")

if __name__ == "__main__":
    gerar_lista_l2d()