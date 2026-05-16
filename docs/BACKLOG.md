# Backlog - SafeGuard ID

## Legenda

- `P0`: Essencial para MVP.
- `P1`: Importante para primeira evolucao.
- `P2`: Melhorias futuras.

## Sprint 1 - MVP Backend

### US01 - Criar projeto Django

**Prioridade:** P0  
**Status:** Concluido

Como desenvolvedor, quero uma estrutura Django configurada para que a API possa ser executada localmente.

**Criterios de aceite:**

- Existe `manage.py`.
- Existe projeto `safeguard_id`.
- Existe app `transactions`.
- `python manage.py check` executa sem erros.

### US02 - Modelar Transaction

**Prioridade:** P0  
**Status:** Concluido

Como sistema, quero persistir transacoes para manter historico das autorizacoes.

**Criterios de aceite:**

- Model possui UUID como chave primaria.
- Model possui `amount`, `customer_id`, `ip_address`, `device_fingerprint`, `risk_score` e `status`.
- Status aceita `APPROVED` e `REJECTED`.
- Migration inicial existe.

### US03 - Criar endpoint de autorizacao

**Prioridade:** P0  
**Status:** Concluido

Como cliente da API, quero enviar uma transacao para receber uma decisao de autorizacao.

**Criterios de aceite:**

- Endpoint `POST /api/transactions/authorize/` existe.
- Payload valido cria uma transacao.
- Resposta contem status, score e razoes de risco.

### US04 - Validar payload de entrada

**Prioridade:** P0  
**Status:** Concluido

Como API, quero validar dados recebidos para evitar transacoes invalidas.

**Criterios de aceite:**

- `amount` deve ser maior que zero.
- `customer_id` nao pode ser vazio.
- `device_fingerprint` nao pode ser vazio.
- Campos calculados nao sao aceitos como entrada obrigatoria.

### US05 - Criar RiskEngine

**Prioridade:** P0  
**Status:** Concluido

Como sistema antifraude, quero avaliar uma transacao com regras de risco para aprovar ou rejeitar a operacao.

**Criterios de aceite:**

- `amount > 10000.00` rejeita a transacao.
- Fingerprint em blacklist rejeita a transacao.
- Transacao sem regra acionada e aprovada.
- Motor retorna `status`, `risk_score` e `reasons`.

### US06 - Configurar Swagger

**Prioridade:** P0  
**Status:** Concluido

Como desenvolvedor integrador, quero visualizar e testar a API via Swagger UI.

**Criterios de aceite:**

- Swagger acessivel em `/api/docs/`.
- Schema OpenAPI acessivel em `/api/schema/`.
- Endpoint de autorizacao aparece na documentacao.

### US07 - Preparar ambiente local

**Prioridade:** P0  
**Status:** Concluido

Como desenvolvedor, quero scripts de setup para abrir o projeto rapidamente.

**Criterios de aceite:**

- Existe `.env`.
- Existe `.env.example`.
- Existe script para preparar banco.
- Existe script para iniciar API.
- README contem instrucoes de uso.

## Sprint 2 - Qualidade e Consulta

### US08 - Criar testes automatizados do RiskEngine

**Prioridade:** P1  
**Status:** Concluido

Como desenvolvedor, quero testes unitarios do motor de risco para garantir que as regras nao quebrem em futuras alteracoes.

**Criterios de aceite:**

- Testa aprovacao de baixo risco.
- Testa rejeicao por valor alto.
- Testa rejeicao por device blacklist.
- Testa multiplas razoes de rejeicao.

### US09 - Criar testes automatizados da API

**Prioridade:** P1  
**Status:** Concluido

Como desenvolvedor, quero testes de endpoint para garantir que a API cria e retorna transacoes corretamente.

**Criterios de aceite:**

- Testa resposta `201` para payload valido.
- Testa `400` para amount invalido.
- Testa captura de IP.
- Testa persistencia da transacao.

### US10 - Listar transacoes

**Prioridade:** P1  
**Status:** Concluido

