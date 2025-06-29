from django.forms import ValidationError
from django.utils.translation import gettext as _

class BlankCharactersValidator:
    """
    Validate that the password doesn't have blank characters.
    """

    def validate(self, password: str, user=None):
        if len(password.split()) > 1:
            raise ValidationError(
                _("This password contains blank characters."),
                code="password_blank_spaces",
            )
        
    def get_help_text(self):
        return _("Your password can't contain blank characters.")
