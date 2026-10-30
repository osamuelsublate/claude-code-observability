# claude-code-observability

Observabilidade do [Claude Code](https://code.claude.com/docs/en/overview) em quase tempo real, com OpenTelemetry e Grafana, rodando localmente em Docker Compose.

> **Status:** em construção. A stack, a Visão geral e o Raio-X da sessão já funcionam; as telas de custo, desempenho e produtividade ainda não foram criadas.

## Sobre

O Claude Code exporta telemetria nativamente via OpenTelemetry. Este projeto reúne a infraestrutura para receber esses dados, armazená-los e exibi-los em dashboards, respondendo a perguntas como:

- Quantos tokens estão sendo consumidos, e de que tipo?
- Quanto custa cada sessão ou modelo?
- Quanto tempo cada chamada à API e cada ferramenta levam?

## Arquitetura

```text
Claude Code → OTel Collector → Prometheus (métricas) → Grafana
                             → Loki (eventos)        →
~/.claude/projects → session-titles → Prometheus (nomes) →
```

| Serviço | Função |
| --- | --- |
| OTel Collector | Recebe os dados do Claude Code e os distribui |
| Prometheus | Armazena as métricas: tokens, custo e tempo ativo |
| Loki | Armazena os eventos: duração por chamada à API e por ferramenta |
| Grafana | Exibe os dashboards |
| session-titles | Lê o nome e a pasta de cada sessão local e os expõe ao Prometheus |
| Caddy | Atende <http://claude-grafana.localhost> na porta 80 |

## Como usar

```bash
cp .env.example .env
docker compose up -d
```

Troque a senha no `.env` antes de subir. O Grafana fica em <http://claude-grafana.localhost> e em <http://localhost:3300>, sem tela de login: quem acessa entra como administrador. Por isso, não publique as portas fora de `127.0.0.1`.

Para usar só `claude-grafana/` no navegador, adicione ao arquivo `hosts` do sistema (no Windows, `C:\Windows\System32\drivers\etc\hosts`, como administrador):

```text
127.0.0.1 claude-grafana
```

Depois, copie o bloco `env` de [`claude-code/settings.example.json`](claude-code/settings.example.json) para o `~/.claude/settings.json`. A telemetria passa a valer nas novas sessões.

### Nome da sessão e projeto

A telemetria só traz o ID da sessão. O nome que o Claude Code dá à conversa e a pasta do projeto ficam nos arquivos de sessão em `~/.claude/projects`, e o serviço `session-titles` lê só esses dois dados de cada arquivo e os expõe ao Prometheus. O conteúdo das conversas não é lido.

Com isso, o filtro de projeto e o nome das sessões funcionam sem nenhuma configuração extra. Se o Claude Code guardar as sessões em outra pasta, ajuste `CLAUDE_PROJECTS_DIR` no `.env`.

### Medir o custo de uma implementação

Abra uma sessão nova para cada implementação. O custo dela é o total daquela sessão (`session_id`).

## Dashboards

| Tela | Pergunta | Filtros |
| --- | --- | --- |
| Visão geral | O que está acontecendo agora? | Projeto e modelo |
| Raio-X da sessão | O que aconteceu nesta sessão e quanto custou cada mensagem? | Projeto e sessão |
| Comparação de sessões | Quais sessões custaram mais, em custo, tokens e tempo? | Projeto e sessões |

Na comparação, cada sessão vira uma barra nos mesmos gráficos. Como as sessões acontecem em horários diferentes, a tela compara totais, não a evolução no tempo.

Custo e tokens vêm dos eventos `api_request` no Loki, e não dos contadores do Prometheus. Cada sessão cria séries novas, e `increase()` ignora o primeiro valor de uma série, então sessões curtas apareceriam com custo zero.

O valor em USD é uma estimativa do Claude Code, não a fatura.

## Privacidade

Por padrão, o Claude Code não inclui o texto dos prompts na telemetria: o campo chega como `<REDACTED>`. Identificadores como o e-mail, o ID da sessão e o da conta são enviados, e o e-mail aparece como label nas métricas. Trate os dados coletados como privados e cuidado ao compartilhar capturas de tela. As portas são publicadas apenas em `127.0.0.1`.

## Referências

- [Documentação de monitoramento do Claude Code](https://code.claude.com/docs/en/monitoring-usage)

## Licença

Distribuído sob a [licença MIT](LICENSE).
