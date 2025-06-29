from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django import forms

from users.models import ProfileComment, ProfileMedia, UserProfile
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
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
        return user


class ProfileCommentCreationForm(forms.ModelForm):
    action = forms.CharField(widget=forms.HiddenInput(), initial='create')
    
    class Meta:
        model = ProfileComment
        fields = ("text",)
        widgets = {
            'text': forms.Textarea()
        }
        
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio', 'signing')
        widgets = {
            'bio': forms.Textarea(),
            'signing': forms.Textarea()
        }

    
class UserUpdateForm(forms.ModelForm):

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        required=False
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        required=False
    )
    
    class Meta:
        model = User
        fields = ('username', 'email')
        
        help_texts = {
            'username': None
        }
    
    def clean_username(self):
        data = self.cleaned_data['username']
        if self.instance.username.lower() != data.lower():
            raise forms.ValidationError('You can only change the casing of the username.\
                                        Username itself cannot be changed.')
            
        return data
    
    def clean_password1(self):
        # Check if anything was entered in the Password field. If not, then ignore. 
        # If yes - use the clean method from the UserRegistrationForm form
        data = self.cleaned_data["password1"]
        if data:
            return UserRegistrationForm.clean_password1(self)
        else:
            return data
    
    def clean_password2(self):
        # Check if anything was entered in the Password confirmation field. If not, then ignore. 
        # If yes - use the clean method from the UserRegistrationForm form
        data = self.cleaned_data["password2"]
        if data:
            return UserRegistrationForm.clean_password2(self)
        else:
            return data

    def save(self, commit=True):
        user: User = super().save(commit=False)

        # Apply the changes only in case if any information was entered, else don't update anything
        if self.cleaned_data['password1'] and self.cleaned_data['password2']:
            new_password = self.cleaned_data['password1']
            user.set_password(new_password)


        if commit:
            user.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
                
        return user


class UploadMediaForm(forms.ModelForm):
    class Meta:
        model = ProfileMedia
        exclude = ("profile", "type", "is_visible")
