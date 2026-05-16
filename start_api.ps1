$ErrorActionPreference = "Stop"

Write-Host "Iniciando SafeGuard ID em http://127.0.0.1:8000/"
Write-Host "Swagger UI: http://127.0.0.1:8000/api/docs/"
Write-Host "Endpoint:    http://127.0.0.1:8000/api/transactions/authorize/"

& ".\.venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000
