import os
from app import app
import routes  # noqa

def main():
    port = int(os.environ.get("PORT", 8080))
    public_url = os.environ.get("RAILWAY_PUBLIC_URL", f"http://localhost:{port}")

    print("\n" + "="*50)
    print("TASK MANAGER - Sistema de Gestión de Tareas")
    print("="*50)
    print(f"\n🌐 Servidor iniciado en: {public_url}")
    print("Para acceder a la aplicación, abre tu navegador en esa dirección")
    print("\nInformación de rutas disponibles:")

    rutas = [
        ("Página inicial", "/"),
        ("Iniciar sesión", "/login"),
        ("Registrarse", "/register"),
        ("Panel principal", "/dashboard"),
        ("Gestión de tareas", "/tasks"),
        ("Gestión de categorías", "/categories"),
        ("Analíticas", "/analytics"),
        ("Perfil de usuario", "/profile"),
    ]

    for nombre, ruta in rutas:
        print(f"  → {nombre}: {public_url}{ruta}")

    print("\nPresiona Ctrl+C para detener el servidor")
    print("="*50 + "\n")

    app.run(debug=True, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
