from django import forms
from .models import MaintenanceRequest


class MaintenanceRequestForm(forms.ModelForm):

    class Meta:
        model = MaintenanceRequest
        fields = [
            "title",
            "description",
            "priority",
            "issue_image",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Example: Water leakage in bathroom",
                    "class": "form-control",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Describe the problem in detail...",
                    "rows": 5,
                    "class": "form-control",
                }
            ),
            "priority": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "issue_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }