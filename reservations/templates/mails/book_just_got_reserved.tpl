{% extends "mail_templated/base.tpl" %}

{% block subject %}
    Bellettrie - One of the books you have lent was just reserved
{% endblock %}

{% block body %}
    Dear {{member.name}},

    A book you have lent has just been reserved. This means you can no longer extend it.

    {{ item.display_code}}: {{item.publication.title}}

    If you have any questions, feel free to contact us by replying to this email.

    Kind regards,

    The board of Bellettrie

    Ps. This email was sent automatically
{% endblock %}

{% block html %}
    Dear {{member.name}}, <br />
    <br />
    A book you have lent has just been reserved. This means you can no longer extend it. <br />

    <table>
        <tr><th>Book Code</th><th>Title</th></tr>
        {%for lending in lendings %}
            <tr><td>{{item.display_code}}</td><td>{{item.publication.title}} </td></tr>
        {% endfor %}
    </table>

    If you have any questions, feel free to contact us by replying to this email. <br />
    <br />

    Kind regards, <br />
    <br />
    The board of Bellettrie<br />
    <br />
    Ps. This email was sent automatically
{% endblock %}