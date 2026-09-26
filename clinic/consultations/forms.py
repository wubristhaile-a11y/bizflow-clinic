from django import forms

from clinic.services.models import Service


class InvestigationOrderForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=Service.objects.none(),
        label="Investigation",
        empty_label="Select an investigation",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    clinical_notes = forms.CharField(
        required=False,
        label="Clinical Notes / Instructions",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": (
                    "Enter relevant clinical instructions for "
                    "the laboratory or investigation department..."
                ),
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["service"].queryset = (
            Service.objects
            .filter(is_active=True)
            .select_related("department")
            .order_by("department__name", "name")
        )

        self.fields["service"].label_from_instance = (
            lambda service: (
                f"{service.name} — "
                f"{service.department.name} — "
                f"{service.price:.2f} ETB"
            )
        )