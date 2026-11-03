# N7 Gestão – Gestão Inteligente de Serviços

Sistema de gestão comercial para empresas e profissionais prestadores de serviços,
focado em orçamentos, ordens de serviço, atendimento e controle financeiro.

**N7 Gestão – Uma solução N7 Info.**

## Stack

- Backend: Python 3 + Flask
- Banco de dados: SQLite (preparado para PostgreSQL)
- ORM: SQLAlchemy (Flask-SQLAlchemy) + Flask-Migrate (Alembic)
- Autenticação: Flask-Login (sessões, hash de senha)
- PDF: ReportLab
- Planilhas: OpenPyXL
- Frontend: HTML5, CSS3, JavaScript, Bootstrap 5

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env   # ajuste SECRET_KEY e DATABASE_URL se necessário
# Exemplo para MySQL:
# DATABASE_URL=mysql+pymysql://if0_43338625:SUA_SENHA@sql211.infinityfree.com:3306/if0_43338625

flask --app run db init     # apenas na primeira instalação
flask --app run db migrate -m "init"
flask --app run db upgrade

flask --app run
```

Acesse `http://localhost:5000/auth/login`.

Na primeira instalação, utilize o primeiro acesso em:

```
http://localhost:5000/auth/primeiro-acesso
```

## Inicialização rápida

Linux:

```bash
./start.sh
```

Windows:

```bat
start.bat
```

## Deploy com MySQL (ex.: InfinityFree)

1. Instale as dependências: `pip install -r requirements.txt` (inclui `pymysql`).
2. Configure as variáveis no `.env`:

```
SECRET_KEY=sua_chave_secreta
DATABASE_URL=mysql+pymysql://usuario:senha@host:3306/banco
UPLOAD_DIR=/caminho/para/uploads
```

3. Suba o código via FTP para a pasta pública do domínio.
4. Use `wsgi.py` como entrada WSGI:

```python
from app import create_app

application = create_app()
```

5. Atualize o banco (via scripts ou `db.create_all()` / migrations).

## Estrutura

```
app/
  config.py
  extensions.py
  models/        # Entidades de domínio
  services/      # Regras de negócio e permissões
  routes/        # Endpoints HTTP
  templates/     # Jinja2
  static/        # CSS, JS, imagens
migrations/
tests/
```

## Módulos

- Dashboard
- Clientes
- Produtos e Serviços
- Orçamentos
- Ordens de Serviço
- Financeiro
- Relatórios
- Configurações
- Administração

## Testes

```bash
python -m pytest tests/
```

## Backup

```bash
cp instance/n7_gestao.db backups/n7_gestao_backup_YYYYMMDD.db
```
