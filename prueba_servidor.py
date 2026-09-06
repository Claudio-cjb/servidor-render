import os
import json
import asyncio

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect
)


app = FastAPI()


clientes = {}

salas = {}

lock = asyncio.Lock()


async def enviar_a_cliente(
    cliente,
    datos
):

    try:

        mensaje = json.dumps(
            datos,
            ensure_ascii=False
        )

        await cliente.send_text(
            mensaje
        )

    except Exception as error:

        print(
            "Error enviando datos:",
            error
        )


async def enviar_error(
    cliente,
    mensaje
):

    await enviar_a_cliente(
        cliente,
        {
            "tipo": "ERROR",
            "mensaje": mensaje
        }
    )


async def obtener_usuarios_sala(
    nombre_sala
):

    async with lock:

        sala = salas.get(
            nombre_sala
        )

        if not sala:

            return []

        usuarios = []

        for nombre in sala["usuarios"]:

            if nombre in clientes:

                usuarios.append(
                    nombre
                )

        return usuarios


async def anunciar_contactos_sala(
    nombre_sala
):

    usuarios = await obtener_usuarios_sala(
        nombre_sala
    )

    async with lock:

        sala = salas.get(
            nombre_sala
        )

        if not sala:

            return

        conexiones = []

        for nombre in usuarios:

            cliente = clientes.get(
                nombre
            )

            if cliente:

                conexiones.append(
                    cliente
                )

    datos = {
        "tipo": "CONTACTOS",
        "usuarios": usuarios
    }

    for cliente in conexiones:

        await enviar_a_cliente(
            cliente,
            datos
        )


async def registrar_usuario(
    cliente,
    estado,
    mensaje
):

    nombre = (
        mensaje.get(
            "nombre"
        )
    )

    tipo_usuario = (
        mensaje.get(
            "tipo_usuario"
        )
    )

    nombre_sala = (
        mensaje.get(
            "sala"
        )
    )

    contrasena = (
        mensaje.get(
            "contrasena"
        )
    )

    if not nombre:

        await enviar_error(
            cliente,
            "Debe indicar un nombre."
        )

        return False

    if not tipo_usuario:

        await enviar_error(
            cliente,
            "Debe indicar el tipo de usuario."
        )

        return False

    if tipo_usuario not in (
        "Profesor",
        "Alumno"
    ):

        await enviar_error(
            cliente,
            "Tipo de usuario inválido."
        )

        return False

    if not nombre_sala:

        await enviar_error(
            cliente,
            "Debe indicar una sala."
        )

        return False

    nombre = nombre.strip()

    nombre_sala = (
        nombre_sala.strip()
    )

    if not nombre:

        await enviar_error(
            cliente,
            "El nombre no puede estar vacío."
        )

        return False

    if not nombre_sala:

        await enviar_error(
            cliente,
            "El nombre de la sala no puede estar vacío."
        )

        return False

    async with lock:

        if nombre in clientes:

            usuario_existente = True

        else:

            usuario_existente = False

    if usuario_existente:

        await enviar_error(
            cliente,
            "El usuario ya está conectado."
        )

        return False

    if tipo_usuario == "Profesor":

        if not contrasena:

            await enviar_error(
                cliente,
                "Debe indicar una contraseña."
            )

            return False

        async with lock:

            if nombre_sala in salas:

                sala_existente = True

            else:

                sala_existente = False

        if sala_existente:

            await enviar_error(
                cliente,
                "La sala ya existe."
            )

            return False

        async with lock:

            salas[nombre_sala] = {
                "contrasena": contrasena,
                "profesor": nombre,
                "usuarios": set()
            }

            salas[
                nombre_sala
            ]["usuarios"].add(
                nombre
            )

            clientes[
                nombre
            ] = cliente

        estado["nombre"] = nombre
        estado["tipo_usuario"] = tipo_usuario
        estado["sala"] = nombre_sala

        print(
            "Sala creada:",
            nombre_sala
        )

        print(
            "Profesor:",
            nombre
        )

        await enviar_a_cliente(
            cliente,
            {
                "tipo": "REGISTRO_OK",
                "nombre": nombre,
                "tipo_usuario": tipo_usuario,
                "sala": nombre_sala
            }
        )

        await anunciar_contactos_sala(
            nombre_sala
        )

        return True

    if tipo_usuario == "Alumno":

        if not contrasena:

            await enviar_error(
                cliente,
                "Debe indicar una contraseña."
            )

            return False

        async with lock:

            sala = salas.get(
                nombre_sala
            )

        if not sala:

            await enviar_error(
                cliente,
                "La sala no existe."
            )

            return False

        if sala["contrasena"] != contrasena:

            await enviar_error(
                cliente,
                "Contraseña incorrecta."
            )

            return False

        async with lock:

            salas[
                nombre_sala
            ]["usuarios"].add(
                nombre
            )

            clientes[
                nombre
            ] = cliente

        estado["nombre"] = nombre
        estado["tipo_usuario"] = tipo_usuario
        estado["sala"] = nombre_sala

        print(
            "Alumno conectado:",
            nombre
        )

        print(
            "Sala:",
            nombre_sala
        )

        await enviar_a_cliente(
            cliente,
            {
                "tipo": "REGISTRO_OK",
                "nombre": nombre,
                "tipo_usuario": tipo_usuario,
                "sala": nombre_sala
            }
        )

        await anunciar_contactos_sala(
            nombre_sala
        )

        return True

    return False


