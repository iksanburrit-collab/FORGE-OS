COSTOS_CONSTRUCCION = {
    "mina_hierro": 3,
    "mina_carbon": 2,
    "fundidora": 4,
    "generador_carbon": {
        "lingotes": 12,
        "engranajes": 2,
    },
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

NIVEL_MAXIMO = 3

PRODUCCION_POR_NIVEL = {
    "mina_hierro": {1: 2, 2: 3, 3: 4},
    "mina_carbon": {1: 1, 2: 2, 3: 3},
}

LOTES_FUNDIDORA_POR_NIVEL = {
    1: 1,
    2: 2,
    3: 3,
}

GENERACION_GENERADOR_POR_NIVEL = {
    1: 10,
    2: 15,
    3: 20,
}

COSTOS_MEJORAS = {
    "mina_hierro": {
        2: {"dinero": 50, "lingotes": 5},
        3: {"dinero": 120, "placas": 4},
    },
    "mina_carbon": {
        2: {"dinero": 50, "lingotes": 5},
        3: {"dinero": 120, "placas": 4},
    },
    "fundidora": {
        2: {"dinero": 80, "lingotes": 8},
        3: {"dinero": 180, "engranajes": 3},
    },
    "generador_carbon": {
        2: {"dinero": 100, "placas": 5},
        3: {"dinero": 250, "engranajes": 5},
    },
}

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
