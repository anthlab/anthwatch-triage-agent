import json
from datetime import datetime
from pathlib import Path


def buscar_eventos(ruta, usuario, servidor, ip, desde, hasta):
    coincidencias = []

    with ruta.open(encoding="utf-8") as archivo:
        for linea in archivo:
            evento = json.loads(linea)
            hora = datetime.fromisoformat(evento["timestamp"])

            if (
                evento["user"] == usuario
                and evento["host"] == servidor
                and evento["src_ip"] == ip
                and desde <= hora <= hasta
            ):
                coincidencias.append(evento)

    return coincidencias


if __name__ == "__main__":
    ruta = Path("data/ssh-caso-003.jsonl")
    eventos = buscar_eventos(
        ruta,
        usuario="usuario-demo",
        servidor="anthwatch-server",
        ip="192.0.2.10",
        desde=datetime.fromisoformat("2026-11-11T09:00:00Z"),
        hasta=datetime.fromisoformat("2026-11-11T09:00:23Z"),
    )

    for evento in eventos:
        print(evento["id"], evento["user"], evento["event"])
