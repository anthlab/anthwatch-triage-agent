import json
from datetime import datetime, timedelta
from pathlib import Path

from buscar_eventos import buscar_eventos


def obtener_evidencia():
    with Path("data/alerta-100100.json").open(encoding="utf-8") as archivo:
        alerta = json.load(archivo)

    hasta = datetime.fromisoformat(alerta["timestamp"])
    desde = hasta - timedelta(seconds=60)

    eventos = buscar_eventos(
        ruta=Path("data/ssh-caso-003.jsonl"),
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


def main():
    evidencia = obtener_evidencia()
    print(json.dumps(evidencia, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
