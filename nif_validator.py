import doctest

def valida_nif(numero):
    """ Validação do número de identificação fiscal
    >>> valida_nif('999999990') 
    True
    >>> valida_nif('999999999') 
    False
    >>> valida_nif('501442600') 
    True
    """
    EXPECTED_DIGITS = 9
    if not numero.isdigit() or len(numero) != EXPECTED_DIGITS: 
        return False
    soma = sum([int(dig) * (EXPECTED_DIGITS - pos) for pos, dig in enumerate(numero)])
    resto = soma % 11
    if (numero[-1] == '0' and resto == 1):
        resto = (soma + 10) % 11
    return resto == 0

if __name__ == '__main__': # pragma: no cover
    doctest.testmod()