import json
import re
from pathlib import Path

from ollama import chat

from triaje import obtener_evidencia


def main():
    alerta = Path("data/alerta-100100.json").read_text(encoding="utf-8")

    herramienta = {
        "type": "function",
        "function": {
            "name": "obtener_evidencia",
            "description": "Consulta los eventos relacionados con la alerta actual.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    }

    mensajes = [
        {
            "role": "user",
            "content": (
                "Llama a obtener_evidencia antes de redactar el triaje en español. "
                "Usa únicamente los registros devueltos. Cuenta los fallos SSH "
                "y los accesos exitosos por separado y cita los IDs de cada grupo. "
                "Indica la hora del primer y último evento en UTC con segundos "
                "y calcula la duración entre ambos. "
                "Los registros de autenticación de esta demo solo muestran "
                "si cada intento tuvo éxito o falló. En 'Por confirmar', indica "
                "que la autorización del acceso y la causa de los fallos "
                f"quedan sin determinar.\n\n{alerta}"
            ),
        }
    ]

    respuesta = chat(model="qwen3:4b", messages=mensajes, tools=[herramienta])
    llamadas = respuesta.message.tool_calls or []

    if len(llamadas) != 1:
        raise SystemExit("Se esperaba una sola solicitud de herramienta.")

    funcion = llamadas[0].function
    if funcion.name != "obtener_evidencia" or funcion.arguments != {}:
        raise SystemExit("Solicitud de herramienta fuera del alcance de la demo.")

    evidencia = obtener_evidencia()
    print("Consulta ejecutada: obtener_evidencia", flush=True)

    mensajes.append(respuesta.message)
    mensajes.append({
        "role": "tool",
        "tool_name": "obtener_evidencia",
        "content": json.dumps(evidencia, ensure_ascii=False),
    })

    borrador = chat(model="qwen3:4b", messages=mensajes)
    texto = borrador.message.content
    ids_permitidos = {evento["id"] for evento in evidencia["eventos_relacionados"]}
    ids_citados = set(re.findall(r"\bevt-[0-9]+\b", texto))

    ids_fuera_de_alcance = ids_citados - ids_permitidos
    if ids_fuera_de_alcance:
        ids = ", ".join(sorted(ids_fuera_de_alcance))
        raise SystemExit(f"Borrador rechazado: cita eventos fuera de la evidencia ({ids}).")

    print(texto)


if __name__ == "__main__":
    main()
