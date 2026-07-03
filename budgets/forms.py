from django import forms

from budgets.models import (
    BUDGET_STATUS_ANSWERED,
    BUDGET_STATUS_CHOICES,
    BUDGET_STATUS_IN_ANALYSIS,
    BUDGET_STATUS_SENT,
    BudgetRequest,
)
from studios.models import TattooArtist


NEXT_STATUS_BY_CURRENT = {
    BUDGET_STATUS_SENT: (
        BUDGET_STATUS_SENT,
        BUDGET_STATUS_IN_ANALYSIS,
        BUDGET_STATUS_ANSWERED,
    ),
    BUDGET_STATUS_IN_ANALYSIS: (
        BUDGET_STATUS_IN_ANALYSIS,
        BUDGET_STATUS_ANSWERED,
    ),
    BUDGET_STATUS_ANSWERED: (BUDGET_STATUS_ANSWERED,),
}


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


class BudgetStatusForm(forms.ModelForm):
    class Meta:
        model = BudgetRequest
        fields = ('status',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed = NEXT_STATUS_BY_CURRENT.get(
            self.instance.status,
            (self.instance.status,),
        )
        labels = dict(BUDGET_STATUS_CHOICES)
        self.fields['status'].choices = [
            (value, labels[value]) for value in allowed
        ]
        self.fields['status'].widget.attrs.setdefault('class', 'ink-input')
