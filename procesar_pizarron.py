import json


async def procesar_pizarron(
    clientes,
    salas,
    lock,
    estado,
    mensaje
):

    if estado["tipo_usuario"] != "Profesor":

        cliente = clientes.get(
            estado["nombre"]
        )

        if cliente:

            await cliente.send_text(
                json.dumps(
                    {
                        "tipo": "ERROR",
                        "mensaje":
                            "Solo el profesor puede modificar el pizarrón."
                    },
                    ensure_ascii=False
                )
            )

        return

    nombre_sala = estado["sala"]

    operacion = mensaje.get(
        "operacion"
    )

    pagina = mensaje.get(
        "pagina"
    )

    posicion = mensaje.get(
        "posicion"
    )

    texto = mensaje.get(
        "texto",
        ""
    )

    cantidad = mensaje.get(
        "cantidad"
    )

    if operacion not in (
        "INSERTAR",
        "BORRAR"
    ):

        return

    if not isinstance(
        pagina,
        int
    ):

        return

    if pagina < 0:

        return

    if not isinstance(
        posicion,
        int
    ):

        return

    if posicion < 0:

        return

    async with lock:

        sala = salas.get(
            nombre_sala
        )

        if not sala:

            return

        pizarron = sala.get(
            "pizarron"
        )

        if pizarron is None:

            pizarron = {
                "paginas": [""]
            }

            sala["pizarron"] = pizarron

        paginas = pizarron[
            "paginas"
        ]

        while len(paginas) <= pagina:

            paginas.append(
                ""
            )

        contenido = paginas[
            pagina
        ]

        if operacion == "INSERTAR":

            if not isinstance(
                texto,
                str
            ):

                return

            if posicion > len(
                contenido
            ):

                posicion = len(
                    contenido
                )

            contenido_nuevo = (
                contenido[
                    :posicion
                ]
                +
                texto
                +
                contenido[
                    posicion:
                ]
            )

            paginas[
                pagina
            ] = contenido_nuevo

        elif operacion == "BORRAR":

            if not isinstance(
                cantidad,
                int
            ):

                return

            if cantidad <= 0:

                return

            if posicion > len(
                contenido
            ):

                return

            fin = min(
                posicion + cantidad,
                len(contenido)
            )

            contenido_nuevo = (
                contenido[
                    :posicion
                ]
                +
                contenido[
                    fin:
                ]
            )

            paginas[
                pagina
            ] = contenido_nuevo

    datos = {
        "tipo": "PIZARRON",
        "operacion": operacion,
        "pagina": pagina,
        "posicion": posicion
    }

    if operacion == "INSERTAR":

        datos["texto"] = texto

    elif operacion == "BORRAR":

        datos["cantidad"] = cantidad

    nombre_profesor = estado[
        "nombre"
    ]

    async with lock:

        sala = salas.get(
            nombre_sala
        )

        if not sala:

            return

        conexiones = []

        for nombre in sala[
            "usuarios"
        ]:

            if nombre == nombre_profesor:

                continue

            cliente = clientes.get(
                nombre
            )

            if cliente:

                conexiones.append(
                    cliente
                )

    datos_json = json.dumps(
        datos,
        ensure_ascii=False
    )

    for cliente in conexiones:

        try:

            await cliente.send_text(
                datos_json
            )

        except Exception as error:

            print(
                "Error enviando pizarrón:",
                error
            )