Como analista, quero listar transacoes para acompanhar decisoes realizadas.

**Criterios de aceite:**

- Endpoint `GET /api/transactions/` existe.
- Retorna lista paginada.
- Permite filtrar por `status`.
- Permite buscar por `customer_id`.

### US11 - Consultar transacao por ID

**Prioridade:** P1  
**Status:** Concluido

Como analista, quero consultar uma transacao especifica para auditar sua decisao.

**Criterios de aceite:**

- Endpoint `GET /api/transactions/{id}/` existe.
- Retorna `404` para UUID inexistente.
- Retorna todos os dados persistidos da transacao.

### US12 - Melhorar contrato de erro

**Prioridade:** P1  
**Status:** Concluido

Como integrador, quero respostas de erro padronizadas para tratar falhas com previsibilidade.

**Criterios de aceite:**

- Erros de validacao seguem formato unico.
- Resposta contem campo `code`.
- Resposta contem campo `message`.
- Resposta contem detalhes por campo quando aplicavel.

## Sprint 3 - Seguranca e Operacao

### US13 - Adicionar autenticacao por API key

**Prioridade:** P1  
**Status:** Concluido

Como dono da API, quero restringir acesso ao endpoint para evitar uso nao autorizado.

**Criterios de aceite:**

- Requisicoes sem chave retornam `401` ou `403`.
- Chave pode ser configurada por variavel de ambiente.
- Swagger documenta o header de autenticacao.

### US14 - Adicionar rate limiting

**Prioridade:** P2  
**Status:** Concluido

Como operador da plataforma, quero limitar volume de requisicoes para reduzir abuso.

**Criterios de aceite:**

- Limite configuravel por ambiente.
- Excesso de chamadas retorna `429`.
- Limite pode ser aplicado por IP.

### US15 - Persistir blacklist em banco

**Prioridade:** P2  
**Status:** Concluido

Como analista antifraude, quero gerenciar fingerprints bloqueadas sem alterar codigo.

**Criterios de aceite:**

- Existe model para blacklist.
- Existe admin para gerenciar fingerprints.
- RiskEngine consulta blacklist persistida.
- Fingerprints podem ser ativadas ou desativadas.

### US16 - Adicionar logs estruturados

**Prioridade:** P2  
**Status:** Concluido

Como operador, quero logs de decisoes para diagnosticar problemas e auditar comportamento.

**Criterios de aceite:**

- Cada autorizacao gera log com `transaction_id`.
- Log contem `customer_id`, `status`, `risk_score` e `risk_reasons`.
- Dados sensiveis nao sao expostos indevidamente.

### US17 - Docker Compose

**Prioridade:** P2  
**Status:** Concluido
Como desenvolvedor, quero subir API e banco com Docker Compose para padronizar ambiente.

**Criterios de aceite:**

- Existe `Dockerfile`.
- Existe `docker-compose.yml`.
- API sobe com PostgreSQL.
- Migrations podem ser aplicadas no container.

## Divida Tecnica

### DT01 - Fixar versoes reais das dependencias

**Prioridade:** P1  
**Status:** Concluido

Atualizar `requirements.txt` para refletir exatamente as versoes instaladas ou criar `requirements-dev.txt`.

### DT02 - Remover dependencia de pacotes globais

**Prioridade:** P1  
**Status:** Concluido

Instalar dependencias diretamente no `.venv` quando houver acesso ao `pip`.

### DT03 - Melhorar configuracao de ambientes

**Prioridade:** P2  
**Status:** Concluido

Separar configuracoes de desenvolvimento, teste e producao.

## Roadmap Resumido

| Fase | Entrega |
| --- | --- |
| MVP | Autorizar transacao, salvar decisao e documentar no Swagger |
| Qualidade | Testes automatizados, listagem e consulta |
| Seguranca | API key, rate limiting e logs |
| Evolucao Antifraude | Blacklist em banco e regras adicionais |
| Operacao | Docker Compose e configuracao por ambiente |