async def procesar_mensaje(
    cliente,
    estado,
    mensaje
):

    tipo = mensaje.get(
        "tipo"
    )

    if tipo == "REGISTRAR":

        if estado["nombre"]:

            await enviar_error(
                cliente,
                "El usuario ya está registrado."
            )

            return

        await registrar_usuario(
            cliente,
            estado,
            mensaje
        )

        return

    if not estado["nombre"]:

        await enviar_error(
            cliente,
            "El usuario no está registrado."
        )

        return

    if tipo == "MENSAJE":

        await enviar_mensaje(
            cliente,
            estado,
            mensaje
        )

        return

    if tipo == "SALIR":

        return

    await enviar_error(
        cliente,
        "Tipo de mensaje desconocido."
    )


async def enviar_mensaje(
    cliente,
    estado,
    mensaje
):

    destinatario = (
        mensaje.get(
            "destinatario"
        )
    )

    texto = (
        mensaje.get(
            "texto"
        )
    )

    if not destinatario:

        await enviar_error(
            cliente,
            "Debe indicar un destinatario."
        )

        return

    if not texto:

        return

    nombre = estado["nombre"]

    nombre_sala = estado["sala"]

    async with lock:

        sala = salas.get(
            nombre_sala
        )

        if not sala:

            await enviar_error(
                cliente,
                "La sala ya no existe."
            )

            return

        if destinatario not in sala["usuarios"]:

            await enviar_error(
                cliente,
                "El destinatario no pertenece a esta sala."
            )

            return

        cliente_destino = clientes.get(
            destinatario
        )

    if not cliente_destino:

        await enviar_error(
            cliente,
            "El usuario no está conectado."
        )

        return

    await enviar_a_cliente(
        cliente_destino,
        {
            "tipo": "MENSAJE",
            "remitente": nombre,
            "texto": texto
        }
    )

    print(
        f"{nombre} -> "
        f"{destinatario}: "
        f"{texto}"
    )


async def atender_cliente(
    cliente,
    direccion
):

    estado = {
        "nombre": None,
        "tipo_usuario": None,
        "sala": None
    }

    print(
        "Nueva conexión:",
        direccion
    )

    try:

        while True:

            datos = await cliente.receive_text()

            print(
                "MENSAJE RECIBIDO:",
                datos
            )

            try:

                mensaje = json.loads(
                    datos
                )

            except json.JSONDecodeError:

                await enviar_error(
                    cliente,
                    "Mensaje JSON inválido."
                )

                continue

            await procesar_mensaje(
                cliente,
                estado,
                mensaje
            )

    except WebSocketDisconnect:

        print(
            "Conexión cerrada:",
            direccion
        )

    except Exception as error:

        print(
            "Error con cliente:",
            error
        )

    finally:

        nombre = estado["nombre"]

        nombre_sala = estado["sala"]

        if nombre:

            async with lock:

                if (
                    clientes.get(
                        nombre
                    ) is cliente
                ):

                    del clientes[
                        nombre
                    ]

                sala = salas.get(
                    nombre_sala
                )

                if sala:

                    sala["usuarios"].discard(
                        nombre
                    )

                    if (
                        nombre
                        ==
                        sala["profesor"]
                    ):

                        del salas[
                            nombre_sala
                        ]

                        sala_eliminada = True

                    elif not sala["usuarios"]:

                        del salas[
                            nombre_sala
                        ]

                        sala_eliminada = True

                    else:

                        sala_eliminada = False

                else:

                    sala_eliminada = False

            print(
                "Usuario desconectado:",
                nombre
            )

            if sala_eliminada:

                print(
                    "Sala eliminada:",
                    nombre_sala
                )

            else:

                await anunciar_contactos_sala(
                    nombre_sala
                )


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket
):

    await websocket.accept()

    print(
        "CONEXIÓN RECIBIDA"
    )

    direccion = websocket.client

    await atender_cliente(
        websocket,
        direccion
    )


@app.get("/")
async def inicio():

    return {
        "estado":
            "Servidor Aula Estudio funcionando"
    }


if __name__ == "__main__":

    import uvicorn

    puerto = int(
        os.environ.get(
            "PORT",
            5001
        )
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=puerto
    )
