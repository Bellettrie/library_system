{% extends "mail_templated/base.tpl" %}

{% block subject %}
Invitation to use Bellettrie's Catalog System
{% endblock %}

{% block body %}
Dear {{member.name}},

As a member of Bellettrie, you can have an account on the catalog system. This will allow you, among other things, to extend and reserve books.

To create an account, follow the link below, and use this to create an account. After that, you can log in and start using the system.

{{BASE_URL}}members/signup/{{member.pk}}?key={{member.invitation_code}}

If you have any questions regarding this process, feel free to contact us by replying to this email.

Kind regards,

The board of Bellettrie

Ps. This email was sent automatically
!!
{% endblock %}

{% block html %}
Dear {{member.name}},<br />
<br />
As a member of Bellettrie, you can have an account on the catalog system. This will allow you, among other things, to extend and reserve books.<br />
<br />
To create an account, follow the link below, and use this to create an account. After that, you can log in and start using the system.<br />
<br />
<a href="{{BASE_URL}}members/signup/{{member.pk}}?key={{member.invitation_code}}">invitation link</a><br />
<br />
If you have any questions regarding this process, feel free to contact us by replying to this email.<br />
<br />
Kind regards,<br />
<br />
The board of Bellettrie<br />
<br />
Ps. This email was sent automatically{% endblock %}