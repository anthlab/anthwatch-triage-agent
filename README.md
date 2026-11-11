# Anthwatch Triage Agent

Agente local que redacta borradores de triaje SOC a partir de alertas de Wazuh. La demo usa datos sintéticos basados en el caso SSH `100100` de [Anthwatch SOC Lab](https://github.com/anthlab/anthwatch-soc-lab).

Qwen3 recibe la alerta y solicita la herramienta `obtener_evidencia`. Python comprueba la solicitud, consulta los eventos locales y entrega el resultado al modelo. Antes de mostrar el borrador, el agente rechaza las citas con IDs `evt-...` ajenos a la evidencia.

## Ejecutar la demo

Con Python y Ollama instalados, ejecuta desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
ollama pull qwen3:4b
python agente.py
```

El caso contiene tres fallos SSH y una autenticación exitosa en 23 segundos. La autorización del acceso y la causa de los fallos quedan sin determinar.

## Pruebas

```bash
python -m unittest -v test_agente
```

Las dos pruebas simulan las respuestas del modelo y comprueban que el agente muestra un borrador con citas válidas y rechaza uno que cita un evento ajeno al caso.

## Alcance

La demo lee archivos locales y genera un borrador para revisión humana. El control comprueba las referencias a eventos. La interpretación del incidente requiere revisión.
