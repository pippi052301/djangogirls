from django import forms
from .models import Note, Folder, Tag, Attachment, NoteLink


class FolderForm(forms.ModelForm):

    class Meta:
        model = Folder
        fields = [
            'name',
            'parent'
        ]

    def __init__(self, *args, **kwargs):

        user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        if user:
            self.fields['parent'].queryset = Folder.objects.filter(
                owner=user
            )
class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = [
            'title',
            'folder',
            'content',
            'template_type',
        ]

        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nhập tiêu đề...'
                }
            ),

            'template_type': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        if user:
            self.fields['folder'].queryset = Folder.objects.filter(
                owner=user
            )
class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file', 'url', 'attachment_type']


class NoteLinkForm(forms.ModelForm):

    class Meta:
        model = NoteLink
        fields = [
            'to_note',
            'relation_label'
        ]

    def __init__(self, *args, **kwargs):

        user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        if user:
            self.fields['to_note'].queryset = Note.objects.filter(
                owner=user
            )


class NoteTagForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['tags'].queryset = Tag.objects.filter(owner=user)