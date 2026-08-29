import os
import json
import requests

# Configurações do Repositório do Nikke-db
REPO_OWNER = "Nikke-db"
REPO_NAME = "Nikke-db.github.io"
BRANCH = "main"

def main():
    # 1. Carrega o arquivo local models.json
    try:
        with open("models.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Erro: O arquivo 'models.json' não foi encontrado na pasta atual.")
        return

    # Pega apenas os IDs listados no JSON
    target_ids = [item['id'] for item in data.get('models', [])]
    print(f"Encontrados {len(target_ids)} modelos para baixar no seu JSON.\n")

    # 2. Pede a estrutura de pastas do repositório via API (recursivo)
    # Isso evita bater no limite da API do GitHub ao verificar pastas individualmente
    print("Mapeando os arquivos no repositório oficial do Nikke-db...")
    tree_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/trees/{BRANCH}?recursive=1"
    response = requests.get(tree_url)
    
    if response.status_code != 200:
        print("Erro ao acessar a API do GitHub:", response.text)
        return
    
    tree = response.json().get('tree', [])
    
    # 3. Processa cada modelo da sua lista
    for char_id in target_ids:
        print(f"\n[{char_id}] Procurando arquivos no GitHub...")
        
        # Filtra na árvore do GitHub apenas arquivos que comecem com l2d/ID/ (ex: l2d/c010/)
        prefix = f"l2d/{char_id}/"
        files_to_download = [item for item in tree if item['type'] == 'blob' and item['path'].startswith(prefix)]
        
        if not files_to_download:
            print(f"[{char_id}] Nenhum arquivo encontrado no repositório deles. Pulando.")
            continue
            
        for file_item in files_to_download:
            repo_path = file_item['path']  # Ex: "l2d/c010/aim/aim.skel"
            
            # Remove o "l2d/" do começo para bater com a estrutura da sua pasta local
            # "l2d/c010/aim/aim.skel" vira "c010/aim/aim.skel"
            local_path = repo_path.replace("l2d/", "", 1)
            
            # Protege o seu config.json! Se o arquivo no repo deles for config.json, ele não baixa.
            if os.path.basename(local_path).lower() == "config.json":
                print(f"  -> Ignorando {local_path} (para proteger o seu arquivo local)")
                continue
            
            # Cria as pastas locais (ex: aim/, cover/) caso elas não existam
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # URL crua para baixar o arquivo real sem passar pela interface do GitHub
            raw_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{repo_path}"
            
            # Verifica se você já baixou esse arquivo antes (para não gastar internet à toa)
            if os.path.exists(local_path):
                print(f"  -> Já existe: {local_path} (Pulando)")
                continue
                
            print(f"  -> Baixando: {local_path} ...", end=" ")
            
            # Faz o download do arquivo
            try:
                file_resp = requests.get(raw_url, stream=True)
                file_resp.raise_for_status()
                
                with open(local_path, 'wb') as lf:
                    for chunk in file_resp.iter_content(chunk_size=8192):
                        lf.write(chunk)
                print("OK")
            except Exception as e:
                print(f"ERRO: {e}")

    print("\nDownload concluído! Verifique suas pastas.")

if __name__ == "__main__":
    main()