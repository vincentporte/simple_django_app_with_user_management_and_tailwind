from django import forms

from apps.users.models import User


class LoginForm(forms.Form):

    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Email"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return self.cleaned_data
            self.add_error("password", forms.ValidationError("Password is wrong"))
        except User.DoesNotExist:
            self.add_error("email", forms.ValidationError("User does not exist"))


class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First Name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last Name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email Name"}),
        }

    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:
            User.objects.get(email=email)
            raise forms.ValidationError("That email is already taken", code="existing_user")
        except User.DoesNotExist:
            return email

    def save(self, *args, **kwargs):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        user.set_password(password)
        user.save()
