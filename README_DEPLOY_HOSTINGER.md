# Deploy na VPS Hostinger - SIAFI Eventos Django

## 1. Preparar servidor

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip postgresql postgresql-contrib nginx git
```

## 2. Criar banco PostgreSQL

```bash
sudo -u postgres psql
CREATE DATABASE siafi_eventos_db;
CREATE USER siafi_eventos_user WITH PASSWORD 'TROQUE_ESTA_SENHA';
ALTER ROLE siafi_eventos_user SET client_encoding TO 'utf8';
ALTER ROLE siafi_eventos_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE siafi_eventos_user SET timezone TO 'America/Recife';
GRANT ALL PRIVILEGES ON DATABASE siafi_eventos_db TO siafi_eventos_user;
\q
```

## 3. Enviar projeto

Copie o projeto para:

```bash
/var/www/siafi_eventos_django
```

Depois:

```bash
cd /var/www/siafi_eventos_django
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
nano .env
```

Preencha `SECRET_KEY`, domínio, IP da VPS e dados do PostgreSQL.

Para gerar uma SECRET_KEY:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 4. Migrar e coletar estáticos

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py importar_tabela_eventos data/TABELE_DE_EVENTOS_2025.txt --limpar
python manage.py carregar_situacoes_seed
python manage.py createsuperuser
python manage.py check --deploy
```

## 5. Gunicorn

```bash
sudo cp deploy/gunicorn.service.example /etc/systemd/system/siafi_eventos.service
sudo nano /etc/systemd/system/siafi_eventos.service
sudo systemctl daemon-reload
sudo systemctl enable siafi_eventos
sudo systemctl start siafi_eventos
sudo systemctl status siafi_eventos
```

Ajuste `User`, `WorkingDirectory`, `EnvironmentFile` e `ExecStart` se o caminho real for diferente.

## 6. Nginx

```bash
sudo cp deploy/nginx.conf.example /etc/nginx/sites-available/siafi_eventos
sudo nano /etc/nginx/sites-available/siafi_eventos
sudo ln -s /etc/nginx/sites-available/siafi_eventos /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 7. Domínio e SSL

No registro.br, aponte o domínio para o IP da VPS:

- `A` para `@` apontando para o IP da VPS
- `A` para `www` apontando para o IP da VPS

Depois instale SSL:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d seudominio.com.br -d www.seudominio.com.br
```

## Observações importantes

- Nunca suba `.env`, `venv`, `db.sqlite3`, `staticfiles` ou `media` para o Git.
- Troque a `SECRET_KEY` e a senha do banco antes de produzir.
- Primeiro teste pelo IP da VPS. Aponte o domínio só depois que o Django responder corretamente via Nginx/Gunicorn.
