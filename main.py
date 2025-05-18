from app import app
import routes  # noqa: F401
import logging
import os

if __name__ == "__main__":
    # Configurar registro para mostrar información de depuración
    logging.basicConfig(level=logging.DEBUG)
    port = int(os.environ.get("PORT", 5000))
    
    print("===========================================")
    print(f"Iniciando aplicación en http://localhost:{port}")
    print("Presiona CTRL+C para detener el servidor")
    print("===========================================")
    
    # Mostrar rutas disponibles
    print("\nRutas disponibles:")
    for rule in app.url_map.iter_rules():
        print(f"  http://localhost:{port}{rule}")
    
    # Iniciar el servidor
    app.run(host="0.0.0.0", port=port, debug=True)
    
if __name__ == "__main__":
    app.run(...)

