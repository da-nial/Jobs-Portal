from django.utils.translation import ugettext_lazy as _
import re
from django.core.exceptions import ValidationError


class HasNumberAndLetterValidator:
    """
    Validate whether the password is not alphanumeric.
    """

    def validate(self, password, user=None):
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]*$", password):
            raise ValidationError(
                _("This password doesn't have letters and numbers combined."))

    def get_help_text(self):
        return _('Password should contain at least one letter and one number')
