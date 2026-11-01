# Escritório Adm: Claude Code no administrativo

Ambiente pronto para a administradora do escritório usar o Claude Code em honorários, cobrança, conciliação bancária, contas a pagar e fechamento mensal.

**Princípio:** o Claude prepara; uma pessoa confere, aprova e executa. Nada de pagamentos, envio de e-mails ou notas fiscais pelo Claude.

## Instalação (Windows 10/11)

Pré-requisito: **Claude Desktop** instalado e com login em um plano **Team ou Enterprise** (sigilo profissional: confira os termos de retenção de dados).

Este repositório é **privado**. A conta do GitHub de quem vai instalar precisa ter sido convidada como colaboradora (permissão de leitura) por Paulo Tony.

Abra o **PowerShell** e rode, uma linha por vez:

```powershell
winget install --id Git.Git -e
```

Feche e abra o PowerShell, e então:

```powershell
git clone https://github.com/PauloTony87/escritorio-adm.git $HOME\escritorio-adm
```

Na primeira vez o Git abre uma janela do navegador para entrar no GitHub; entre com a conta convidada. Depois:

```powershell
& $HOME\escritorio-adm\instalar.ps1
```

Se o PowerShell bloquear o script, rode antes `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

O instalador, nesta ordem: instala Git e uv (se faltarem), prepara o Python e as bibliotecas, roda os testes, cria as pastas de trabalho e baixa IPCA e IGP-M do Banco Central. É seguro rodar de novo para atualizar.

## Primeiro uso

1. Claude Desktop, aba **Code**, escolha a pasta `escritorio-adm` (em seu usuário).
2. Aceite os plugins **finance** e **operations** quando o Claude pedir (já vêm declarados no projeto).
3. Com o responsável, preencha o cofre `conhecimento/`: procure por `[PREENCHER]`. Enquanto uma regra estiver em branco, o Claude avisa e não presume.
4. Teste com dados fictícios antes dos reais.

Plugins opcionais (instalar depois, com o responsável técnico): `claude-code-setup` (`/plugin install claude-code-setup@claude-plugins-official`) e Task Observer (veja abaixo).

## O que já vem pronto

| Skill | Para quê | Usa script? |
| --- | --- | --- |
| `/conciliacao-bancaria` | Extrato OFX/CSV × lançamentos, com pendências | sim |
| `/regua-cobranca` | Aging de honorários e rascunhos de cobrança | sim |
| `/reajuste-honorarios` | Reajuste por IPCA ou IGP-M com memória de cálculo | sim |
| `/honorarios-exito` | Êxito com piso e teto | sim |
| `/contas-a-pagar` | Agenda de pagamentos e validação de linha digitável | sim |
| `/contratos-honorarios` | Base estruturada de contratos | modelo inicial |
| `/reembolso-custas` | Custas por cliente e processo | modelo inicial |
| `/fechamento-mensal` | DRE gerencial, caixa e variações | modelo inicial |
| `/rentabilidade` | Resultado por cliente, área e sócio | modelo inicial |

"Modelo inicial" significa que a skill descreve o procedimento e o Claude usa as bibliotecas do projeto, sem script dedicado ainda. Os scripts passam a ser criados depois do piloto, quando o processo estiver estável.

Comandos diretos (sem o Claude), na pasta do projeto:

```powershell
uv run python -m escritorio exito --base 100000 --percentual 20 --teto 15000
uv run python -m escritorio reajuste --valor 1000 --indice IPCA --mes-reajuste 2026-03
uv run python -m escritorio aging --arquivo dados\receber\2026-10.xlsx
uv run python -m escritorio conciliar --extrato dados\extratos\banco.ofx --lancamentos dados\lancamentos.xlsx
uv run python -m escritorio boleto "<linha digitável>"
uv run python -m escritorio indices
```

## Estrutura

```
CLAUDE.md             regras gerais do assistente
.claude/settings.json permissões e plugins
.claude/skills/       skills do escritório
escritorio/           código Python (cálculos)
tests/                testes automáticos
conhecimento/         cofre Obsidian: regras e processos (sem dados de clientes)
contexto/             índices de reajuste
modelos/              modelos Word/Excel do escritório
dados/ e relatorios/  entradas e saídas (FORA do Git)
```

Abra a pasta `conhecimento/` no Obsidian como cofre, se a equipe quiser editar com links e busca.

## Segurança e sigilo

- `dados/` e `relatorios/` são ignorados pelo Git: **nunca** faça commit de arquivos de clientes. Este repositório contém apenas regras, modelos e código.
- Permissões em `.claude/settings.json` bloqueiam apagar arquivos, baixar da internet, `git push` e leitura de `.env`.
- Não conecte o Claude a Gmail com permissão de envio nem a sistemas bancários.
- Faça backup cifrado da pasta `dados/`.
- Registre o tratamento na política de privacidade e no inventário de dados (LGPD).

## Limitações conhecidas

- Os cálculos usam os índices do Banco Central (séries SGS 433 e 189). A janela de apuração do reajuste (12 meses terminando 1 mês antes) é o padrão do script: **confira a cláusula de cada contrato**.
- Boletos de arrecadação (48 dígitos) não são validados pelo script.
- Leitura de OFX foi testada em testes automáticos com dados fictícios; valide com o extrato real de cada banco.
- Linha digitável: validada com dados gerados nos testes; confirme com boletos reais do escritório.
- Em PDFs escaneados é preciso OCR (não incluído).

## Atualizar e testar

```powershell
& $HOME\escritorio-adm\instalar.ps1     # atualiza e testa
uv run pytest -q                        # só os testes
```

## Task Observer (opcional)

Meta-skill de comunidade que registra as correções da equipe e propõe melhorias de skills: [rebelytics/one-skill-to-rule-them-all](https://github.com/rebelytics/one-skill-to-rule-them-all). Leia o código antes de instalar e fixe a versão. O `CLAUDE.md` já manda carregá-lo no início das tarefas, se estiver instalado. Toda proposta passa pelo curador.

## Licença e uso

Material interno de apoio; adapte livremente. Não substitui a revisão de um contador nem de um profissional de proteção de dados.
