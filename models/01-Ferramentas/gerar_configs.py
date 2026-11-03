import os
import json

def criar_configs_nikke():
    # Caminho do arquivo l2d.json
    l2d_path = "l2d.json"
    
    # Verifica se o arquivo base l2d.json existe
    if not os.path.exists(l2d_path):
        print(f"Erro: O arquivo '{l2d_path}' não foi encontrado no diretório atual.")
        return

    # Carrega a lista de personagens
    with open(l2d_path, "r", encoding="utf-8") as f:
        personagens = json.load(f)

    # Contador para exibir o status no final
    pastas_processadas = 0

    for char in personagens:
        char_id = char.get("id")
        char_name = char.get("name")

        if not char_id:
            continue

        # Caminho absoluto/relativo para a pasta do ID (ex: ./c010)
        char_folder_path = os.path.join(".", char_id)

        # Só trabalha na pasta se ela realmente existir fisicamente
        if os.path.isdir(char_folder_path):
            # Verifica se as subpastas "aim" e "cover" existem dentro da pasta do ID
            has_aim = os.path.isdir(os.path.join(char_folder_path, "aim"))
            has_cover = os.path.isdir(os.path.join(char_folder_path, "cover"))

            # 1. Criação da variante obrigatória: 'default'
            variants = [
                {
                    "id": "default",
                    "folder": "",
                    "position": {
                        "x": 9,
                        "y": -25,
                        "scale": 6
                    },
                    "animations": {
                        "idle": "idle",
                        "action": "action",
                        "hit": "angry"
                    },
                    "model": {
                        "skeleton": f"{char_id}_00.skel",
                        "atlas": f"{char_id}_00.atlas"
                    }
                }
            ]

            # 2. Se as subpastas existirem, adiciona dinamicamente 'cover' e 'aim'
            if has_cover:
                variants.append({
                    "id": "cover",
                    "folder": "cover",
                    "position": {
                        "x": 0,
                        "y": -10,
                        "scale": 7
                    },
                    "animations": {
                        "idle": "cover_idle",
                        "action": "cover_reload",
                        "hit": "cover_stun"
                    },
                    "model": {
                        "skeleton": f"{char_id}_cover_00.skel",
                        "atlas": f"{char_id}_cover_00.atlas"
                    }
                })

            if has_aim:
                variants.append({
                    "id": "aim",
                    "folder": "aim",
                    "position": {
                        "x": 0,
                        "y": -10,
                        "scale": 7
                    },
                    "animations": {
                        "idle": "aim_idle",
                        "action": "aim_fire",
                        "hit": "aim_hit"
                    },
                    "model": {
                        "skeleton": f"{char_id}_aim_00.skel",
                        "atlas": f"{char_id}_aim_00.atlas"
                    }
                })

            # Monta a estrutura final do config.json
            config_data = {
                "name": char_name,
                "appearance": {
                    "color1": "#005372",
                    "color2": "#000b63"
                },
                "variants": variants
            }

            # Caminho de destino para salvar o config.json do respectivo modelo
            config_file_path = os.path.join(char_folder_path, "config.json")

            # Grava o config.json na pasta do ID
            with open(config_file_path, "w", encoding="utf-8") as out_file:
                json.dump(config_data, out_file, indent=4, ensure_ascii=False)

            print(f"✓ Config.json criado com sucesso em: {char_folder_path} (Variantes: {len(variants)})")
            pastas_processadas += 1
        else:
            print(f"⚠️ Pasta '{char_id}' não encontrada no diretório local. Ignorando...")

    print(f"\nConcluído! Total de pastas atualizadas: {pastas_processadas}")

if __name__ == "__main__":
    criar_configs_nikke()