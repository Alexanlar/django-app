from django import forms

from myauth.models import Profile


class UserAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar", ]
