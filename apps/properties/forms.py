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


class OwnerMaintenanceUpdateForm(forms.ModelForm):

    class Meta:
        model = MaintenanceRequest
        fields = ["status", "owner_note"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-control"}),
            "owner_note": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Add an update for the tenant",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_statuses = {
            "PENDING": ["PENDING", "IN_PROGRESS"],
            "IN_PROGRESS": ["IN_PROGRESS", "RESOLVED", "REJECTED"],
        }.get(self.instance.status, [])
        self.fields["status"].required = False
        self.fields["status"].choices = [("", "Keep current status")] + [
            choice
            for choice in MaintenanceRequest.STATUS_CHOICES
            if choice[0] in allowed_statuses
        ]
        self.initial["owner_note"] = ""

    def clean_status(self):
        return self.cleaned_data.get("status") or self.instance.status