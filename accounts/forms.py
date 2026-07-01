from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import CustomUser, ROLE_CHOICES


REGISTRATION_ROLE_CHOICES = [
    choice for choice in ROLE_CHOICES if choice[0] in ('owner', 'client')
]


class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        label='Tipo de conta',
        choices=REGISTRATION_ROLE_CHOICES,
        initial='client',
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'cpf', 'phone', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ink-input')
