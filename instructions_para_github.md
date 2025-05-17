# Instrucciones para migrar el proyecto a GitHub

Sigue estos pasos para migrar este proyecto a tu cuenta de GitHub:

## 1. Preparación de los archivos locales

Los archivos principales del proyecto ya están listos para ser migrados:
- Se ha creado un README.md con documentación detallada
- Se ha añadido un archivo .gitignore para excluir archivos innecesarios
- Se ha incluido un archivo requirements_export.txt con las dependencias

## 2. Crear un repositorio en GitHub

1. Inicia sesión en tu cuenta de GitHub
2. Haz clic en el botón "+" en la esquina superior derecha y selecciona "New repository"
3. Nombra tu repositorio (por ejemplo, "task-manager")
4. Opcionalmente, añade una descripción
5. Elige la visibilidad del repositorio (público o privado)
6. No inicialices el repositorio con ningún archivo (sin README, .gitignore o licencia)
7. Haz clic en "Create repository"

## 3. Inicializar el repositorio local y subirlo a GitHub

Ejecuta los siguientes comandos en tu máquina local después de clonar o descargar los archivos del proyecto:

```bash
# Inicializar un repositorio Git en la carpeta del proyecto
git init

# Añadir todos los archivos al área de preparación
git add .

# Realizar el primer commit
git commit -m "Primer commit: Proyecto de gestión de tareas"

# Añadir el repositorio remoto (reemplaza USER con tu nombre de usuario y REPO con el nombre de tu repositorio)
git remote add origin https://github.com/USER/REPO.git

# Subir el código al repositorio
git push -u origin main
```

Nota: Si tu rama principal se llama "master" en lugar de "main", usa:
```bash
git push -u origin master
```

## 4. Despliegue del proyecto (opcional)

Para desplegar la aplicación, puedes utilizar plataformas como:
- Heroku
- Render
- Railway
- PythonAnywhere
- Vercel

Recuerda configurar las variables de entorno en la plataforma de despliegue:
- `DATABASE_URL`: La URL de conexión a tu base de datos PostgreSQL
- `SESSION_SECRET`: Una clave secreta para las sesiones
- `FLASK_ENV`: Establece como "production" para entornos de producción

## 5. Configuración de la base de datos (importante)

Asegúrate de no incluir en el repositorio público tu cadena de conexión a la base de datos de Neon Postgres. Esta información debe ser configurada como variable de entorno en tu entorno de desarrollo y producción.

La cadena de conexión actual:
```
postgresql://neondb_owner:npg_8ipwCteMGoA6@ep-super-fog-a4otjfcl-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
```

Debe ser almacenada como variable de entorno `DATABASE_URL` y no en el código fuente.

## 6. Desarrollo y mantenimiento continuo

Ahora puedes continuar desarrollando tu proyecto utilizando Git para el control de versiones:

```bash
# Para crear una nueva rama para desarrollar funcionalidades
git checkout -b nueva-funcionalidad

# Para enviar tus cambios
git add .
git commit -m "Descripción de los cambios"
git push origin nueva-funcionalidad

# Para fusionar cambios, crea un Pull Request en GitHub
```

¡Listo! Tu proyecto ahora está en GitHub y listo para seguir desarrollándose.