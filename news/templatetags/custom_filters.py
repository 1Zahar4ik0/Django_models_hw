from django import template

register = template.Library()


@register.filter
def censor(text):
    for word in ['редиска']:
        text = text.replace(word, '*' * len(word))
    return text
