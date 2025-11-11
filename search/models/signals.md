# Search Updating Through Signals
The search functionality has its own separate text indexing. In order to keep this index up to date, Django's Signalling functionality is used.
This allows the search-module to "react" to save- and delete- actions on the models in the works module.

Although there are eight different signal-receiver functions within the signals.py file, they all do basically the same thing:
They look which works are related to this change, and then update these works.
In the case of deletes, the updates are delayed, so the entities are removed by the time the update is finished.