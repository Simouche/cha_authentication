from django.forms import forms, CharField


class LoginForm(forms.Form):
    username = CharField(required=True)
    password = CharField(required=True)
