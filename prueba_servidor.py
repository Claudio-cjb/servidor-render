import os
from fastapi import FastAPI, WebSocket

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    print("CONEXIÓN RECIBIDA")

    while True:
        mensaje = await websocket.receive_text()

        print(
            "MENSAJE RECIBIDO:",
            mensaje
        )

        await websocket.send_text(
            "Conexion recibida correctamente"
        )


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