import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def _only_digits(value):
    return re.sub(r'\D', '', value)


def validate_cpf(value):
    """Valida CPF brasileiro (11 dígitos, dígitos verificadores)."""
    cpf = _only_digits(value)
    if len(cpf) != 11:
        raise ValidationError(_('CPF deve conter 11 dígitos.'))
    if cpf == cpf[0] * 11:
        raise ValidationError(_('CPF inválido.'))

    for i in range(9, 11):
        weight = list(range(i + 1, 1, -1))
        total = sum(int(cpf[num]) * weight[num] for num in range(i))
        digit = (total * 10 % 11) % 10
        if int(cpf[i]) != digit:
            raise ValidationError(_('CPF inválido.'))


def validate_cnpj(value):
    """Valida CNPJ brasileiro (14 dígitos, dígitos verificadores)."""
    cnpj = _only_digits(value)
    if len(cnpj) != 14:
        raise ValidationError(_('CNPJ deve conter 14 dígitos.'))
    if cnpj == cnpj[0] * 14:
        raise ValidationError(_('CNPJ inválido.'))

    weights_first = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights_second = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    def calc_digit(cnpj_partial, weights):
        total = sum(int(d) * w for d, w in zip(cnpj_partial, weights))
        remainder = total % 11
        return '0' if remainder < 2 else str(11 - remainder)

    if calc_digit(cnpj[:12], weights_first) != cnpj[12]:
        raise ValidationError(_('CNPJ inválido.'))
    if calc_digit(cnpj[:13], weights_second) != cnpj[13]:
        raise ValidationError(_('CNPJ inválido.'))
