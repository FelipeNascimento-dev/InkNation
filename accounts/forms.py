import re

from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import CustomUser
from core.constants import CLIENT, STUDIO_OWNER

REGISTRATION_ROLE_CHOICES = [
    (CLIENT, 'Cliente'),
    (STUDIO_OWNER, 'Dono de estúdio'),
]


class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        label='Tipo de conta',
        choices=REGISTRATION_ROLE_CHOICES,
        initial=CLIENT,
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'cpf', 'phone', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ink-input')

    def clean_cpf(self):
        cpf = re.sub(r'\D', '', self.cleaned_data['cpf'])
        if len(cpf) != 11:
            raise forms.ValidationError('CPF deve conter 11 dígitos.')
        return cpf
