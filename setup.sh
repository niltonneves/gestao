#!/bin/bash
# ============================================================
# N7 Gestão – Script de Setup Automatizado
# Uso: ./setup.sh
# ============================================================
cd "$(dirname "$0")"

echo "========================================"
echo "  N7 Gestão – Setup"
echo "========================================"

echo "[1/4] Instalando dependências Python..."
pip3 install -r requirements.txt

echo "[2/4] Criando banco de dados (SQLite)..."
python3 - <<'EOF'
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Banco pronto.")
EOF

echo "[3/4] Configurando variáveis de ambiente..."
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Arquivo .env criado a partir do .env.example"
fi

echo "[4/4] Iniciando servidor..."
python3 run.py
