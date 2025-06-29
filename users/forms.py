from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django import forms
from .helpers import mcuser


class UserRegistrationFormOld(UserCreationForm):
    email = forms.EmailField(required=True)
    application = forms.CharField(max_length=256, required=False, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].help_text = None
            
    def clean_application(self):
        data = self.cleaned_data['application']
        
        if not data:
            data = ''
        
        return data


class UserRegistrationForm(forms.ModelForm):
    
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )
    application = forms.CharField(max_length=256, required=False, widget=forms.Textarea)
    
    class Meta:
        model = User
        fields = ("username", 'password1', 'password2', 'email')
        
        help_texts = {
            'username': None
        }
        
    def clean_password1(self):
        data = self.cleaned_data["password1"]

        validate_password(data, User)

        return data
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "Passwords Mismatch",
                code="password_mismatch",
            )
        return password2
    
    def clean_username(self):
        data = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=data).exists():
            raise forms.ValidationError(
                "The username is already taken."
            )

        mcuuid = mcuser.username_to_mc_uuid(data) # ? Implement caching as this stage
            
        if not mcuuid:
            raise forms.ValidationError(
                "Such Minecraft user does not exist."
            )
            
        return data
        
    def clean_application(self):
        data = self.cleaned_data['application']
        
        if not data:
            data = ''
        
        return data
    
    def save(self, commit=False):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
        return user
