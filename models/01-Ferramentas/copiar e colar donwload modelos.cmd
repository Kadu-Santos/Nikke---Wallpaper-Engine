# 1. Cria a pasta principal e entra nela
New-Item -ItemType Directory -Force -Path "nikke_downloads" | Out-Null
Set-Location "nikke_downloads"

Write-Host "Inicializando a conexão com o repositório..." -ForegroundColor Cyan
# 2. Conecta ao repositório sem baixar nada ainda
git clone -n --depth=1 --filter=tree:0 https://github.com/Nikke-db/Nikke-db.github.io.git .

Write-Host "Configurando as pastas exatas que você quer..." -ForegroundColor Cyan
# 3. Informa ao Git a lista de pastas (tudo na mesma linha no PowerShell)
git sparse-checkout set "l2d/c103" "l2d/c103_01" "l2d/c105" "l2d/c105_01" "l2d/c9029" "l2d/c9031" "l2d/c9032" "l2d/c411_01" "l2d/c472" "l2d/c473" "l2d/c580_01" "l2d/c870" "l2d/c870_01" "l2d/c870_02" "l2d/c871" "l2d/c871_01" "l2d/c871_02" "l2d/c872"

Write-Host "Baixando os arquivos..." -ForegroundColor Cyan
# 4. Faz o download de fato
git checkout

# 5. Remove a pasta oculta .git para limpar a sujeira
Remove-Item -Recurse -Force .git

Write-Host "✅ Download concluído com sucesso!" -ForegroundColor Green