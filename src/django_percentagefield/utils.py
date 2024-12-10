import re
import sys
from decimal import Decimal
from typing import Any

from django.db import models
from django.utils import formats
from django.utils.safestring import mark_safe, SafeString


def is_unfold_admin_decimal_field_widget(obj: any) -> bool:
    if 'unfold.widgets' in sys.modules:
        unfold_admin_decimal_field_widget = getattr(sys.modules['unfold.widgets'], 'UnfoldAdminDecimalFieldWidget')
        return obj == unfold_admin_decimal_field_widget
    else:
        return False


def format_percentage(value: Decimal | None, include_percentage_symbol: bool = False) -> str:
    if value is None:
        return ''

    percentage: str = formats.number_format(value.normalize(), use_l10n=True)
    return f'{percentage}%' if include_percentage_symbol else percentage


def format_message(message: any, obj: models.Model) -> SafeString | Any:
    def adjust_percentage(match: re.Match) -> str:
        value: str = match.group(0)[:-1]  # Extract the percentage value and remove the '%' sign
        value: str = value.replace(',', '.')  # Replace ',' with '.' for decimal conversion
        value: Decimal = Decimal(value)

        # If the percentage is less than 1, multiply by 100
        if value < 1:
            value *= 100

        # Return the adjusted percentage as a string with '%' sign
        return f'{value.normalize()}%'

    try:
        obj_str: str = str(obj)
        adjusted_obj_str: str = re.sub(pattern=r'\b\d+(?:[.|,]\d+)?%', repl=adjust_percentage, string=obj_str)
        adjusted_message: str = message.replace(obj_str, adjusted_obj_str)

        return mark_safe(adjusted_message)
    except Exception:
        return message
