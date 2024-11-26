import re
from decimal import Decimal

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.models import Expression
from django.forms import TypedChoiceField, CharField
from django.utils.translation import gettext_lazy as _
from django_percentagefield.forms import PercentageWidget
from django_percentagefield.utils import is_unfold_admin_decimal_field_widget, format_percentage

PERCENTAGE_MAX_DIGITS = getattr(settings, 'PERCENTAGE_MAX_DIGITS', 7)
PERCENTAGE_DECIMAL_PLACES = getattr(settings, 'PERCENTAGE_DECIMAL_PLACES', 4)


# TODO: update the label for the Unfold form field (now not styled properly)
class PercentageField(models.DecimalField):
    """ A field that gets a value between 0 and 1 and displays as a value between 0 and 100"""

    def __init__(self, verbose_name=None, name=None, max_digits=PERCENTAGE_MAX_DIGITS,
                 decimal_places=PERCENTAGE_DECIMAL_PLACES, **kwargs) -> None:
        default_min_value_validator = MinValueValidator(Decimal('0'))
        default_max_value_validator = MaxValueValidator(
            # value gets divided by 100 before reaching the validator, but the message must show ``100`` instead of ``1``
            Decimal('1'),
            message=_('Ensure this value is less than or equal to %(limit_value)s.') % {'limit_value': 100})

        validators = kwargs.get('validators', [])

        if not any(isinstance(validator, MinValueValidator) for validator in validators):
            validators.append(default_min_value_validator)
        if not any(isinstance(validator, MaxValueValidator) for validator in validators):
            validators.append(default_max_value_validator)

        kwargs['validators'] = validators

        super().__init__(verbose_name=verbose_name, name=name, max_digits=max_digits, decimal_places=decimal_places,
                         **kwargs)

    def get_prep_value(self, value: Decimal | None) -> Decimal | None:
        # Ensure the value is stored in decimal form (0.2100 for 21%)
        value: Decimal | None = super().get_prep_value(value)
        return value / 100 if value is not None else None

    def formfield(self, **kwargs) -> CharField | TypedChoiceField:
        # Display percentage in the form field, without decimals
        widget = kwargs.pop('widget', None)

        if widget and is_unfold_admin_decimal_field_widget(widget):
            widget = PercentageWidget(attrs={'is_unfold_admin_widget': True})
        else:
            widget = PercentageWidget()

        defaults = {'form_class': forms.DecimalField, 'widget': widget, 'localize': True,
                    'decimal_places': PERCENTAGE_DECIMAL_PLACES}
        defaults.update(kwargs)

        return super().formfield(**defaults)

    def to_python(self, value: Decimal | None) -> Decimal | None:
        if value is None:
            return value

        if isinstance(value, str):
            # Remove percent sign if present and strip any spaces
            value = re.sub(pattern=r'[%\s]', repl='', string=value)

        try:
            # Convert ``value`` to Decimal, divide by 100 if it’s an integer (or float) between 1 and 100
            value = Decimal(value)
            if value > 1:
                value /= 100
            return value
        except (ValueError, TypeError):
            raise ValidationError(_('Invalid percentage value: %(value)s'), params={'value': value})

    def from_db_value(self, value: Decimal | None, expression: Expression,
                      connection: BaseDatabaseWrapper) -> Decimal | None:
        # Convert stored decimal value to percentage for display, e.g., 0.2100 -> 21
        if value is None:
            return value
        return (value * 100).normalize()

    def value_to_string(self, obj) -> str:
        value = self.value_from_object(obj=obj)
        if value is None:
            return ''
        value *= 100
        value = format_percentage(value=value)
        return value
