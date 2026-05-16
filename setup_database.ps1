$ErrorActionPreference = "Stop"

function Read-DotEnvValue($name, $fallback) {
    if (Test-Path ".env") {
        $line = Get-Content ".env" | Where-Object { $_ -match "^$name=" } | Select-Object -First 1
        if ($line) {
            return ($line -split "=", 2)[1].Trim().Trim('"').Trim("'")
        }
    }

    return $fallback
}

$dbName = Read-DotEnvValue "POSTGRES_DB" "safeguard_id"
$dbUser = Read-DotEnvValue "POSTGRES_USER" "postgres"
$dbPassword = Read-DotEnvValue "POSTGRES_PASSWORD" "postgres"
$dbHost = Read-DotEnvValue "POSTGRES_HOST" "localhost"
$dbPort = Read-DotEnvValue "POSTGRES_PORT" "5432"
$psql = "C:\Program Files\PostgreSQL\18\bin\psql.exe"

if (-not (Test-Path $psql)) {
    $psql = "psql"
}

$env:PGPASSWORD = $dbPassword

Write-Host "Verificando banco PostgreSQL '$dbName'..."
$exists = & $psql -h $dbHost -p $dbPort -U $dbUser -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$dbName';"

if ($LASTEXITCODE -ne 0) {
    throw "Nao foi possivel conectar ao PostgreSQL em $dbHost`:$dbPort com o usuario '$dbUser'. Confira POSTGRES_PASSWORD e POSTGRES_PORT no arquivo .env."
}

if ([string]::IsNullOrWhiteSpace($exists) -or $exists.Trim() -ne "1") {
    Write-Host "Criando banco '$dbName'..."
    & $psql -h $dbHost -p $dbPort -U $dbUser -d postgres -c "CREATE DATABASE $dbName;"
}
else {
    Write-Host "Banco '$dbName' ja existe."
}

Write-Host "Aplicando migrations..."
& ".\.venv\Scripts\python.exe" manage.py migrate

Write-Host "Setup concluido."
