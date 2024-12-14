from pymongo import MongoClient
import json
from bson.objectid import ObjectId
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import os
import math

# Conexión noSQL para comentarios
try:
    client = MongoClient("mongodb+srv://jmendieta:1234@perfumes.rwvdn.mongodb.net/")
    db = client["perfumes"]
    comments_collection = db["comentarios"]
    print("Conexión exitosa a MongoDB")
except Exception as e:
    print("Error al conectar a MongoDB:", e)

# Conexión MySQL para productos, usuarios y sucursales
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="perfumes"
    )

# Función para calcular la distancia usando la fórmula de Haversine
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radio de la Tierra en kilómetros
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Función para ver las sucursales más cercanas
def sucursales_cercanas(usuario):
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)

        # Obtener la ubicación del cliente actual
        lat_cliente = usuario["latitud"]
        lon_cliente = usuario["longitud"]

        # Obtener las sucursales desde la base de datos
        consulta = "SELECT id_sucursal, nombre, latitud, longitud FROM sucursales"
        cursor.execute(consulta)
        sucursales = cursor.fetchall()

        # Calcular la distancia a cada sucursal
        for sucursal in sucursales:
            distancia = calcular_distancia(lat_cliente, lon_cliente, sucursal["latitud"], sucursal["longitud"])
            sucursal["distancia"] = distancia

        # Ordenar las sucursales por distancia
        sucursales_ordenadas = sorted(sucursales, key=lambda x: x["distancia"])

        # Mostrar las sucursales ordenadas
        print("\n=== Sucursales más cercanas ===")
        for sucursal in sucursales_ordenadas:
            print(f"Sucursal: {sucursal['nombre']} (ID: {sucursal['id_sucursal']}) - Distancia: {sucursal['distancia']:.2f} km")

        input("\nPresione Enter para volver al menú principal.")

    except Error as e:
        print("Error al obtener sucursales:", e)

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
# Definimos la función iniciar_sesion() que no recibe parámetros
def iniciar_sesion():
    try:
        # Intentamos establecer una conexión con la base de datos
        conexion = conectar()
        # Creamos un cursor con la opción 'dictionary=True' para obtener resultados como diccionarios
        cursor = conexion.cursor(dictionary=True)

        # Pedimos al usuario que ingrese su correo electrónico
        correo = input("Ingrese su correo electrónico: ")
        # Pedimos al usuario que ingrese su contraseña
        contraseña = input("Ingrese su contraseña: ")

        # Definimos la consulta SQL que se ejecutará para verificar si el correo y contraseña son correctos
        consulta = """
        SELECT * FROM clientes WHERE correo_electronico = %s AND contraseña = %s
        """
        # Definimos los valores a pasar a la consulta
        valores = (correo, contraseña)

        # Ejecutamos la consulta con los valores proporcionados
        cursor.execute(consulta, valores)
        # Obtenemos un solo registro que coincida con los datos de la consulta
        usuario = cursor.fetchone()

        # Si se encuentra un usuario que coincida con los datos, mostramos un mensaje de bienvenida
        if usuario:
            print(f"Bienvenido, {usuario['nombre']}!")
            return usuario
        else:
            # Si no se encuentra el usuario, mostramos un mensaje de error
            print("Correo o contraseña incorrectos.")
            return None

    except Error as e:
        # Si ocurre un error, lo capturamos y mostramos el mensaje correspondiente
        print("Error al iniciar sesión:", e)

    finally:
        # En el bloque 'finally' nos aseguramos de cerrar la conexión y el cursor
        if conexion.is_connected():
            cursor.close()
            conexion.close()

