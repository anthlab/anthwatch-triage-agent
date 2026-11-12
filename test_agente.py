import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

import agente


class TestAgente(unittest.TestCase):
    def setUp(self):
        funcion = SimpleNamespace(name="obtener_evidencia", arguments={})
        self.consulta = SimpleNamespace(
            message=SimpleNamespace(
                tool_calls=[SimpleNamespace(function=funcion)]
            )
        )
        self.clasificacion = {
            "fallos_ids": ["evt-001", "evt-002", "evt-004"],
            "exitos_ids": ["evt-005"],
        }

    def ejecutar_con_borrador(self, clasificacion):
        borrador = SimpleNamespace(
            message=SimpleNamespace(content=json.dumps(clasificacion))
        )
        salida = StringIO()

        with patch("agente.chat", side_effect=[self.consulta, borrador, borrador]):
            with redirect_stdout(salida):
                agente.main()

        return salida.getvalue()

    def test_muestra_clasificacion_y_duracion_correctas(self):
        salida = self.ejecutar_con_borrador(self.clasificacion)

        self.assertIn("Fallos SSH (3): evt-001, evt-002, evt-004", salida)
        self.assertIn("Éxitos SSH (1): evt-005", salida)
        self.assertIn("09:00:00–09:00:23 UTC (23 s)", salida)

    def test_rechaza_eventos_ajenos_mal_clasificados_u_omitidos(self):
        casos = {
            "evento de otro usuario": ["evt-001", "evt-002", "evt-003", "evt-004"],
            "éxito clasificado como fallo": ["evt-001", "evt-002", "evt-004", "evt-005"],
            "fallo omitido": ["evt-001", "evt-002"],
        }

        for nombre, fallos in casos.items():
            with self.subTest(caso=nombre):
                clasificacion = {**self.clasificacion, "fallos_ids": fallos}
                with self.assertRaisesRegex(
                    SystemExit, r"Borrador rechazado: fallos_ids no coincide"
                ):
                    self.ejecutar_con_borrador(clasificacion)

    def test_bloquea_peticiones_invalidas_antes_de_leer_evidencia(self):
        herramienta_desconocida = SimpleNamespace(
            function=SimpleNamespace(name="otra_herramienta", arguments={})
        )
        herramienta_con_argumentos = SimpleNamespace(
            function=SimpleNamespace(
                name="obtener_evidencia",
                arguments={"host": "otro-servidor"},
            )
        )
        casos = {
            "sin llamadas": ([], "Se esperaba una sola solicitud"),
            "nombre incorrecto": ([herramienta_desconocida], "fuera del alcance"),
            "argumentos no permitidos": ([herramienta_con_argumentos], "fuera del alcance"),
        }

        for nombre, (llamadas, mensaje) in casos.items():
            with self.subTest(caso=nombre):
                respuesta = SimpleNamespace(
                    message=SimpleNamespace(tool_calls=llamadas)
                )

                with patch("agente.chat", return_value=respuesta) as chat:
                    with patch("agente.obtener_evidencia") as obtener_evidencia:
                        with self.assertRaisesRegex(SystemExit, mensaje):
                            agente.main()

                obtener_evidencia.assert_not_called()
                chat.assert_called_once()

    def test_muestra_contexto_sin_mezclarlo_con_el_caso_principal(self):
        contexto = SimpleNamespace(
            function=SimpleNamespace(name="buscar_contexto", arguments={"segundos": 60})
        )
        self.consulta.message.tool_calls.append(contexto)

        salida = self.ejecutar_con_borrador(self.clasificacion)

        self.assertIn("Fallos SSH (3): evt-001, evt-002, evt-004\n", salida)
        self.assertIn("Éxitos SSH (1): evt-005\n", salida)
        self.assertIn(
            "Contexto de otras cuentas:\n  evt-003 | otro-usuario | ssh_failed\n",
            salida,
        )

    def test_rechaza_una_ventana_de_contexto_superior_a_300_segundos(self):
        contexto = SimpleNamespace(
            function=SimpleNamespace(name="buscar_contexto", arguments={"segundos": 301})
        )
        self.consulta.message.tool_calls.append(contexto)

        with patch("agente.chat", return_value=self.consulta) as chat:
            with self.assertRaisesRegex(SystemExit, "Consulta de contexto rechazada"):
                agente.main()

        chat.assert_called_once()

    def test_corrige_la_clasificacion_en_el_segundo_intento(self):
        clasificacion_invalida = {
            **self.clasificacion,
            "fallos_ids": ["evt-001", "evt-002", "evt-004", "evt-005"],
            "exitos_ids": [],
        }
        primer_borrador = SimpleNamespace(
            message=SimpleNamespace(content=json.dumps(clasificacion_invalida))
        )
        segundo_borrador = SimpleNamespace(
            message=SimpleNamespace(content=json.dumps(self.clasificacion))
        )
        salida = StringIO()

        with (
            patch(
                "agente.chat",
                side_effect=[self.consulta, primer_borrador, segundo_borrador],
            ) as chat,
            patch("agente.obtener_evidencia", wraps=agente.obtener_evidencia) as evidencia,
            redirect_stdout(salida),
        ):
            agente.main()

        self.assertEqual(chat.call_count, 3)
        evidencia.assert_called_once()
        self.assertIn("Reintentando...", salida.getvalue())
        self.assertIn("Éxitos SSH (1): evt-005", salida.getvalue())
