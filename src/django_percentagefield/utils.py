import sys
from decimal import Decimal

from django.utils import formats


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
