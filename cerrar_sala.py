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

    mensaje = {
        "tipo": "SALA_CERRADA",
        "mensaje":
            "La sala fue cerrada por el profesor."
    }

    datos = json.dumps(
        mensaje,
        ensure_ascii=False
    )

    for nombre, alumno in alumnos:

        try:

            print(
                "ENVIANDO SALA_CERRADA A:",
                nombre
            )

            await alumno.send_text(
                datos
            )

            print(
                "SALA_CERRADA ENVIADO A:",
                nombre
            )

        except Exception as error:

            print(
                "ERROR ENVIANDO SALA_CERRADA A:",
                nombre,
                error
            )