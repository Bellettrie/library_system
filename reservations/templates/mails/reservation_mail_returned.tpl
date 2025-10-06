{% extends "mail_templated/base.tpl" %}

{% block subject %}
    Bellettrie - One of your reserved books was just returned
{% endblock %}

{% block body %}
    Dear {{member.name}},

    A book you have reserved is now returned, and you can come to pick it up.

    {{ item.display_code}}: {{item.work.title}}

    After 14  days this reservation will automatically be cancelled, to give others a chance to read it as well.

    If you have any questions, feel free to contact us by replying to this email.

    Kind regards,

    The board of Bellettrie

    Ps. This email was sent automatically
{% endblock %}

{% block html %}
    Dear {{member.name}}, <br />
    <br />
    A book you have reserved is now returned, and you can come to pick it up. <br />

    <table>
        <tr><th>Book Code</th><th>Title</th></tr>
        {%for lending in lendings %}
            <tr><td>{{item.display_code}}</td><td>{{item.work.title}} </td></tr>
        {% endfor %}
    </table><br>
    After 14  days this reservation will automatically be cancelled, to give others a chance to read it as well.<br>
    <br>
    If you have any questions, feel free to contact us by replying to this email. <br />
    <br />

    Kind regards, <br />
    <br />
    The board of Bellettrie<br />
    <br />
    Ps. This email was sent automatically
{% endblock %}