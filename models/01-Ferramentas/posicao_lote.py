import os
import json
import glob

def obter_versao_spine(caminho_pasta):
    """
    Procura o arquivo .skel na pasta, lê os primeiros 16 bytes
    e retorna se o modelo é 'novo' (4.1) ou 'antigo' (4.0, 3.8, 3.7).
    """
    # Procura por qualquer arquivo .skel dentro da pasta do personagem
    arquivos_skel = glob.glob(os.path.join(caminho_pasta, "*.skel"))
    
    if not arquivos_skel:
        return None
        
    caminho_skel = arquivos_skel[0] # Pega o primeiro .skel que encontrar
    
    try:
        # Abre o arquivo em modo de leitura binária ("rb")
        with open(caminho_skel, "rb") as f:
            bytes_iniciais = f.read(16)
            
            # Decodifica para texto ignorando erros e removendo caracteres nulos (\x00)
            version_string = bytes_iniciais.decode('utf-8', errors='ignore').replace('\x00', '')
            
            # Decide qual versão é com base na string encontrada
            if "4.1" in version_string:
                return "novo"
            elif any(v in version_string for v in ["4.0", "3.8", "3.7"]):
                return "antigo"
            else:
                return None
    except Exception as e:
        print(f"⚠️ Erro ao ler {caminho_skel}: {e}")
        return None

def editar_posicao():
    print("--- Editor de Posicionamento Inteligente (Spine) ---")
    variante_alvo = input("Qual variante deseja ajustar (ex: default, cover, aim)? ").strip().lower()
    
    # Coleta as configurações para modelos antigos
    print("\n--- Posições para Modelos ANTIGOS (Spine 3.7, 3.8, 4.0) ---")
    try:
        antigo_x = int(input("Digite o valor de X: "))
        antigo_y = int(input("Digite o valor de Y: "))
        antigo_scale = float(input("Digite o valor de Scale (tamanho): "))
        
        # Coleta as configurações para modelos novos
        print("\n--- Posições para Modelos NOVOS (Spine 4.1) ---")
        novo_x = int(input("Digite o valor de X: "))
        novo_y = int(input("Digite o valor de Y: "))
        novo_scale = int(input("Digite o valor de Scale (tamanho): "))
    except ValueError:
        print("❌ Erro: Os valores devem ser números. (Use . para decimais no Scale se necessário)")
        return

    sucessos = 0
    ignorados = 0
    
    # Percorre todas as pastas
    for pasta in os.listdir("."):
        caminho_config = os.path.join(pasta, "config.json")
        
        # Só prossegue se for uma pasta que contenha o config.json
        if not os.path.isfile(caminho_config):
            continue
            
        # 1. Checa a versão do Spine
        versao = obter_versao_spine(pasta)
        
        if not versao:
            print(f"⚠️ Ignorado: Pasta '{pasta}' não possui arquivo .skel reconhecido.")
            ignorados += 1
            continue
            
        # 2. Define os valores dinâmicos com base na versão
        if versao == "novo":
            x_alvo, y_alvo, scale_alvo = novo_x, novo_y, novo_scale
            tag = "[Spine 4.1]"
        else:
            x_alvo, y_alvo, scale_alvo = antigo_x, antigo_y, antigo_scale
            tag = "[Spine <4.1]"

        # 3. Lê e atualiza o config.json
        with open(caminho_config, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except:
                continue
        
        if "variants" in data:
            modificado = False
            for v in data["variants"]:
                if v.get("id", "").lower() == variante_alvo:
                    v["position"] = {
                        "x": x_alvo,
                        "y": y_alvo,
                        "scale": scale_alvo
                    }
                    modificado = True
            
            # 4. Salva o arquivo modificado
            if modificado:
                with open(caminho_config, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                print(f"✅ Atualizado: {pasta} {tag}")
                sucessos += 1

    print(f"\n🚀 Concluído! {sucessos} arquivos atualizados com sucesso ({ignorados} ignorados).")

if __name__ == "__main__":
    editar_posicao()