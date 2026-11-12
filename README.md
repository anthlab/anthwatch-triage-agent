# Anthwatch Triage Agent

Prototipo local en Python para el triaje de alertas con Qwen3 y Ollama. Usa registros SSH sintéticos basados en la regla `100100` de [Anthwatch SOC Lab](https://github.com/anthlab/anthwatch-soc-lab).

## Cómo funciona

- `obtener_evidencia()` consulta los eventos del usuario, servidor e IP de la alerta en los 60 segundos previos, incluido el instante de la alerta.
- `buscar_contexto(segundos)` consulta opcionalmente actividad de otras cuentas desde la misma IP y en el mismo servidor. Python admite entre 60 y 300 segundos y muestra el contexto aparte del recuento principal.
- Qwen3 devuelve en JSON los IDs de los fallos y éxitos. Python comprueba ambas listas contra los registros, calcula la duración y genera el informe. Si la clasificación falla, permite un reintento con la evidencia ya consultada.

## Ejecutar

Requiere Python 3.11 o superior y Ollama en ejecución. El desarrollo se hizo con Python 3.14.4.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
ollama pull qwen3:4b
python agente.py
```

## Salida observada en el caso base

```text
Consulta ejecutada: obtener_evidencia
Borrador de triaje
Fallos SSH (3): evt-001, evt-002, evt-004
Éxitos SSH (1): evt-005
Ventana observada: 09:00:00–09:00:23 UTC (23 s)
Por confirmar: autorización del acceso y causa de los fallos.
```

## Pruebas

```bash
python -m unittest -v
```

Las ocho pruebas cubren los filtros, el rechazo de llamadas inválidas, la clasificación, el contexto y el reintento. Las pruebas del agente simulan las respuestas de Qwen3. La ejecución completa con Ollama de la versión con dos herramientas quedó pendiente tras superar el límite de 180 segundos.

## Alcance

La demo trabaja con archivos locales y genera un borrador para revisión humana. Una autenticación exitosa deja abierta la cuestión de si el acceso estaba autorizado. En una integración con Wazuh, los campos de los registros deben tratarse como datos no confiables: pueden contener texto que parezca una instrucción para el modelo.
