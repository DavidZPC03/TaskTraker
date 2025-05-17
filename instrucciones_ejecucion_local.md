# Instrucciones para Ejecutar la Aplicación Localmente

Para ejecutar correctamente esta aplicación en tu entorno local, sigue estos pasos:

## 1. Instalación de Dependencias

Primero, asegúrate de tener instaladas todas las dependencias necesarias:

```bash
pip install -r requirements_export.txt
```

## 2. Configuración de Variables de Entorno (Opcional)

Puedes configurar las siguientes variables de entorno, aunque tienen valores por defecto:

- `DATABASE_URL`: La URL de conexión a tu base de datos PostgreSQL
- `SESSION_SECRET`: Clave secreta para las sesiones
- `FLASK_ENV`: Entorno de ejecución (development/production)

## 3. Ejecución de la Aplicación

Ejecuta la aplicación utilizando el archivo `main.py`:

```bash
python main.py
```

NO ejecutes directamente `app.py`, ya que esto puede causar problemas de importación.

## 4. Acceso a la Aplicación

Una vez que la aplicación esté en ejecución, puedes acceder a ella a través de tu navegador en:

```
http://localhost:5000
```

## 5. Rutas Disponibles

Las siguientes rutas están disponibles en la aplicación:

- `/`: Página de inicio
- `/login`: Iniciar sesión
- `/register`: Registrarse
- `/logout`: Cerrar sesión
- `/dashboard`: Panel principal (requiere autenticación)
- `/tasks`: Lista de tareas (requiere autenticación)
- `/tasks/create`: Crear nueva tarea (requiere autenticación)
- `/tasks/<id>`: Ver detalles de una tarea específica (requiere autenticación)
- `/tasks/<id>/edit`: Editar una tarea (requiere autenticación)
- `/categories`: Lista de categorías (requiere autenticación)
- `/categories/create`: Crear nueva categoría (requiere autenticación)
- `/analytics`: Ver estadísticas y análisis (requiere autenticación)
- `/profile`: Ver perfil de usuario (requiere autenticación)

## 6. Posibles Problemas y Soluciones

### Error de ImportError debido a importaciones circulares

Si encuentras un error como:
```
ImportError: cannot import name 'X' from partially initialized module 'Y' (most likely due to a circular import)
```

Asegúrate de:
1. Ejecutar la aplicación con `python main.py` en lugar de `app.py`
2. No modificar el orden de las importaciones en los archivos principales

### Error de conexión a la base de datos

Si encuentras problemas de conexión a la base de datos, verifica:
1. Que la cadena de conexión sea correcta
2. Que la base de datos esté accesible desde tu red
3. Que tengas los permisos necesarios

### Error al crear tablas

Si las tablas no se crean automáticamente, puedes forzar su creación:

```python
from app import app, db
with app.app_context():
    db.create_all()
```

## 7. Desarrollo y Mejoras

Para continuar desarrollando la aplicación:

1. Sigue la estructura modular existente
2. Usa los patrones de programación establecidos (OOP, funcional, asíncrono)
3. Ejecuta `python main.py` para pruebas locales
4. Utiliza el sistema de logging para depuración