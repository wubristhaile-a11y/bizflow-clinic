from django import forms


class LabResultForm(forms.Form):

    result = forms.CharField(
        label="Laboratory Result",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 8,
                "placeholder": (
                    "Enter the laboratory findings..."
                ),
            }
        ),
    )

    notes = forms.CharField(
        label="Laboratory Notes",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": (
                    "Additional notes or comments..."
                ),
            }
        ),
    )