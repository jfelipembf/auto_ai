from db.especialistas import listar_especialistas

def escolher_especialista(pedido):
    especialistas = listar_especialistas()
    for esp in especialistas:
        if esp["status"] == "ativo" and esp["especialidade"].lower() in pedido.lower():
            return esp
    return None
