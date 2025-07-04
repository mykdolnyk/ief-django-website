from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
import common.forms

from users.models import ProfileComment, ProfileMedia, UserProfile
from .helpers import mcuser
from users import tasks

class UserRegistrationForm(forms.ModelForm):

    template_name = "users/logreg/registration_form_template.html"

    password1 = forms.CharField(
        label="",  # This label is defined in the template
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )
    application = forms.CharField(
        max_length=256, required=False, widget=forms.Textarea(attrs={'rows': 4}))

    class Meta:
        model = User
        fields = ("username", 'email')

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

        mcuuid = mcuser.username_to_mc_uuid(data)

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
    
    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError(
                "The email address is already taken."
            )
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
        return user


class UserAuthenticationForm(AuthenticationForm):
    # Expand the error messages dict
    error_messages = {'login_restricted':
                      f'Too many login attempts. Please try again in about {settings.LOGIN_RESTRICTION_TIMEOUT // 60} minutes.',
                      **AuthenticationForm.error_messages}

    def clean_username(self):
        # To make the form case-insensetive, I will replace 
        # the incorrect casing with the correct one
        data = self.cleaned_data.get("username")
        
        try:
            correct_username = User.objects.get(username__iexact=data)
        except User.DoesNotExist:
            return self.get_invalid_login_error()
        return correct_username

    def get_login_restricted_error(self):
        return forms.ValidationError(
            self.error_messages['login_restricted'],
            code='login_restricted'
        )


class ProfileCommentCreationForm(common.forms.AbstractCommentCreationForm):
    class Meta(common.forms.AbstractCommentCreationForm.Meta):
        model = ProfileComment


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio', 'signing')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3,
                                         'placeholder': "Tell us about yourself!"}),
            'signing': forms.Textarea(attrs={'rows': 3,
                                             'placeholder': "You can enter your signature here. It will be automatically added to every post you made."})
        }


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'email')

        help_texts = {
            'username': 'Note: You can only change the casing of the username.\
                                        Username itself cannot be changed.'
        }

    def clean_username(self):
        data = self.cleaned_data['username']
        if self.instance.username.lower() != data.lower():
            raise forms.ValidationError('You can only change the casing of the username.\
                                        Username itself cannot be changed.')

        return data

    def save(self, commit=True):
        user: User = super().save(commit=False)

        if commit:
            user.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()

        return user


class UserPasswordChangeForm(forms.ModelForm):

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", 'placeholder': 'Your New Password'}),
        strip=False,
        required=False
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", 'placeholder': 'Your New Password Again'}),
        strip=False,
        required=False
    )

    class Meta:
        model = User
        fields = list()

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

        labels = {
            'image': '',
            'title': 'Image Title',
        }


class PasswordResetEmailForm(PasswordResetForm):
    """Password Reset Email Form with `send_mail` method remade for using Celery."""
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name = ...):
        
        context['user'] = context["user"].id # "pack" the user into an ID
        
        # Some witchcraft to pass the settings obj into the task:
        if context['settings'] is settings:
            context['settings'] = True
        
        tasks.send_password_reset_email.delay(
            subject_template_name, email_template_name,
            context, from_email, to_email, html_email_template_name)
