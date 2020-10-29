{% extends "mail_templated/base.tpl" %}

{% block subject %}
Bellettrie - Some of your books are late
{% endblock %}

{% block body %}
Dear {{member.name}},



{%if has_late%}
You have items that are late. Please hand them in as soon as possible. This will limit the fine.
{%for lending in lendings %}
{{lending.item.display_code}}:  {{lending.item.publication.title}} -- Due: {{lending.end_date}}
{% endfor %}
{%if has_nearly_late %}
    You also have items that are nearly late:

{%endif%}
{%else%}
    You have items that are nearly late:

{%endif %}
{%for lending in almost_late %}
    {{lending.item.display_code}}:  {{lending.item.publication.title}} -- Due: {{lending.end_date}}
{% endfor %}
If you have any questions regarding your lendings, feel free to contact us by replying to this email.

Kind regards,

The board of Bellettrie

Ps. This email was sent automatically
!!
{% endblock %}

{% block html %}
Dear {{member.name}}, <br />
<br />

 {%if has_late%}
You have items that are late. Please hand them in as soon as possible. This will limit the fine.<br />
 <br />
 <table>
 <tr><th>Book Code</th><th>Title</th><th>Due Date<th></th></tr>
{%for lending in lendings %}
 <tr><td>{{lending.item.display_code}}</td><td>{{lending.item.publication.title}} </td><td>{{lending.end_date}}</td></tr>
{% endfor %}
</table>
{%if has_nearly_late %}
    You also have items that are nearly late:<br />

{%endif%}
{%else%}
    You have items that are nearly late. Please hand them in before their deadline expires. <br />
{%endif%}
 <table>
 <tr><th>Book Code</th><th>Title</th><th>Due Date<th></th></tr>
{%for lending in almost_late %}
 <tr><td>{{lending.item.display_code}}</td><td>{{lending.item.publication.title}} </td><td>{{lending.end_date}}</td></tr>
{% endfor %}
</table>
 If you have any questions regarding your lendings, feel free to contact us by replying to this email. <br />
 <br />

Kind regards, <br />
 <br />
The board of Bellettrie<br />
<br />
Ps. This email was sent automatically
{% endblock %}