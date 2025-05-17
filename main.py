from app import app
import routes  # noqa: F401
import logging

if __name__ == "__main__":
    # Configurar registro para mostrar información de depuración
    logging.basicConfig(level=logging.DEBUG)
    print("===========================================")
    print("Iniciando aplicación en http://localhost:5000")
    print("Presiona CTRL+C para detener el servidor")
    print("===========================================")
    
    # Mostrar rutas disponibles
    print("\nRutas disponibles:")
    for rule in app.url_map.iter_rules():
        print(f"  http://localhost:5000{rule}")
    
    # Iniciar el servidor
    app.run(host="0.0.0.0", port=5000, debug=True)
