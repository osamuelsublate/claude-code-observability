# claude-code-observability

Observabilidade do [Claude Code](https://code.claude.com/docs/en/overview) em quase tempo real, com OpenTelemetry e Grafana, rodando localmente em Docker Compose.

> **Status:** em construção. A stack descrita abaixo ainda não foi adicionada a este repositório.

## Sobre

O Claude Code exporta telemetria nativamente via OpenTelemetry. Este projeto reúne a infraestrutura para receber esses dados, armazená-los e exibi-los em dashboards, respondendo a perguntas como:

- Quantos tokens estão sendo consumidos, e de que tipo?
- Quanto custa cada sessão ou modelo?
- Quanto tempo cada chamada à API e cada ferramenta levam?

## Arquitetura

```text
Claude Code → OTel Collector → Prometheus (métricas) → Grafana
                             → Loki (eventos)        →
```

| Serviço | Função |
| --- | --- |
| OTel Collector | Recebe os dados do Claude Code e os distribui |
| Prometheus | Armazena as métricas: tokens, custo e tempo ativo |
| Loki | Armazena os eventos: duração por chamada à API e por ferramenta |
| Grafana | Exibe os dashboards |

## Privacidade

Por padrão, o Claude Code não inclui prompts, respostas nem parâmetros de ferramentas na telemetria. Identificadores como o ID da sessão e o da conta são enviados, então trate os dados coletados como privados.

## Referências

- [Documentação de monitoramento do Claude Code](https://code.claude.com/docs/en/monitoring-usage)

## Licença

Distribuído sob a [licença MIT](LICENSE).
