from motor.grupos import (
    dezena_para_grupo,
    grupo_para_animal
)


def processar_numero(numero):
    """
    Processa um número de 4 dígitos e retorna
    milhar, centena, dezena, grupo e bicho.
    """

    numero = str(numero).strip().zfill(4)

    if not numero.isdigit():
        raise ValueError(f"Número inválido: {numero}")

    if len(numero) != 4:
        raise ValueError(f"O número deve ter 4 dígitos: {numero}")

    milhar = numero
    centena = numero[-3:]
    dezena = numero[-2:]

    grupo = dezena_para_grupo(int(dezena))
    bicho = grupo_para_animal(grupo)

    return {
        "milhar": milhar,
        "centena": centena,
        "dezena": dezena,
        "grupo": grupo,
        "bicho": bicho
    }
