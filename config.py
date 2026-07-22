COSTOS_CONSTRUCCION = {
    "mina_hierro": 3,
    "mina_carbon": 2,
    "fundidora": 4,
    "generador_carbon": {
        "lingotes": 12,
        "engranajes": 2,
    },
}

GENERACION_ENERGIA = {
    "generador_carbon": 10,
}

CONSUMO_CARBON_GENERADOR = 1
ENERGIA_INICIAL = 10

CONSUMO_ENERGIA = {
    "mina_carbon": 2,
    "mina_hierro": 2,
    "fundidora": 4,
}

PRIORIDAD_ENERGIA = (
    "mina_carbon",
    "mina_hierro",
    "fundidora",
)

PRECIOS_VENTA = {
    "hierro": 2,
    "carbon": 3,
    "lingotes": 8,
    "placas": 12,
    "engranajes": 30,
}

PRECIOS_COMPRA = {
    "hierro": 5,
    "carbon": 6,
    "lingotes": 12,
    "placas": 20,
    "engranajes": 40,
    "mina_carbon": 80,
    "mina_hierro": 100,
    "fundidora": 150,
    "generador_carbon": 200,
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
    "generador_carbon": "Generador de carbón",
}

ALIAS = {
    "mina de hierro": "mina_hierro",
    "mina hierro": "mina_hierro",
    "mina de carbon": "mina_carbon",
    "mina carbon": "mina_carbon",
    "fundidora": "fundidora",
    "generador carbon": "generador_carbon",
    "generador de carbon": "generador_carbon",
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
