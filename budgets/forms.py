from django import forms

from budgets.models import BudgetRequest
from studios.models import TattooArtist


class BudgetRequestForm(forms.ModelForm):
    class Meta:
        model = BudgetRequest
        fields = ('artist', 'description', 'reference_image')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, studio=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.studio = studio
        if studio:
            self.fields['artist'].queryset = TattooArtist.objects.filter(
                studio=studio,
            ).order_by('name')
        else:
            self.fields['artist'].queryset = TattooArtist.objects.none()
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs.setdefault('class', 'ink-input')

    def clean_artist(self):
        artist = self.cleaned_data['artist']
        if self.studio and artist.studio_id != self.studio.pk:
            raise forms.ValidationError('Artista não pertence a este estúdio.')
        return artist
