## How to use the base templates

To extend base.html in your mail templates:

1. you must define the `header` and `title` blocks. They often have the same content
2. recipient must be passed and must be an email
3. you must define the `body` block

### Example

{% extends 'base.html'%}

    {% block title %}
        Account Verification
    {% endblock %}

    {% block title %}
        Account Verification
    {% endblock%}

    {% block body %}
    <p>
    Lorem ipsum dolor sit amet
    </p>
    {% endblock %}
