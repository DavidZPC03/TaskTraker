# Sistema de Gestión de Tareas

Una aplicación web de gestión de tareas desarrollada con Flask que integra múltiples paradigmas de programación:

- **Programación Orientada a Objetos (OOP)**: Implementada en la estructura del modelo y la organización de clases.
- **Programación Funcional**: Utilizada para el procesamiento y filtrado de datos.
- **Programación Asíncrona**: Aplicada para procesamiento en segundo plano y operaciones no bloqueantes.

## Características

- Gestión completa de tareas con prioridades, fechas de vencimiento y categorías
- Panel de análisis con estadísticas y gráficos de productividad
- Filtrado y búsqueda avanzada de tareas
- Diseño responsivo con Bootstrap
- Autenticación de usuarios
- Interfaz intuitiva con tema oscuro

## Tecnologías Utilizadas

- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **Frontend**: Bootstrap, Chart.js, Feather Icons
- **Paradigmas**: OOP, Funcional, Asíncrono

## Instalación y Configuración

1. Clonar el repositorio:

```bash
git clone https://github.com/tu-usuario/task-manager.git
cd task-manager
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:

```bash
export FLASK_APP=main.py
export FLASK_ENV=development
export DATABASE_URL=tu_url_de_base_de_datos
export SESSION_SECRET=tu_clave_secreta
```

4. Iniciar la aplicación:

```bash
flask run
```

## Estructura del Proyecto

- `app.py`: Configuración principal de la aplicación Flask
- `models.py`: Definición de modelos y relaciones (Paradigma OOP)
- `routes.py`: Rutas y controladores de la aplicación
- `functional_utils.py`: Utilidades de procesamiento funcional (Paradigma Funcional)
- `async_processor.py`: Procesamiento asíncrono de tareas (Paradigma Asíncrono)
- `templates/`: Plantillas HTML
- `static/`: Archivos estáticos (CSS, JavaScript, imágenes)

## Paradigmas de Programación Implementados

### Orientación a Objetos

- Jerarquía de clases con herencia (TimeStampMixin, SoftDeleteMixin)
- Encapsulamiento en modelos con propiedades y métodos
- Polimorfismo en la gestión de diferentes tipos de entidades

### Programación Funcional

- Uso de funciones puras para transformaciones de datos
- Implementación de funciones de orden superior (map, filter, reduce)
- Composición de funciones para operaciones complejas

### Programación Asíncrona/Concurrente

- Procesamiento asíncrono para tareas no bloqueantes
- Operaciones concurrentes para mejora de rendimiento
- Manejo de eventos asíncronos
