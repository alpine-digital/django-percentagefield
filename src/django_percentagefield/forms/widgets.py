import sys
from decimal import Decimal
from types import ModuleType

from django.contrib.admin.widgets import AdminIntegerFieldWidget

from django_percentagefield.utils import format_percentage

__all__ = [
    'PercentageWidget',
]


class PercentageWidget(AdminIntegerFieldWidget):
    input_type = 'text'
    template_name = 'django_percentagefield/forms/widgets/percentage.html'

    def __init__(self, attrs: dict[str, any] | None = None):
        if attrs and attrs.get('is_unfold_admin_widget', False):
            # check if unfold.widgets module exists
            unfold_widgets_module: ModuleType | None = sys.modules.get('unfold.widgets', None)
            if unfold_widgets_module:
                input_classes: list[str] | None = getattr(unfold_widgets_module, 'INPUT_CLASSES')
                if input_classes:
                    if 'w-full' in input_classes:
                        # replace `w-full` with `max-w-full` to accommodate the `%` p-tag after the field
                        input_classes[input_classes.index('w-full')] = 'max-w-full'
                    # add the extra Unfold input classes
                    attrs = {'class': ' '.join(input_classes), **(attrs or {})}

        super().__init__(attrs=attrs)

    def format_value(self, value: Decimal | str | None) -> str:
        if value is None:
            return ''

        if isinstance(value, str):
            return value

        return format_percentage(value=value)
