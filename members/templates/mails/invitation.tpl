{% extends "mail_templated/base.tpl" %}

{% block subject %}
Hello {{ user.name }}
{% endblock %}

{% block body %}
Yo yo,

Your invitation code is: {{member.invitation_code}}
{% endblock %}

{% block html %}
Yo yo,<br><br>

Your invitation code is: {{member.invitation_code}}
{% endblock %}