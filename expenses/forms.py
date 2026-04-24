from django import forms
from django.contrib.auth.models import User
from .models import Expense


class ExpenseForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'participant-checkbox'}),
        required=True,
        label='Split Between'
    )

    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'split_type', 'paid_by', 'date', 'note']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Dinner at Zomato'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'id': 'id_amount'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'split_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_split_type'}),
            'paid_by': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional note...'}),
        }

    def __init__(self, *args, group=None, **kwargs):
        super().__init__(*args, **kwargs)
        if group:
            members = list(group.members.all())
            if group.created_by not in members:
                members = [group.created_by] + members
            qs = User.objects.filter(id__in=[m.id for m in members])
            self.fields['participants'].queryset = qs
            self.fields['paid_by'].queryset = qs


class ExpenseFilterForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Search expenses...'}))
    category = forms.ChoiceField(required=False, choices=[('', 'All Categories')] + Expense.CATEGORY_CHOICES,
                                 widget=forms.Select(attrs={'class': 'form-select'}))
    split_type = forms.ChoiceField(required=False,
                                   choices=[('', 'All Split Types')] + Expense.SPLIT_CHOICES,
                                   widget=forms.Select(attrs={'class': 'form-select'}))
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
