from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

        error_messages = {
            'text': {
                'required': _('Это обязательное поле.'),
            },
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = {'text'}
        widgets = {
            'text': forms.Textarea(attrs={'cols': 50, 'rows': 5})
        }
