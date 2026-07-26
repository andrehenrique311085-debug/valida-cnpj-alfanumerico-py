import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import valida_cnpj_alfanumerico as cnpj


def test_exemplo_oficial_receita():
    assert cnpj.check_digits("12ABC34501DE") == "35"
    assert cnpj.is_valid("12.ABC.345/01DE-35")


def test_minusculas_normalizadas():
    assert cnpj.is_valid("12abc34501de35")


def test_dv_errado_invalido():
    assert not cnpj.is_valid("12.ABC.345/01DE-36")


def test_cnpjs_numericos_reais():
    assert cnpj.is_valid("00.000.000/0001-91")
    assert cnpj.is_valid("33.000.167/0001-01")
    assert not cnpj.is_valid("00.000.000/0001-92")


def test_regras_de_rejeicao():
    assert not cnpj.is_valid("")
    assert not cnpj.is_valid("123")
    assert not cnpj.is_valid("11111111111111")
    assert not cnpj.is_valid("12ABC34501DEA5")
    assert cnpj.validate("12ABC34501DEA5").reason == "dv_not_numeric"
    assert not cnpj.is_valid("12ÃBC34501DE35")  # caractere fora de A-Z/0-9


def test_formatacao():
    assert cnpj.format_cnpj("12ABC34501DE35") == "12.ABC.345/01DE-35"
    assert cnpj.format_cnpj("12AB") == "12.AB"


def test_gerador_massa():
    for _ in range(5000):
        a = cnpj.generate(alphanumeric=True)
        n = cnpj.generate(alphanumeric=False)
        assert cnpj.is_valid(a) and re.search(r"[A-Z]", a[:12])
        assert cnpj.is_valid(n) and not re.search(r"[A-Z]", n)


def test_explain_coerente():
    ex = cnpj.explain("12ABC34501DE")
    assert ex is not None
    assert ex.digits == "35"
    assert ex.dv1.sum == 459
    assert ex.dv2.sum == 424


if __name__ == "__main__":
    import traceback

    testes = [v for k, v in list(globals().items()) if k.startswith("test_")]
    falhas = 0
    for t in testes:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError:
            falhas += 1
            print(f"FAIL  {t.__name__}")
            traceback.print_exc()
    print("\nTodos os testes passaram." if falhas == 0 else f"\n{falhas} teste(s) falharam.")
    sys.exit(0 if falhas == 0 else 1)
