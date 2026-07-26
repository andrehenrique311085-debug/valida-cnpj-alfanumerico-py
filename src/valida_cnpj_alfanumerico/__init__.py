"""Validação, formatação e geração de CNPJ alfanumérico (e numérico).

Regras conforme a Receita Federal (IN RFB nº 2.229/2024):
  - 14 posições: as 12 primeiras (raiz + ordem) podem conter dígitos 0-9 e
    letras A-Z; as 2 últimas (dígitos verificadores) são sempre numéricas.
  - Valor de cada caractere para o cálculo do DV = código ASCII - 48
    ('0'-'9' -> 0-9, 'A'-'Z' -> 17-42).
  - DV por módulo 11, com os mesmos pesos do CNPJ tradicional.

Porta fiel da implementação de referência em JavaScript usada em
https://cnpjcomletras.com.br — mesmos algoritmo, mensagens de erro e
comportamento de máscara.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Optional

__all__ = [
    "strip_cnpj",
    "format_cnpj",
    "check_digits",
    "validate",
    "is_valid",
    "generate",
    "explain",
    "ValidationResult",
    "DigitStep",
    "ExplainResult",
]

_VALID_CHARS = re.compile(r"^[0-9A-Z]{12}[0-9]{2}$")
_HAS_14_ALNUM = re.compile(r"^[0-9A-Z]{14}$")
_REPEATED = re.compile(r"^(.)\1{13}$")
_HAS_LETTER = re.compile(r"[A-Z]")
_MASK_STRIP = re.compile(r"[.\-/\s]")

_WEIGHTS_DV1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
_WEIGHTS_DV2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

_DIGITS = "0123456789"
_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def strip_cnpj(value: Optional[str]) -> str:
    """Remove máscara (pontos, barra, hífen, espaços) e normaliza para maiúsculas."""
    return _MASK_STRIP.sub("", str(value or "").upper())


def _char_value(ch: str) -> int:
    return ord(ch) - 48


def _calc_digit(base: str, weights: list[int]) -> int:
    total = sum(_char_value(ch) * w for ch, w in zip(base, weights))
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def check_digits(base12: str) -> str:
    """Calcula os 2 dígitos verificadores de uma base de 12 caracteres. Retorna string de 2 dígitos."""
    dv1 = _calc_digit(base12, _WEIGHTS_DV1)
    dv2 = _calc_digit(base12 + str(dv1), _WEIGHTS_DV2)
    return f"{dv1}{dv2}"


@dataclass
class ValidationResult:
    valid: bool
    reason: Optional[str]
    stripped: str
    formatted: Optional[str]
    is_alphanumeric: bool
    expected_digits: Optional[str]


def validate(value: Optional[str]) -> ValidationResult:
    """Valida um CNPJ (com ou sem máscara), aceitando os formatos numérico e alfanumérico."""
    stripped = strip_cnpj(value)
    result = ValidationResult(
        valid=False, reason=None, stripped=stripped, formatted=None,
        is_alphanumeric=False, expected_digits=None,
    )

    if not stripped:
        result.reason = "empty"
        return result
    if len(stripped) != 14:
        result.reason = "length"
        return result
    if not _VALID_CHARS.match(stripped):
        result.reason = "dv_not_numeric" if _HAS_14_ALNUM.match(stripped) else "invalid_chars"
        return result
    if _REPEATED.match(stripped):
        result.reason = "repeated"
        return result

    result.is_alphanumeric = bool(_HAS_LETTER.search(stripped))
    result.expected_digits = check_digits(stripped[:12])

    if stripped[12:] != result.expected_digits:
        result.reason = "check_digits"
        return result

    result.valid = True
    result.formatted = format_cnpj(stripped)
    return result


def is_valid(value: Optional[str]) -> bool:
    return validate(value).valid


def format_cnpj(value: Optional[str]) -> str:
    """Aplica a máscara XX.XXX.XXX/XXXX-XX (aceita entrada parcial)."""
    s = strip_cnpj(value)[:14]
    out = []
    for i, ch in enumerate(s):
        if i in (2, 5):
            out.append(".")
        if i == 8:
            out.append("/")
        if i == 12:
            out.append("-")
        out.append(ch)
    return "".join(out)


def generate(alphanumeric: bool = True, branch: Optional[str] = None) -> str:
    """Gera um CNPJ válido para testes.

    alphanumeric: True (padrão) -> raiz pode conter letras; False -> só dígitos.
    branch: número da ordem/filial (padrão "0001").
    """
    pool = (_DIGITS + _LETTERS) if alphanumeric else _DIGITS
    root8 = "".join(random.choice(pool) for _ in range(8))

    # Garante ao menos uma letra quando alfanumérico for solicitado.
    if alphanumeric and not _HAS_LETTER.search(root8):
        pos = random.randrange(8)
        root8 = root8[:pos] + random.choice(_LETTERS) + root8[pos + 1:]

    branch_str = "0001" if branch is None else str(branch)
    branch_str = branch_str[-4:].rjust(4, "0")

    base12 = root8 + branch_str
    return base12 + check_digits(base12)


@dataclass
class DigitStep:
    rows: list[dict]
    sum: int
    remainder: int
    digit: int


@dataclass
class ExplainResult:
    base: str
    dv1: DigitStep
    dv2: DigitStep
    digits: str


def explain(value: Optional[str]) -> Optional[ExplainResult]:
    """Retorna o passo a passo do cálculo dos dígitos verificadores (uso didático/depuração)."""
    stripped = strip_cnpj(value)
    if len(stripped) < 12:
        return None
    base12 = stripped[:12]
    if not re.match(r"^[0-9A-Z]{12}$", base12):
        return None

    def steps(base: str, weights: list[int]) -> DigitStep:
        rows = []
        total = 0
        for ch, w in zip(base, weights):
            v = _char_value(ch)
            rows.append({"char": ch, "value": v, "weight": w, "product": v * w})
            total += v * w
        remainder = total % 11
        digit = 0 if remainder < 2 else 11 - remainder
        return DigitStep(rows=rows, sum=total, remainder=remainder, digit=digit)

    dv1 = steps(base12, _WEIGHTS_DV1)
    dv2 = steps(base12 + str(dv1.digit), _WEIGHTS_DV2)
    return ExplainResult(base=base12, dv1=dv1, dv2=dv2, digits=f"{dv1.digit}{dv2.digit}")
