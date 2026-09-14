GRUPOS = {
    1: "Avestruz",
    2: "Águia",
    3: "Burro",
    4: "Borboleta",
    5: "Cachorro",
    6: "Cabra",
    7: "Carneiro",
    8: "Camelo",
    9: "Cobra",
    10: "Coelho",
    11: "Cavalo",
    12: "Elefante",
    13: "Galo",
    14: "Gato",
    15: "Jacaré",
    16: "Leão",
    17: "Macaco",
    18: "Porco",
    19: "Pavão",
    20: "Peru",
    21: "Touro",
    22: "Tigre",
    23: "Urso",
    24: "Veado",
    25: "Vaca"
}


def dezena_para_grupo(dezena):
    dezena = int(dezena)

    if dezena == 0:
        dezena = 100

    return ((dezena - 1) // 4) + 1


def grupo_para_animal(grupo):
    return GRUPOS.get(grupo, "Desconhecido")
