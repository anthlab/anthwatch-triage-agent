import unittest
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

import agente


class TestAgente(unittest.TestCase):
    def setUp(self):
        funcion = SimpleNamespace(name="obtener_evidencia", arguments={})
        llamada = SimpleNamespace(function=funcion)
        self.consulta = SimpleNamespace(
            message=SimpleNamespace(tool_calls=[llamada])
        )

    def test_rechaza_evento_fuera_de_la_evidencia(self):
        borrador = SimpleNamespace(
            message=SimpleNamespace(content="El evento evt-003 forma parte del caso.")
        )

        with patch("agente.chat", side_effect=[self.consulta, borrador]):
            with self.assertRaises(SystemExit) as error:
                agente.main()

        self.assertEqual(
            str(error.exception),
            "Borrador rechazado: cita eventos fuera de la evidencia (evt-003).",
        )

    def test_muestra_borrador_con_citas_validas(self):
        texto = "Tres fallos (evt-001, evt-002, evt-004) y un acceso exitoso (evt-005)."
        borrador = SimpleNamespace(message=SimpleNamespace(content=texto))

        with patch("agente.chat", side_effect=[self.consulta, borrador]):
            with patch("sys.stdout", new_callable=StringIO) as salida:
                agente.main()

        self.assertIn(texto, salida.getvalue())
