def validar_clasificacion(borrador, eventos):
    if not isinstance(borrador, dict):
        raise ValueError("El borrador debe ser un objeto.")

    categorias = {
        "fallos_ids": "ssh_failed",
        "exitos_ids": "ssh_success",
    }

    for campo, tipo in categorias.items():
        ids = borrador.get(campo)
        if not isinstance(ids, list) or not all(
            isinstance(evento_id, str) for evento_id in ids
        ):
            raise ValueError(f"{campo} debe ser una lista de IDs.")

        esperados = [
            evento["id"] for evento in eventos if evento["event"] == tipo
        ]
        if sorted(ids) != sorted(esperados):
            raise ValueError(f"{campo} no coincide con la evidencia.")
