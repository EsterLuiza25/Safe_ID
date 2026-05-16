from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings


def api_home(request):
    docs_url = reverse("swagger-ui")
    schema_url = reverse("schema")
    transaction_list_url = reverse("transaction-list")
    authorize_url = reverse("authorize-transaction")
    swagger_authorize_url = f"{docs_url}#/api/api_transactions_authorize_create"
    swagger_list_url = f"{docs_url}#/api/api_transactions_list"
    swagger_detail_url = f"{docs_url}#/api/api_transactions_retrieve"
    api_key = settings.SAFEGUARD_API_KEY

    html = f"""
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SafeGuard ID API</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #eef2f7;
      --surface: #ffffff;
      --surface-soft: #f8fafc;
      --text: #111827;
      --muted: #667085;
      --line: #d7deea;
      --brand: #0b5cad;
      --brand-soft: #e7f0fb;
      --green: #067647;
      --green-soft: #e7f8ef;
      --red: #b42318;
      --red-soft: #fff1f0;
      --amber: #946200;
      --amber-soft: #fff7df;
      --code: #0b1220;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, Segoe UI, Arial, Helvetica, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    main {{
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 34px 0 48px;
    }}
    .topbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      margin-bottom: 22px;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .mark {{
      display: grid;
      place-items: center;
      width: 44px;
      height: 44px;
      border: 1px solid #b9c8dd;
      background: var(--surface);
      color: var(--brand);
      font-weight: 900;
      font-size: 20px;
    }}
    h1 {{
      margin: 0;
      font-size: 30px;
      line-height: 1.15;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin: 3px 0 0;
      color: var(--muted);
      font-size: 15px;
    }}
    .status {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border: 1px solid #a9dec4;
      background: var(--green-soft);
      color: var(--green);
      font-weight: 800;
      white-space: nowrap;
    }}
    .dot {{
      width: 8px;
      height: 8px;
      background: var(--green);
      border-radius: 999px;
    }}
    .hero {{
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.65fr);
      gap: 18px;
      margin-bottom: 18px;
    }}
    .panel {{
      background: var(--surface);
      border: 1px solid var(--line);
      padding: 20px;
    }}
    .intro {{
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-height: 210px;
    }}
    .intro p {{
      max-width: 720px;
      margin: 0;
      color: var(--muted);
      font-size: 16px;
    }}
    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 24px;
    }}
    a {{
      color: var(--brand);
      text-decoration: none;
      font-weight: 800;
    }}
    a:hover {{ text-decoration: underline; }}
    .button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 40px;
      padding: 9px 14px;
      border: 1px solid var(--brand);
      background: var(--brand);
      color: #ffffff;
      font-weight: 800;
    }}
    .button.secondary {{
      background: var(--surface);
      color: var(--brand);
    }}
    .button:hover {{
      text-decoration: none;
      filter: brightness(0.97);
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 17px;
      letter-spacing: 0;
    }}
    .metrics {{
      display: grid;
      gap: 10px;
    }}
    .metric {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 11px 12px;
      border: 1px solid var(--line);
      background: var(--surface-soft);
    }}
    .metric span {{
      color: var(--muted);
      font-size: 14px;
    }}
    .metric strong {{
      font-size: 14px;
      text-align: right;
    }}
    .grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
      gap: 18px;
    }}
    .endpoint-list {{
      display: grid;
      gap: 10px;
    }}
    .endpoint {{
      display: grid;
      grid-template-columns: 74px minmax(0, 1fr) auto;
      align-items: center;
      gap: 12px;
      min-height: 56px;
      padding: 12px;
      border: 1px solid var(--line);
      background: var(--surface-soft);
    }}
    .endpoint:hover {{
      border-color: #9db8d8;
      background: #f4f8fd;
    }}
    .method {{
      display: inline-flex;
      justify-content: center;
      padding: 4px 8px;
      border: 1px solid;
      font-size: 12px;
      font-weight: 900;
      letter-spacing: 0;
    }}
    .method.post {{
      color: var(--amber);
      background: var(--amber-soft);
      border-color: #f0d485;
    }}
    .method.get {{
      color: var(--green);
      background: var(--green-soft);
      border-color: #a9dec4;
    }}
    code {{
      color: #24324a;
      font-family: Consolas, Monaco, monospace;
      font-size: 14px;
      word-break: break-word;
    }}
    .endpoint small {{
      color: var(--muted);
      font-weight: 800;
      white-space: nowrap;
    }}
    .rules {{
      display: grid;
      gap: 10px;
    }}
    .rule {{
      padding: 12px;
      border: 1px solid var(--line);
      background: var(--surface-soft);
      color: var(--muted);
    }}
    .rule strong {{
      color: var(--text);
    }}
    .approved {{
      color: var(--green);
      font-weight: 900;
    }}
    .rejected {{
      color: var(--red);
      font-weight: 900;
    }}
    pre {{
      margin: 0;
      overflow: auto;
      padding: 16px;
      border: 1px solid #22304a;
      background: var(--code);
      color: #e7eefc;
      font-family: Consolas, Monaco, monospace;
      font-size: 14px;
    }}
    .footnote {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 13px;
    }}
    @media (max-width: 840px) {{
      main {{ width: min(100% - 24px, 1120px); padding-top: 22px; }}
      .topbar {{ align-items: flex-start; flex-direction: column; }}
      .hero, .grid {{ grid-template-columns: 1fr; }}
      .intro {{ min-height: auto; }}
      .endpoint {{ grid-template-columns: 68px minmax(0, 1fr); }}
      .endpoint small {{ grid-column: 2; }}
    }}
  </style>
</head>
<body>
  <main>
    <div class="topbar">
      <div class="brand">
        <div class="mark">S</div>
        <div>
          <h1>SafeGuard ID API</h1>
          <p class="subtitle">Autorizacao de transacoes com motor de risco</p>
        </div>
      </div>
      <div class="status"><span class="dot"></span>API online</div>
    </div>

    <div class="hero">
      <section class="panel intro">
        <div>
          <h2>Console da API</h2>
          <p>Use esta pagina como indice do backend. A documentacao interativa esta no Swagger, e as rotas abaixo apontam para listagem, consulta e autorizacao de transacoes.</p>
        </div>
        <div class="actions">
          <a class="button" href="{docs_url}">Abrir Swagger</a>
          <a class="button secondary" href="{schema_url}">Ver OpenAPI</a>
          <a class="button secondary" href="{transaction_list_url}">Listar transacoes</a>
        </div>
      </section>

      <section class="panel">
        <h2>Resumo</h2>
        <div class="metrics">
          <div class="metric"><span>Framework</span><strong>Django REST</strong></div>
          <div class="metric"><span>Banco</span><strong>PostgreSQL</strong></div>
          <div class="metric"><span>Docs</span><strong>drf-spectacular</strong></div>
          <div class="metric"><span>Versao</span><strong>1.0.0</strong></div>
        </div>
      </section>
    </div>

    <div class="grid">
      <section class="panel">
        <h2>Endpoints</h2>
        <div class="endpoint-list">
          <a class="endpoint" href="{swagger_authorize_url}">
            <span class="method post">POST</span>
            <code>{authorize_url}</code>
            <small>Testar</small>
          </a>
          <a class="endpoint" href="{transaction_list_url}">
            <span class="method get">GET</span>
            <code>{transaction_list_url}</code>
            <small>Abrir</small>
          </a>
          <a class="endpoint" href="{swagger_detail_url}">
            <span class="method get">GET</span>
            <code>/api/transactions/&lt;uuid&gt;/</code>
            <small>Ver docs</small>
          </a>
          <a class="endpoint" href="{swagger_list_url}">
            <span class="method get">GET</span>
            <code>{transaction_list_url}?status=APPROVED&amp;customer_id=customer</code>
            <small>Filtro</small>
          </a>
        </div>
      </section>

      <section class="panel">
        <h2>Regras de Risco</h2>
        <div class="rules">
          <div class="rule"><strong>Valor alto</strong><br>amount &gt; 10000.00 retorna <span class="rejected">REJECTED</span>.</div>
          <div class="rule"><strong>Dispositivo bloqueado</strong><br>Fingerprint na blacklist retorna <span class="rejected">REJECTED</span>.</div>
          <div class="rule"><strong>Baixo risco</strong><br>Sem regra acionada retorna <span class="approved">APPROVED</span>.</div>
        </div>
      </section>

      <section class="panel">
        <h2>Autenticacao</h2>
        <div class="rules">
          <div class="rule"><strong>Header obrigatorio</strong><br><code>X-API-Key: {api_key}</code></div>
          <div class="rule"><strong>Rate limit</strong><br>Limite atual: <code>{settings.SAFEGUARD_RATE_LIMIT}</code> por IP.</div>
        </div>
      </section>

      <section class="panel">
        <h2>Payload de Autorizacao</h2>
        <pre>{{
  "amount": "250.00",
  "customer_id": "customer-123",
  "device_fingerprint": "ios-device-abc"
}}</pre>
      </section>

      <section class="panel">
        <h2>Rotas de Documentacao</h2>
        <div class="endpoint-list">
          <a class="endpoint" href="{docs_url}">
            <span class="method get">GET</span>
            <code>{docs_url}</code>
            <small>Swagger</small>
          </a>
          <a class="endpoint" href="{schema_url}">
            <span class="method get">GET</span>
            <code>{schema_url}</code>
            <small>Schema</small>
          </a>
        </div>
        <p class="footnote">A rota POST abre no Swagger porque navegadores fazem GET ao clicar em links.</p>
      </section>
    </div>
  </main>
</body>
</html>
"""
    return HttpResponse(html)