# Definimos la función registrar_usuario() que no recibe parámetros
def registrar_usuario():
    try:
        # Intentamos establecer una conexión con la base de datos
        conexion = conectar()
        # Creamos un cursor para ejecutar comandos SQL
        cursor = conexion.cursor()

        # Pedimos al usuario que ingrese su nombre y lo guardamos en una variable
        nombre = input("Ingrese su nombre: ")
        # Pedimos al usuario que ingrese su correo electrónico
        correo = input("Ingrese su correo electrónico: ")
        # Pedimos al usuario que ingrese su dirección
        direccion = input("Ingrese su dirección: ")
        # Pedimos la latitud, convertimos la entrada a un número flotante y la guardamos
        latitud = float(input("Ingrese la latitud: "))
        # Pedimos la longitud, también la convertimos a un número flotante
        longitud = float(input("Ingrese la longitud: "))
        # Pedimos al usuario que ingrese su contraseña
        contraseña = input("Ingrese su contraseña: ")

        # Definimos la consulta SQL que se ejecutará para insertar los datos del usuario
        consulta = """
        INSERT INTO clientes (nombre, correo_electronico, direccion, latitud, longitud, contraseña)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        # Definimos los valores que serán insertados en la consulta
        valores = (nombre, correo, direccion, latitud, longitud, contraseña)

        # Ejecutamos la consulta con los valores proporcionados
        cursor.execute(consulta, valores)
        # Confirmamos la transacción para que los cambios se apliquen en la base de datos
        conexion.commit()
        # Imprimimos un mensaje de éxito
        print("Usuario registrado con éxito.")

    except Error as e:
        # Si ocurre un error, se captura y se imprime el mensaje de error
        print("Error al registrar el usuario:", e)

    finally:
        # En el bloque 'finally' nos aseguramos de cerrar la conexión y el cursor, sin importar si hubo error o no
        if conexion.is_connected():
            cursor.close()
            conexion.close()

# Función para listar productos
def listar_productos():
    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)

        consulta = "SELECT id_perfume, nombre, precio, stock FROM perfumes"
        cursor.execute(consulta)
        productos = cursor.fetchall()

        print("Productos disponibles:")
        for producto in productos:
            print(f"{producto['id_perfume']}. {producto['nombre']} - ${producto['precio']} (Stock: {producto['stock']})")

        return productos

    except Error as e:
        print("Error al listar productos:", e)
        return []

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

# Función para realizar una compra
def realizar_compra(usuario):
    try:
        conexion = conectar()
        cursor = conexion.cursor()

        carrito = []
        total = 0

        while True:
            productos = listar_productos()
            if not productos:
                return

            id_producto = int(input("Ingrese el ID del producto que desea comprar: "))
            cantidad = int(input("Ingrese la cantidad que desea comprar: "))

            consulta = "SELECT nombre, precio, stock FROM perfumes WHERE id_perfume = %s"
            cursor.execute(consulta, (id_producto,))
            producto = cursor.fetchone()

            if producto and cantidad <= producto[2]:  # Validar stock
                carrito.append((id_producto, producto[0], cantidad, producto[1] * cantidad))
                total += producto[1] * cantidad
                print(f"Producto {producto[0]} agregado al carrito.")
            else:
                print("Cantidad no disponible en el stock.")

            agregar_mas = input("¿Desea agregar otro producto? (s/n): ").strip().lower()
            if agregar_mas != 's':
                break

        # Mostrar resumen del carrito
        print("\nResumen de su compra:")
        for item in carrito:
            print(f"Producto: {item[1]}, Cantidad: {item[2]}, Subtotal: ${item[3]:.2f}")
        print(f"Total a pagar: ${total:.2f}")

        # Confirmar compra
        confirmar = input("¿Desea confirmar su compra? (s/n): ").strip().lower()
        if confirmar == 's':
            for item in carrito:
                consulta_compra = "CALL registro_compra(%s, %s, %s)"
                valores = (usuario['id_cliente'], item[0], item[2])
                cursor.execute(consulta_compra, valores)

            conexion.commit()
            print("Compra realizada con éxito.")
        else:
            print("Compra cancelada. Regresando al menú.")

    except Error as e:
        print("Error al realizar la compra:", e)

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

# Función para gestionar comentarios
def gestionar_comentarios(usuario):
    print("\n=== Gestión de comentarios ===")
    while True:
        print("1. Comentar producto")
        print("2. Ver comentarios de un producto")
        print("3. Buscar comentarios")
        print("4. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            clienteID = input("Ingrese su nombre: ")
            productoID = input("Ingrese el ID del producto: ")
            calificacion = input("Ingrese la calificación (1-5): ")
            comentario = input("Ingrese su comentario: ")

            # Crear documento para insertar en MongoDB
            comment = {
                "customer_name": clienteID,
                "productid": productoID,
                "comment": comentario,
                "rating": calificacion
            }

            # Insertar comentario
            comments_collection.insert_one(comment)
            print("Comentario registrado con éxito.")

        elif opcion == "2":
            codigoProducto = input("Ingrese el ID del producto para ver comentarios: ")
            comments = comments_collection.find({"productid": codigoProducto})

            # Mostrar los resultados
            for comentario in comments:
                json_format = json.dumps(comentario, indent=4, default=str)
                print(json_format)

        elif opcion == "3":
            textoComentario = input("Ingrese palabra a buscar en los comentarios: ")
            comments = comments_collection.find({"comment": {"$regex": textoComentario, "$options": "i"}})

            # Mostrar los resultados
            for comentario in comments:
                json_format = json.dumps(comentario, indent=4, default=str)
                print(json_format)

        elif opcion == "4":
            break

        else:
            print("Opción no válida. Intente nuevamente.")

# Menú principal
def menu_principal():
    while True:
        print("\n=== Menú Principal ===")
        print("1. Registrar usuario")
        print("2. Iniciar sesión")
        print("3. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar_usuario()
        elif opcion == "2":
            usuario = iniciar_sesion()
            if usuario:
                menu_usuario(usuario)
        elif opcion == "3":
            print("Saliendo del programa. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

# Menú para usuarios autenticados
def menu_usuario(usuario):
    while True:
        print("\n=== Menú Usuario ===")
        print("1. Comprar productos")
        print("2. Ver sucursales cercanas")
        print("3. Gestionar comentarios")
        print("4. Cerrar sesión")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            realizar_compra(usuario)
        elif opcion == "2":
            sucursales_cercanas(usuario)
        elif opcion == "3":
            gestionar_comentarios(usuario)
        elif opcion == "4":
            print("Cerrando sesión. Regresando al menú principal.")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

# Inicio del programa
if __name__ == "__main__":
    menu_principal()
