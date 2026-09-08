from django import forms

# Form Inputs and Styling
class VideoUploadForm(forms.Form):

    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Enter video title"
            }
        )
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-input",
                "placeholder": "Enter video description",
                "rows": 4
            }
        )
    )
    file_id = forms.CharField(max_length=200)
    video_url = forms.URLField(max_length=500)
    thumbnail_url = forms.URLField(max_length=500, required=False)