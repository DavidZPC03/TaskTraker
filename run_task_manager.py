import os
import logging
from app import app  # 'app' ya está definido aquí y es accesible globalmente
import routes  # noqa: F401

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Función principal para iniciar la aplicación."""
    port = int(os.environ.get("PORT", 5000))

    print("\n" + "="*50)
    print("TASK MANAGER - Sistema de Gestión de Tareas")
    print("="*50)
    print(f"\nServidor iniciado en: http://localhost:{port}")
    print("Para acceder a la aplicación, abre tu navegador en esa dirección")
    print("\nInformación de rutas disponibles:")

    routes_info = [
        ("Página inicial", "/"),
        ("Iniciar sesión", "/login"),
        ("Registrarse", "/register"),
        ("Panel principal", "/dashboard"),
        ("Gestión de tareas", "/tasks"),
        ("Gestión de categorías", "/categories"),
        ("Analíticas", "/analytics"),
        ("Perfil de usuario", "/profile")
    ]

    for name, route in routes_info:
        print(f"  → {name}: http://localhost:{port}{route}")

    print("\nPresiona Ctrl+C para detener el servidor")
    print("="*50 + "\n")

    app.run(debug=True, host="0.0.0.0", port=port)  # puedes cambiar host según tu necesidad

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario. ¡Hasta pronto!")
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {e}")
        print(f"\n⚠️ Error: {e}")
        print("Consulta el archivo de log para más detalles.")
