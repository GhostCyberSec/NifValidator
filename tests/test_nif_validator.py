import nif_validator as validator


def test_positive():
    db = ['292849680', '245832343', '121588955', '592889050', '522523129', '620365498', 
          '636695468', '998113360']
    for nif in db:
        print('[+] nif: {}'.format(nif))
        assert validator.valida_nif(nif)


def test_negative():
    db = ['292849681', '245382343', '12158895', '59288905000', '999999999', '123', '639566468']
    for nif in db:
        print('[-] nif: {}'.format(nif))
        assert validator.valida_nif(nif) == False


def test_dummy():
    db = ['', 'abc', '\r\n', '999999abc', '9999O9999', '999999990abc', 'a12345678', 
          'username!', '@999999990',
          ' 999999990', '999999990 ']
    for nif in db:
        print('[*] nif: {}'.format(nif))
        assert validator.valida_nif(nif) == False