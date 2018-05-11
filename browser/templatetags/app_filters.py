from django.template.defaulttags import register
import json
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name
from pygments import highlight
from django.utils.safestring import mark_safe
import textwrap
from picklefield.fields import PickledObjectField


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


@register.filter(name='markdown')
def convert_to_markdown(string):
    response = "\n".join(textwrap.wrap(string, width=100))

    # Get the Pygments formatter
    formatter = get_formatter_by_name('html', style='colorful')

    # Highlight the data
    response = highlight(response, get_lexer_by_name('md'), formatter)

    # Get the stylesheet
    style = "<style>" + formatter.get_style_defs() + "</style><br>"

    # Safe the output
    return mark_safe(style + response)




@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter('find_param_type')
def find_param_type(parameters, key):

    for parameter in parameters:

        if key == parameter.name:
            return parameter.type


@register.filter('json_dumps')
def json_dumps(dictionary):
    return json.dumps(dictionary)


@register.filter(is_safe=True)
def js(obj):
    return mark_safe(json.dumps(obj))



@register.filter(name='is_pickle_rick')
def is_pickle_rick(field):
  return type(field) == dict


@register.filter(name='strcat')
def strcat(val1, val2):
  return "{}{}".format(str(val1), str(val2))

@register.filter(name='request_url_cat')
def request_url_cat(host, base_path, request_path):
    """
    Combine the host path with base path and request path. The request path
    :param base_url:
    :type base_url:
    :param request_url:
    :type request_url:
    :return: 
    :rtype: 
    """

    return "{}{}{}".format(str(host), str(base_path), str(request_path)[1:])
