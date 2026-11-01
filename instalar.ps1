# Instalador do ambiente do administrativo (Windows 10/11).
# Uso (PowerShell), de dentro da pasta do projeto ja baixada:  .\instalar.ps1
# O repositorio e privado: o "git clone" pede login no GitHub na primeira vez.
#
# Idempotente: pode rodar de novo para atualizar. Texto sem acentos de proposito
# (PowerShell 5.1 le scripts sem BOM como ANSI).

param(
    [string]$Destino = (Join-Path $HOME "escritorio-adm"),
    [string]$Repo = "https://github.com/paulotony11/escritorio-adm.git"
)

$ErrorActionPreference = "Stop"

function Passo($texto) { Write-Host "`n==> $texto" -ForegroundColor Cyan }
function Tem($comando) { [bool](Get-Command $comando -ErrorAction SilentlyContinue) }
function AtualizarPath {
    $maquina = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $usuario = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$maquina;$usuario"
}
function InstalarComWinget($id, $nome) {
    Write-Host "Instalando $nome..."
    winget install --id $id -e --silent --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar $nome. Instale manualmente e rode de novo." }
    AtualizarPath
}

Passo "1/6 Verificando programas"
if (-not (Tem "winget")) {
    throw "winget nao encontrado. Atualize o 'Instalador de Aplicativo' na Microsoft Store e rode de novo."
}
if (-not (Tem "git")) { InstalarComWinget "Git.Git" "Git" }
if (-not (Tem "uv")) { InstalarComWinget "astral-sh.uv" "uv (gerenciador do Python)" }
if (-not (Tem "git") -or -not (Tem "uv")) {
    throw "Programas instalados, mas nao reconhecidos nesta janela. Feche e abra o PowerShell e rode de novo."
}

Passo "2/6 Baixando o projeto"
$emRepo = $PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot "pyproject.toml"))
if ($emRepo) {
    $Destino = $PSScriptRoot
    Write-Host "Usando a pasta atual: $Destino"
}
elseif (Test-Path (Join-Path $Destino ".git")) {
    git -C $Destino pull --ff-only
    if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel atualizar $Destino (alteracoes locais?)." }
}
elseif ((Test-Path $Destino) -and (Get-ChildItem $Destino -Force | Select-Object -First 1)) {
    throw "A pasta $Destino ja existe e nao esta vazia. Escolha outra com -Destino."
}
else {
    git clone $Repo $Destino
    if ($LASTEXITCODE -ne 0) { throw "Falha ao baixar $Repo. Se o repositorio for privado, faca login no GitHub." }
}
Set-Location $Destino

Passo "3/6 Criando pastas de trabalho"
foreach ($pasta in "dados\extratos", "dados\contratos", "dados\receber", "dados\pagar", "dados\custas", "relatorios", "modelos") {
    New-Item -ItemType Directory -Force -Path (Join-Path $Destino $pasta) | Out-Null
}

Passo "4/6 Instalando o Python e as bibliotecas (pode levar alguns minutos)"
uv sync
if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar as bibliotecas." }

Passo "5/6 Testando as ferramentas"
uv run pytest -q
if ($LASTEXITCODE -ne 0) { throw "Os testes falharam. Nao use o ambiente ate resolver." }

Passo "6/6 Baixando indices IPCA e IGP-M do Banco Central"
$desde = (Get-Date).AddYears(-3).ToString("yyyy-MM-dd")
uv run python -m escritorio indices --desde $desde
if ($LASTEXITCODE -ne 0) {
    Write-Host "Aviso: nao foi possivel baixar os indices agora. Repita depois com: uv run python -m escritorio indices" -ForegroundColor Yellow
}

Write-Host "`nInstalacao concluida em: $Destino" -ForegroundColor Green
Write-Host @"

Proximos passos:
  1. Abra o Claude Desktop, aba Code, e escolha a pasta: $Destino
  2. Confirme os plugins finance e operations quando o Claude pedir.
  3. Preencha o cofre (pasta conhecimento) com o responsavel: procure por [PREENCHER].
  4. Leia o README.md (secao 'Primeiro uso').
"@
