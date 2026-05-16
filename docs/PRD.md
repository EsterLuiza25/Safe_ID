# PRD - SafeGuard ID

## 1. Visao Geral

O SafeGuard ID e uma API backend para autorizacao de transacoes com analise basica de risco. O sistema recebe dados de uma transacao, captura automaticamente informacoes da requisicao HTTP, calcula um score de risco e decide se a transacao deve ser aprovada ou rejeitada.

## 2. Problema

Sistemas que processam pagamentos, pedidos ou operacoes sensiveis precisam identificar transacoes suspeitas antes da conclusao. Sem um mecanismo de avaliacao, operacoes com alto valor ou dispositivos conhecidos por comportamento fraudulento podem ser aprovadas sem controle.

## 3. Objetivo

Construir uma API documentada, persistente e extensivel para:

- Receber pedidos de autorizacao de transacao.
- Capturar IP e User-Agent automaticamente.
- Avaliar risco com regras de negocio.
- Persistir a decisao no PostgreSQL.
- Expor documentacao interativa via Swagger UI.

## 4. Publico-Alvo

- Times backend que precisam integrar uma camada antifraude simples.
- Aplicacoes de checkout, fintechs, marketplaces ou sistemas internos.
- Avaliadores tecnicos que precisam validar arquitetura com Django, DRF, PostgreSQL e Swagger.

## 5. Escopo da Versao 1

### Incluido

- Projeto Django com DRF.
- Model `Transaction`.
- Endpoint de autorizacao de transacoes.
- Captura automatica de IP.
- Captura automatica de User-Agent.
- Motor de risco `RiskEngine`.
- Regra de rejeicao por valor maior que `10000.00`.
- Regra de rejeicao por `device_fingerprint` em blacklist simulada.
- Persistencia em PostgreSQL.
- Swagger UI para testar a API.
- Scripts para preparar banco e iniciar API localmente.

### Fora de Escopo Inicial

- Autenticacao por API key ou JWT.
- Dashboard administrativo customizado.
- Integracao com gateways de pagamento reais.
- Machine learning antifraude.
- Blacklist persistida em banco.
- Analise geolocalizada por IP.
- Rate limiting.
- Logs estruturados e observabilidade avancada.

## 6. Requisitos Funcionais

### RF01 - Autorizar Transacao

O sistema deve receber uma requisicao `POST` com:

- `amount`
- `customer_id`
- `device_fingerprint`

O sistema deve retornar:

- `id`
- `amount`
- `customer_id`
- `ip_address`
- `device_fingerprint`
- `risk_score`
- `status`
- `risk_reasons`
- `created_at`

### RF02 - Capturar IP Automaticamente

O sistema deve capturar o IP da requisicao usando:

- `HTTP_X_FORWARDED_FOR`, quando disponivel.
- `REMOTE_ADDR`, como fallback.

### RF03 - Capturar User-Agent Automaticamente

O sistema deve capturar o `HTTP_USER_AGENT` da requisicao para uso pelo motor de risco.

### RF04 - Calcular Risco

O sistema deve rejeitar transacoes quando:

- `amount > 10000.00`
- `device_fingerprint` estiver na blacklist simulada.

### RF05 - Persistir Transacao

Toda tentativa de autorizacao valida deve ser persistida no banco PostgreSQL com a decisao tomada.

### RF06 - Documentar API

O sistema deve disponibilizar documentacao interativa em:

```text
/api/docs/
```

## 7. Requisitos Nao Funcionais

- O backend deve usar Django e Django REST Framework.
- O banco principal deve ser PostgreSQL.
- A API deve ter schema OpenAPI gerado automaticamente.
- A estrutura deve separar regra de negocio da camada de view.
- O endpoint deve validar dados de entrada antes da persistencia.
- O projeto deve ser executavel localmente por scripts.

## 8. Contrato da API

### Autorizar Transacao

```http
POST /api/transactions/authorize/
Content-Type: application/json
```

Payload aprovado:

```json
{
  "amount": "250.00",
  "customer_id": "customer-123",
  "device_fingerprint": "ios-device-abc"
}
```

Resposta esperada:

```json
{
  "id": "uuid",
  "amount": "250.00",
  "customer_id": "customer-123",
  "ip_address": "127.0.0.1",
  "device_fingerprint": "ios-device-abc",
  "risk_score": 10,
  "status": "APPROVED",
  "created_at": "2026-05-14T17:58:03.344354-03:00",
  "risk_reasons": ["LOW_RISK"]
}
```

Payload rejeitado:

```json
{
  "amount": "15000.00",
  "customer_id": "customer-999",
  "device_fingerprint": "blocked-fingerprint-demo"
}
```

Resposta esperada:

```json
{
  "id": "uuid",
  "amount": "15000.00",
  "customer_id": "customer-999",
  "ip_address": "127.0.0.1",
  "device_fingerprint": "blocked-fingerprint-demo",
  "risk_score": 100,
  "status": "REJECTED",
  "created_at": "2026-05-14T17:58:57.316342-03:00",
  "risk_reasons": ["AMOUNT_ABOVE_LIMIT", "BLACKLISTED_DEVICE"]
}
```

## 9. Regras de Negocio

| Regra | Condicao | Resultado | Score |
| --- | --- | --- | --- |
| Valor alto | `amount > 10000.00` | `REJECTED` | `90` |
| Dispositivo bloqueado | Fingerprint na blacklist | `REJECTED` | `100` |
| Baixo risco | Nenhuma regra acionada | `APPROVED` | `10` |

Quando mais de uma regra de rejeicao for acionada, a transacao deve retornar todas as razoes aplicaveis.

## 10. Metricas de Sucesso

- API sobe localmente sem erro.
- Swagger UI exibe o endpoint de autorizacao.
- Transacao valida de baixo risco retorna `APPROVED`.
- Transacao acima de `10000.00` retorna `REJECTED`.
- Fingerprint bloqueada retorna `REJECTED`.
- Transacoes avaliadas sao salvas no PostgreSQL.

## 11. Riscos

- Senha local do PostgreSQL pode variar entre ambientes.
- Dependencias podem nao instalar sem internet.
- Regras simuladas sao simples e nao representam antifraude real de producao.
- Uso de pacotes globais no ambiente local pode diferir do `requirements.txt`.

## 12. Proximas Evolucoes

- Autenticacao da API.
- Endpoint para consultar transacoes.
- Blacklist gerenciada no banco.
- Logs estruturados.
- Testes automatizados.
- Rate limiting.
- Docker Compose para app e PostgreSQL.
- Regras adicionais por IP, cliente e frequencia transacional.
