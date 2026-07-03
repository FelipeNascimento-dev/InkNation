import re

from django import forms

from studios.models import PortfolioItem, Studio, TattooArtist


class StudioRegistrationForm(forms.ModelForm):
    class Meta:
        model = Studio
        fields = (
            'name',
            'cnpj',
            'address_street',
            'address_number',
            'neighborhood',
            'city',
            'state',
            'cep',
            'latitude',
            'longitude',
        )
        widgets = {
            'latitude': forms.NumberInput(attrs={'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'step': 'any'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ink-input')

    def clean_cnpj(self):
        cnpj = re.sub(r'\D', '', self.cleaned_data['cnpj'])
        if len(cnpj) != 14:
            raise forms.ValidationError('CNPJ deve conter 14 dígitos.')
        return cnpj

    def clean_cep(self):
        cep = re.sub(r'\D', '', self.cleaned_data['cep'])
        if len(cep) != 8:
            raise forms.ValidationError('CEP deve conter 8 dígitos.')
        return cep


class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ('image',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ink-input')


class TattooArtistForm(forms.ModelForm):
    class Meta:
        model = TattooArtist
        fields = ('name', 'bio', 'instagram', 'specialties')

    def __init__(self, *args, **kwargs):
        self.studio = kwargs.pop('studio', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ink-input')

    def save(self, commit=True):
        artist = super().save(commit=False)
        if self.studio:
            artist.studio = self.studio
        if commit:
            artist.save()
        return artist
