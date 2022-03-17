from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField

User = get_user_model()


# class EmailAuthenticationForm(AuthenticationForm):
#     username = forms.EmailField()
#     password = forms.CharField(widget=forms.PasswordInput)
#     error_messages = {
#         "invalid_login": "Please enter a correct email and password.",
#         "inactive": "This account is inactive.",
#     }

#     def __init__(self, *args, **kwargs):
#         super(EmailAuthenticationForm, self).__init__(*args, **kwargs)
#         self.fields["username"].label = "Email"


class UserAdminCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if not user.client_id:
            user.client_id = user.email
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ["password"]

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    def __init__(self, *args, **kwargs):
        super(UserAdminChangeForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields["email"].required = False
