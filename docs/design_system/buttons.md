# Buttons

Unless really impossible to do otherwise, use `<button>` instead of `<input type="submit">`

## Colors
We have four colors that we use:
- default. This is reached by not specifying a color, in which case it will use the 'neutral' colors from the color scheme.
- primary. This color is used to indicate to the user that this button is part of a primary process. Primary buttons should not cause state-changes to the system.
- success. Persisting: This color is used to indicate that this button will save the user's task, ending a flow of actions in the process. 
- error. Deletion: Use the error color from daisy-UI to indicate that the user's actions will remove a thing from the system (or perform an action that can be thought of as deletion, such as removing someone from a committee).

Note that we have 'secondary' colored buttons as well on the site. Secondary has the same meaning as primary, but is used to have two buttons next to each other with different colors.
Secondary should only be used if the same 'area of buttons' has primary as well.

## Joins
When buttons are next to each other, use  join/join-item from daisy UI to merge them together. Alternatively, add some margin to the buttons.