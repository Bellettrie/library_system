{% extends "mail_templated/base.tpl" %}

{% block subject %}
Bellettrie - Some of your books are late
{% endblock %}

{% block body %}
Dear {{member.name}},

As a member of Bellettrie, you can have an account on the catalog system. This will allow you, among other things, to extend and reserve books.

To create an account, follow the link below, and use this to create an account. After that, you can log in and start using the system.

{%for lending in lendings %}
 {{lending.item.publication.title}}
{% endfor %}

If you have any questions regarding this process, feel free to contact us by replying to this email.

Kind regards,

The board of Bellettrie

Ps. This email was sent automatically
!!
{% endblock %}

{% block html %}
Dear {{member.name}},

You have items that are late. Please hand them in as soon as possible. This will limit the fine.
 <br />
{%for lending in lendings %}
 {{lending.item.publication.title}} <br />
{% endfor %}
 <br />
If you have any questions regarding this process, feel free to contact us by replying to this email. <br />
 <br />

Kind regards, <br />
 <br />
The board of Bellettrie


{% endblock %}