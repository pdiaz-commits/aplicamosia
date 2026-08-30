# AplicamosIA

Landing comercial de **AplicamosIA.es**, agencia de IA para pymes: transforma el negocio con agentes que venden, atienden y automatizan. Plantilla oscura tipo Hostinger; servicios más simples que una consultora AI-native grande.

Producción prevista: **Django en AWS Lightsail** (misma máquina que oca-i.net, vhost aparte). No Hostinger.

| Variante | Uso |
| --- | --- |
| Django | Desarrollo local y producción AWS |
| `deploy/` | nginx + systemd + env de producción |

Ver `DEPLOY-AWS.md`. No se publica el dominio hasta confirmación.

## Identidad (borrador)

- Marca: **AplicamosIA**
- Qué es: agencia de IA
- Promesa: sistemas que venden, atienden y automatizan
- Entrada: Diagnóstico · Piloto en 7 días · Sistema en marcha
- Servicios modulares
- Demostración visible en la propia página
- Bloque de privacidad y control humano
- Sin cifras, logos ni testimonios de clientes no demostrados
- Correo provisional de contacto: `merlin655040999@gmail.com`

## Django

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 manage.py test
python3 manage.py runserver
```

Abrir `http://127.0.0.1:8000/` (o el puerto libre que use `runserver`).

## Hostinger (solo local)

```bash
python3 -m http.server 8080 --directory hostinger/public
```

No subir a FTP, File Manager ni un dominio hasta confirmación explícita.
