#!/bin/bash
# Inicializador N7 Gestão – Linux
cd "$(dirname "$0")"
export FLASK_APP=run.py
export FLASK_DEBUG=1
python3 run.py
