# valida-cnpj-alfanumerico (Python)

Validação, formatação e geração de **CNPJ alfanumérico** (e numérico) em Python, conforme a [IN RFB nº 2.229/2024](https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2024/outubro/cnpj-tera-letras-e-numeros-a-partir-de-julho-de-2026).

- ✅ Algoritmo oficial da Receita Federal (valor do caractere = ASCII − 48, módulo 11)
- ✅ Valida os dois formatos: numérico tradicional e o novo alfanumérico (desde 31/07/2026)
- ✅ Zero dependências, Python 3.8+
- ✅ Porta fiel da [implementação de referência em JavaScript](https://github.com/andrehenrique311085-debug/valida-cnpj-alfanumerico) usada em produção em [cnpjcomletras.com.br](https://cnpjcomletras.com.br) — mesmos algoritmo e mensagens de erro
- ✅ Testado contra o exemplo oficial da Receita e 10.000 CNPJs gerados

> 🔧 Prefere validar sem instalar nada? Ferramentas online gratuitas (validador, validação em lote com CSV e gerador de massa de teste) em **[cnpjcomletras.com.br](https://cnpjcomletras.com.br)**.

## Instalação

```bash
pip install valida-cnpj-alfanumerico
```

## Uso

```python
import valida_cnpj_alfanumerico as cnpj

cnpj.is_valid("12.ABC.345/01DE-35")  # True  (exemplo oficial da Receita)
cnpj.is_valid("00.000.000/0001-91")  # True  (numérico continua válido)
cnpj.is_valid("12.ABC.345/01DE-00")  # False (DV não confere)

cnpj.validate("12ABC34501DE35")
# ValidationResult(valid=True, reason=None, stripped='12ABC34501DE35',
#                   formatted='12.ABC.345/01DE-35', is_alphanumeric=True, expected_digits='35')

cnpj.check_digits("12ABC34501DE")      # "35" — calcula os 2 DVs para uma base de 12
cnpj.format_cnpj("12abc34501de35")     # "12.ABC.345/01DE-35"
cnpj.strip_cnpj("12.ABC.345/01DE-35")  # "12ABC34501DE35"

cnpj.generate(alphanumeric=True)   # ex.: "IAKAXAJX000147" (CNPJ de teste válido)
cnpj.generate(alphanumeric=False)  # CNPJ de teste só numérico

ex = cnpj.explain("12ABC34501DE35")
ex.base, ex.digits  # ("12ABC34501DE", "35") — passo a passo do cálculo em ex.dv1 / ex.dv2
```

## O que muda com o CNPJ alfanumérico?

Desde **31 de julho de 2026**, novas inscrições podem receber CNPJ contendo letras:

| Posições | Conteúdo | Aceita |
|---|---|---|
| 1–8 (raiz) | identificação da empresa | `0-9` e `A-Z` |
| 9–12 (ordem) | estabelecimento | `0-9` e `A-Z` |
| 13–14 (DV) | dígitos verificadores | somente `0-9` |

CNPJs já emitidos **não mudam**. O cálculo do DV usa o mesmo módulo 11 de sempre, mas cada caractere entra com o valor **ASCII − 48** (`'0'`→0 … `'9'`→9, `'A'`→17 … `'Z'`→42).

Sistemas que guardam CNPJ como número, validam com regex só-dígitos (`^\d{14}$`) ou fazem `int(cnpj)` **rejeitam ou corrompem** os novos CNPJs. Guia completo de adaptação: [como adaptar seu sistema](https://cnpjcomletras.com.br/como-adaptar-sistema-cnpj-alfanumerico) · [funções em Python, Java, C# e SQL](https://cnpjcomletras.com.br/cnpj-alfanumerico-em-codigo).

## API

| Função | Descrição |
|---|---|
| `is_valid(valor)` | `True`/`False` — aceita com ou sem máscara, maiúsculas ou minúsculas |
| `validate(valor)` | `ValidationResult` com `valid`, `reason` (se inválido), `stripped`, `formatted`, `is_alphanumeric`, `expected_digits` |
| `check_digits(base12)` | calcula os 2 dígitos verificadores de uma base de 12 caracteres |
| `format_cnpj(valor)` | aplica a máscara `XX.XXX.XXX/XXXX-XX` |
| `strip_cnpj(valor)` | remove máscara e normaliza para maiúsculas |
| `generate(alphanumeric=True, branch=None)` | gera CNPJ de teste válido |
| `explain(valor)` | `ExplainResult` com o passo a passo do cálculo do DV (para depuração/didática) |

Motivos possíveis em `ValidationResult.reason`: `empty`, `length`, `invalid_chars`, `dv_not_numeric`, `repeated`, `check_digits`.

⚠️ A validação é **estrutural** (formato + dígitos verificadores). Ela não consulta a base da Receita Federal — um CNPJ estruturalmente válido pode não existir.

## Testes

```bash
pip install -e .
python tests/test_cnpj.py
# ou, com pytest instalado:
pytest tests/
```

## Ferramentas relacionadas

- 🔍 [Validador online + gerador de massa de teste](https://cnpjcomletras.com.br) — grátis, roda no navegador
- 📊 [Auditoria de Cadastro](https://cnpjcomletras.com.br/auditoria) — cole sua planilha de clientes/fornecedores e veja quantos CNPJs estão inválidos, duplicados ou corrompidos pelo Excel
- 🩺 [Diagnóstico de Prontidão](https://cnpjcomletras.com.br/diagnostico) — varredura do seu código-fonte atrás de padrões que quebram com o CNPJ alfanumérico

## Licença

[MIT](./LICENSE) © [CNPJcomLetras.com.br](https://cnpjcomletras.com.br)
