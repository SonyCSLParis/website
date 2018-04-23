from django.template.defaulttags import register
import json
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name
from pygments import highlight
from django.utils.safestring import mark_safe


@register.filter(name='json')
def convert_to_json(json_string):
    response = json.dumps(json_string, sort_keys=True, indent=2)

    # Get the Pygments formatter
    formatter = get_formatter_by_name('html', style='colorful')

    # Highlight the data
    response = highlight(response, get_lexer_by_name('json'), formatter)

    # Get the stylesheet
    style = "<style>" + formatter.get_style_defs() + "</style><br>"

    # Safe the output
    return mark_safe(style + response)
