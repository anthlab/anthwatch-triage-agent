import unittest
from datetime import datetime
from pathlib import Path

from buscar_eventos import buscar_eventos


class TestBuscarEventos(unittest.TestCase):
    def buscar_ids(self, desde, hasta):
        eventos = buscar_eventos(
            ruta=Path("data/ssh-caso-003.jsonl"),
            usuario="usuario-demo",
            servidor="anthwatch-server",
            ip="192.0.2.10",
            desde=datetime.fromisoformat(f"2026-11-11T{desde}Z"),
            hasta=datetime.fromisoformat(f"2026-11-11T{hasta}Z"),
        )
        return [evento["id"] for evento in eventos]

    def test_excluye_eventos_de_otro_usuario(self):
        ids = self.buscar_ids("08:59:23", "09:00:24")
        self.assertEqual(ids, ["evt-001", "evt-002", "evt-004", "evt-005"])

    def test_incluye_eventos_en_ambos_limites(self):
        ids = self.buscar_ids("09:00:05", "09:00:15")
        self.assertEqual(ids, ["evt-002", "evt-004"])
