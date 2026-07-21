COSTOS_CONSTRUCCION = {
    "mina_hierro": 3,
    "mina_carbon": 2,
    "fundidora": 4,
}

PRECIOS_VENTA = {
    "hierro": 2,
    "carbon": 3,
    "lingotes": 8,
    "placas": 12,
    "engranajes": 30,
}

NOMBRES = {
    "hierro": "Hierro",
    "carbon": "Carbón",
    "lingotes": "Lingotes",
    "engranajes": "Engranajes",
    "placas": "Placas",
    "mina_hierro": "Mina de hierro",
    "mina_carbon": "Mina de carbón",
    "fundidora": "Fundidora",
}

ALIAS = {
    "mina de hierro": "mina_hierro",
    "mina hierro": "mina_hierro",
    "mina de carbon": "mina_carbon",
    "mina carbon": "mina_carbon",
    "fundidora": "fundidora",
    "hierro": "hierro",
    "carbon": "carbon",
    "lingote": "lingotes",
    "lingotes": "lingotes",
    "engranaje": "engranajes",
    "engranajes": "engranajes",
    "placa": "placas",
    "placas": "placas",
}


def obtener_nombre(clave):
    return NOMBRES.get(clave, clave)


def normalizar_clave(texto):
    texto = texto.strip().lower()
    return ALIAS.get(texto, texto)
