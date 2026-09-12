import json


async def cerrar_sala(
    salas,
    clientes,
    lock,
    nombre_sala
):

    print(
        "CERRAR_SALA EJECUTADA:",
        nombre_sala
    )

    async with lock:

        sala = salas.get(
            nombre_sala
        )

        if not sala:

            print(
                "ERROR: la sala no existe:",
                nombre_sala
            )

            return

        profesor = sala["profesor"]

        alumnos = []

        for nombre in sala["usuarios"]:

            if nombre != profesor:

                cliente = clientes.get(
                    nombre
                )

                if cliente:

                    alumnos.append(
                        (
                            nombre,
                            cliente
                        )
                    )

    print(
        "ALUMNOS A NOTIFICAR:",
        len(alumnos)
    )

    mensaje_sala_cerrada = {
        "tipo": "SALA_CERRADA",
        "mensaje":
            "La sala fue cerrada por el profesor."
    }

    datos_sala_cerrada = json.dumps(
        mensaje_sala_cerrada,
        ensure_ascii=False
    )

    mensaje_contactos = {
        "tipo": "CONTACTOS",
        "usuarios": []
    }

    datos_contactos = json.dumps(
        mensaje_contactos,
        ensure_ascii=False
    )

    for nombre, alumno in alumnos:

        try:

            print(
                "ENVIANDO SALA_CERRADA A:",
                nombre
            )

            await alumno.send_text(
                datos_sala_cerrada
            )

            print(
                "SALA_CERRADA ENVIADO A:",
                nombre
            )

            print(
                "ENVIANDO CONTACTOS VACIOS A:",
                nombre
            )

            await alumno.send_text(
                datos_contactos
            )

            print(
                "CONTACTOS VACIOS ENVIADO A:",
                nombre
            )

        except Exception as error:

            print(
                            "ERROR ENVIANDO DATOS A:",
                nombre,
                error
            )
