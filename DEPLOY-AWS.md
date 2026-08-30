# AplicamosIA en AWS Lightsail (Django)

Misma máquina que `oca-i.net`. **No sustituye** ese sitio. Puerto interno propio: `8027`.

| Campo | Valor |
| --- | --- |
| Servidor | Lightsail `15.224.60.79` (`ssh lightsail`) |
| Ruta | `/var/www/aplicamosia.es` |
| Dominio | `aplicamosia.es` + `www` |
| Proceso | Gunicorn → `127.0.0.1:8047` |
| Público | solo nginx 80/443 |

No usar Hostinger para esta web.

## Cloudflare (origen AWS)

| Tipo | Nombre | Contenido | Proxy |
| --- | --- | --- | --- |
| A | `@` | `15.224.60.79` | Naranja |
| A | `www` | `15.224.60.79` | Naranja |

SSL/TLS: **Full**. Correo: Email Routing → `hola@aplicamosia.es` → Merlin.

## Despliegue

Hace falta repo en Git y confirmación explícita antes de abrir el dominio al público. Luego, en el servidor:

```bash
sudo mkdir -p /var/www/aplicamosia.es
sudo chown -R ubuntu:ubuntu /var/www/aplicamosia.es
# clonar el repo en /var/www/aplicamosia.es
cd /var/www/aplicamosia.es
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp deploy/env.production.example .env
# editar .env
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py check --deploy
sudo cp deploy/systemd/aplicamosia.service /etc/systemd/system/
sudo cp deploy/nginx/aplicamosia.es.conf /etc/nginx/sites-available/aplicamosia.es
sudo ln -sf /etc/nginx/sites-available/aplicamosia.es /etc/nginx/sites-enabled/
sudo systemctl daemon-reload
sudo systemctl enable --now aplicamosia
sudo nginx -t && sudo systemctl reload nginx
```
