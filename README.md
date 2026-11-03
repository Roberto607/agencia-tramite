# LB&A Consulter

## Desarrollo

Requisitos: Docker Desktop con Compose y Node.js.

1. Copia `.env.example` a `.env` y cambia las contraseñas/clave para tu entorno.
2. Inicia Django y PostgreSQL:

   ```powershell
   docker compose up --build
   ```

3. En otra terminal, inicia React:

   ```powershell
   npm install
   npm run dev
   ```

La API queda en `http://localhost:8000`; el frontend Vite en `http://localhost:5173`.

- `GET /api/health/`: estado de Django y PostgreSQL.
- `POST /api/applications/`: crea una solicitud con campos multipart y cualquier cantidad de archivos bajo la clave repetida `documents`.

Los registros viven en el volumen `postgres_data` y los adjuntos en `uploaded_media`. `docker compose down` conserva ambos; `docker compose down -v` elimina también los datos persistidos.

## Pruebas

```powershell
docker compose exec backend python manage.py test
```

La configuración es para desarrollo local. Antes de publicar, configura secretos reales, `DEBUG=0`, hosts/CORS del dominio y almacenamiento duradero de archivos.

## Administrador inicial en Render

El contenedor crea el administrador inicial al arrancar si configuras juntas estas variables privadas en el servicio web:

- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_PASSWORD`

Después de confirmar que puedes iniciar sesión en `/admin/`, elimina estas tres variables de Render. El usuario creado permanece en PostgreSQL; el comando no cambia la contraseña ni los permisos de un superusuario ya existente.
