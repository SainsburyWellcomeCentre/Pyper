You can alter the behaviour of the ROIs by overwriting the callback methods
in a subclass of the GuiTraker class (see API).

Clicking on **Add custom** will popup a simple code editor with a template class inheriting from the GuiTracker class.
The methods you will most likely want to overwrite are displayed in this class.
First edit the name of the class. The new name will appear in the menu under **Add custom** once you select
*file* > *export* and this new method will be automatically e.
Then, edit the methods to give them the desired behaviour.
Finally, select export as described above to add the new tracking method to the menu.
In future versions, an option will allow you to save and reload these classes and the previously defined ones will
automatically appear in the menu.

This also allows you to easily alter the callbacks triggered by the different types of ROIs.
Again, please refer to the :doc:`api` to know which methods you may want to overwrite.