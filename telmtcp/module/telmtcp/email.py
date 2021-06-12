from django.template.loader import get_template

def render_email(context, template_path):
    template = get_template(template_path)
    html = template.render(context)
    return html
