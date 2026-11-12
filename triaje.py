import json
from datetime import datetime, timedelta
from pathlib import Path

from buscar_eventos import buscar_eventos


DIRECTORIO_DATOS = Path(__file__).resolve().parent / "data"


def obtener_evidencia():
    with (DIRECTORIO_DATOS / "alerta-100100.json").open(encoding="utf-8") as archivo:
        alerta = json.load(archivo)

    hasta = datetime.fromisoformat(alerta["timestamp"])
    desde = hasta - timedelta(seconds=60)

    eventos = buscar_eventos(
        ruta=DIRECTORIO_DATOS / "ssh-caso-003.jsonl",
        usuario=alerta["user"],
        servidor=alerta["host"],
        ip=alerta["src_ip"],
        desde=desde,
        hasta=hasta,
    )

    return {
        "alerta": alerta,
        "eventos_relacionados": eventos,
    }


def buscar_contexto(segundos):
    if type(segundos) is not int or not 60 <= segundos <= 300:
        raise ValueError("La ventana de contexto debe ser un entero entre 60 y 300 segundos.")

    with (DIRECTORIO_DATOS / "alerta-100100.json").open(encoding="utf-8") as archivo:
        alerta = json.load(archivo)

    hasta = datetime.fromisoformat(alerta["timestamp"])
    eventos = buscar_eventos(
        ruta=DIRECTORIO_DATOS / "ssh-caso-003.jsonl",
        usuario=None,
        servidor=alerta["host"],
        ip=alerta["src_ip"],
        desde=hasta - timedelta(seconds=segundos),
        hasta=hasta,
    )

    return [evento for evento in eventos if evento["user"] != alerta["user"]]


def main():
    evidencia = obtener_evidencia()
    print(json.dumps(evidencia, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
