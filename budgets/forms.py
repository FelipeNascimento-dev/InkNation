from django import forms

from budgets.models import BudgetRequest


class BudgetRequestForm(forms.ModelForm):
    class Meta:
        model = BudgetRequest
        fields = ('artist', 'description', 'reference_image')

    def __init__(self, *args, studio=None, **kwargs):
        super().__init__(*args, **kwargs)
        if studio:
            self.fields['artist'].queryset = studio.artists.filter(is_active=True)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'ink-input')
