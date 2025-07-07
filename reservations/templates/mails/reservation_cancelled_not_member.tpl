{% extends "mail_templated/base.tpl" %}

{% block subject %}
    Bellettrie - One of your reservations was cancelled, because your membership period has ended.
{% endblock %}

{% block body %}
    Dear {{member.name}},

    You had a reservation on the following book:

    {{ item.display_code}}: {{item.work.title}}

    Since you are no longer a member, this reservation was cancelled.

    If you have any questions, feel free to contact us by replying to this email.

    Kind regards,

    The board of Bellettrie

    Ps. This email was sent automatically
{% endblock %}

{% block html %}
    Dear {{member.name}}, <br />
    <br />
You had a reservation on the following book: <br />

    <table>
        <tr><th>Book Code</th><th>Title</th></tr>
        {%for lending in lendings %}
            <tr><td>{{item.display_code}}</td><td>{{item.work.title}} </td></tr>
        {% endfor %}
    </table>
    Since you are no longer a member, this reservation was cancelled.<br>
    <br>
    If you have any questions, feel free to contact us by replying to this email. <br />
    <br />

    Kind regards, <br />
    <br />
    The board of Bellettrie<br />
    <br />
    Ps. This email was sent automatically
{% endblock %}
