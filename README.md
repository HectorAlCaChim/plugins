# Extensión de API para Open edX 21 (Tutor)

Instala el paquete `custom-api` dentro de la imagen del LMS, para que los
cambios **no se pierdan** al reiniciar o recrear contenedores.

> Ejecutar todo como el usuario `tutor` (no root). El usuario debe estar en el grupo `docker`.

## 1. Validar el estado de la instancia

```bash
tutor config printvalue DOCKER_IMAGE_OPENEDX   # anotar: es el punto de retorno
tutor config printvalue LMS_HOST
tutor config printvalue ENABLE_HTTPS
groups                                         # debe incluir "docker"
```

## 2. Crear el Dockerfile

```bash
mkdir -p ~/custom-image && cd ~/custom-image
nano Dockerfile
```

Contenido (el `FROM` debe ser igual al valor de `DOCKER_IMAGE_OPENEDX` del paso 1):

```dockerfile
FROM docker.io/overhangio/openedx:21.0.8-indigo
RUN /openedx/venv/bin/pip install "custom-api @ https://github.com/HectorAlCaChim/plugins/archive/refs/heads/main.zip"
```

## 3. Validar acceso al repositorio

```bash
curl -sIL https://github.com/HectorAlCaChim/plugins/archive/refs/heads/main.zip | head -n 5
```

Debe responder `200`.

## 4. Construir y validar la imagen

```bash
docker build -t local/openedx-custom:1 .
docker run --rm local/openedx-custom:1 /openedx/venv/bin/pip show custom-api
```

`pip show` debe mostrar `Name: custom-api` y `Version: 0.1.0`.

## 5. Aplicar en Tutor

```bash
tutor config save --set DOCKER_IMAGE_OPENEDX=local/openedx-custom:1
tutor local start -d
```

> Reinicia LMS, CMS y workers (unos minutos de interrupción). No afecta datos.

## 6. Verificar

```bash
tutor local logs lms --tail 30
tutor local exec lms pip show custom-api
curl -i https://<LMS_HOST>/api/custom/v1/courses/
```

Esperado: sin `Traceback` y respuesta **401/403** (la ruta existe y pide
autenticación). Un **404** indica que el plugin no se registró.

## Actualizar el plugin

1. Hacer commit y push de los cambios al repositorio.
2. Reconstruir con un tag nuevo (`:2`, `:3`...):

```bash
cd ~/custom-image
docker build --no-cache -t local/openedx-custom:2 .
tutor config save --set DOCKER_IMAGE_OPENEDX=local/openedx-custom:2
tutor local restart lms cms lms-worker cms-worker
```

`--no-cache` es obligatorio mientras el Dockerfile apunte a `main`, porque
Docker reutilizaría la capa anterior y no traería el código nuevo.

## Rollback

```bash
tutor config save --set DOCKER_IMAGE_OPENEDX=docker.io/overhangio/openedx:21.0.8-indigo
tutor local start -d
```

(o el tag anterior, por ejemplo `local/openedx-custom:1`).

## Precauciones

- Nunca modificar código con `docker exec`: se pierde al recrear el contenedor.
- Si se ejecuta `tutor images build openedx` o se actualiza Indigo, revisar que
  `DOCKER_IMAGE_OPENEDX` siga apuntando a `local/openedx-custom:<tag>`.
- No publicar el `config.yml` de Tutor: contiene secretos.







# VALIDAR ESTADO DE LA INSTANCIA
1. tutor config printvalue DOCKER_IMAGE_OPENEDX
2. tutor config printvalue LMS_HOST
3. tutor config printvalue ENABLE_HTTPS
4. groups

# CREAR DOCKER FILE 
1. Se crear el directorio en donde esta el tutor
  mkdir -p ~/custom-image && cd ~/custom-image
2. Se genera el archivo en el directorio anterior
  nano Dockerfile
3. Se valida que se pueda conectar al repo
  curl -sIL https://github.com/HectorAlCaChim/plugins/archive/refs/heads/main.zip
4. Se genera el contenedor
  docker build -t local/openedx-custom:1 .
5. Se valida la configuracion del contenedor
  docker run --rm local/openedx-custom:1 /openedx/venv/bin/pip show custom-api
6. Se confirma la configuracion del contenedor con el api extendida a core open edx
  tutor config save --set DOCKER_IMAGE_OPENEDX=local/openedx-custom:1
7. Se reinicia el tutor para agregar el nuevo plugin
  tutor local start -d
8. Validat logs 
  tutor local logs lms --tail 30

# PARA PROXIMAS ACTULIZACIONES
1. Entrar al directorio del contenedor
  cd ~/custom-image
2. Aplicar y reconstruir contenedor
  docker build --no-cache -t local/openedx-custom:2 .
3. Guardar Configuraciones del core opend edx con el contenedor plugin
tutor config save --set DOCKER_IMAGE_OPENEDX=local/openedx-custom:2
4. Volver a aplicar
  tutor local restart lms cms lms-worker cms-worker