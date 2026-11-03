# N7 Gestão – Guia de Deploy no Hosting com MySQL (InfinityFree)

## Visão geral do fluxo

1. **Código** enviado para a pasta pública do domínio (`public_html/`).
2. **Banco MySQL** criado no painel da InfinityFree.
3. **Variáveis de ambiente** configuradas (`DATABASE_URL`, `UPLOAD_DIR`, `SECRET_KEY`).
4. **Tabelas** criadas no MySQL (`db.create_all()` ou instalador).
5. **Instalador web** acessa `/install/` e configura empresa + administrador automaticamente.

---

## Passo 1 – Preparação do ambiente local

```bash
pip install -r requirements.txt
```

Edite o arquivo `.env` (ou variáveis de ambiente do servidor):

```env
SECRET_KEY=sua_chave_secreta_aqui
DATABASE_URL=mysql+pymysql://if0_43338625:SUA_SENHA@sql211.infinityfree.com:3306/if0_43338625
UPLOAD_DIR=/caminho/para/public_html/uploads
```

---

## Passo 2 – Criar as tabelas no MySQL

Com o `DATABASE_URL` apontando para o MySQL, execute:

```python
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    db.create_all()
```

---

## Passo 3 – Upload via FTP

1. Use FileZilla (ou cliente FTP) com:
   - Host: `ftpupload.net`
   - Usuário: `if0_43338625`
2. Faça upload da estrutura para a pasta `public_html` do domínio.

Estrutura mínima recomendada em `public_html`:

```
public_html/
├── wsgi.py
├── run.py
├── requirements.txt
├── .env
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models/
│   ├── services/
│   ├── routes/
│   ├── static/
│   └── templates/
├── assets/
└── docs/
```

---

## Passo 4 – Configurar WSGI

Crie/editar o arquivo `wsgi.py` na raiz:

```python
from app import create_app

application = create_app()
```

---

## Passo 5 – Configurar variáveis de ambiente no servidor

No Apache/Passenger (dependendo do painel):

```apache
PassengerEnabled On
PassengerAppRoot /caminho/public_html
PassengerPython /path/to/python
SetEnv PYTHONPATH /caminho/public_html
```

Ou via painel da InfinityFree (variáveis de ambiente).

---

## Passo 6 – Instalar o sistema (via navegador)

Com o código no ar e o banco configurado:

1. Acesse: `https://<seu-dominio>/install/`
2. Preencha os dados da **empresa** (razão social, CNPJ, endereço, contato, dados bancários/Pix).
3. Preencha os dados do **administrador inicial**.
4. Clique em **Instalar sistema**.
5. O sistema cria as tabelas, a empresa e o admin, e redireciona para `/auth/login`.

Alternativa manual (via script):

```bash
./setup.sh
```

---

## Passo 7 – Testar

1. Acesse `https://<seu-dominio>/auth/login`
2. Faça login com o admin criado no instalador.
3. Acesse `https://<seu-dominio>/dashboard`

---

## ⚠️ Observações importantes sobre o plano free

- O plano gratuito pode **não suportar WSGI/Python** da forma desejada (muitos hosts gratuitos só hospedam PHP).
- Se o InfinityFree não suportar Python, a solução comercial recomendada é uma **VPS**.
- O `DEBUG=True` **não deve** ser usado em produção (usar `wsgi.py`).

---

## 🔧 Comandos de manutenção no MySQL

```bash
# Backup
mysqldump -h sql211.infinityfree.com -u if0_43338625 -p if0_43338625 n7_gestao > backup.sql

# Restore
mysql -h sql211.infinityfree.com -u if0_43338625 -p if0_43338625 n7_gestao < backup.sql
```
