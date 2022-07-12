{% extends "mail_templated/base.tpl" %}

{% block subject %}
    Bellettrie - One of your reservations was cancelled, because it was available for too long
{% endblock %}

{% block body %}
    Dear {{member.name}},

    You had a reservation on the following book:

    {{ item.display_code}}: {{item.publication.title}}

    However, this item has been registered as unavailable for lending.
    This may be due to the book being either defective, or missing.

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
            <tr><td>{{item.display_code}}</td><td>{{item.publication.title}} </td></tr>
        {% endfor %}
    </table>
    However, this item has been registered as unavailable for lending.<br>
        This may be due to the book being either defective, or missing.<br>
    <br>
    If you have any questions, feel free to contact us by replying to this email. <br />
    <br />

    Kind regards, <br />
    <br />
    The board of Bellettrie<br />
    <br />
    Ps. This email was sent automatically
{% endblock %}