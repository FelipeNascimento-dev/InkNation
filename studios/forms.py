from django import forms

from studios.models import PortfolioItem, Studio, TattooArtist


class StudioRegistrationForm(forms.ModelForm):
    class Meta:
        model = Studio
        fields = (
            'name',
            'cnpj',
            'address',
            'city',
            'state',
            'zip_code',
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


class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ('title', 'image')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ink-input')


class TattooArtistForm(forms.ModelForm):
    class Meta:
        model = TattooArtist
        fields = ('name', 'bio', 'instagram', 'specialties', 'is_active')

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
