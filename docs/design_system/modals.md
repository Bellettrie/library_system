# Modals

We use modals for two reasons:
- Highlights
- Intermediate steps of a flow of actions by the user.

All modals should always have a close button on the top-right, and close by clicking next to it. This behavior is default for our ModalForm component.

## Highlights
A highlight is an on-page view of some information. For instance, we might want to show the tree of a series by clicking an (i) icon next to the name. That way the user can click the (i)--> click a book.


## Steps of a flow
When we want to guide the user through one or more small steps, or we want to confirm their actions, we may choose to show a modal instead of redirecting the user to a separate page.
This is nice for two reasons:
- The user returns to where they came from after the actions
- We have fewer full pages

Note that modals should only ever exist for places that the user does not reasonably want to bookmark/share the link of.


The modal must always contain the information required for the user to do their job. This way we make sure that the modal can be re-used. For example: the modal for borrowing a book should contain the info for the member + book (and also borrowing money and end-date).



## Example code
```jinja
{% extends hx_enabled|yesno:"hx_modal.html,base.html" %}
{% block content %}
    {% component 'modalform.ModalForm' title='Extend Item' path=request.path %}
        {% fill "modal_body" %}

            Extending work: {{ item.publication.title }} <br/>
            Extending for member: {{ member.name }} <br/>
            End date {{ date }} <br/>
        {% endfill %}
        {% fill "modal_submit_button" %}
            <button class="btn btn-success">Extend</button>
        {% endfill %}
    {% endcomponent %}
{% endblock %}
```