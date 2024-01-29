# panelview_running_file
An example of how to get the current running file name in a PanelView via MSG

A few people in forums have asked if it was possible to get the current running
MER file name in a PanelView Plus back to the PLC so that it can be displayed
on the HMI.  The consensus was no but I thought there must be a way.  The file name
is stored in the registry on the PanelView.  This example will read the registry
entry, then return the path to the file, including the name.

This can be useful for situations when multiple files are saved on the PanelView.
When you upload via the Transfer Utility, you don't know which one is the file
running.  It's not a perfect solution, it relies on someone configuring the
PanelView to run an application at startup.  If the PanelView is not configured
to run an application at startup, this will not work.  Also, the user could shut
an application and load a different one.  It would still report the application
configured to run at startup.

The only thing you should have to adjust is the path.  My example was making the
request from a 5069-L320ERM, which has a path of 3, IPAddress.  The example was
written with Studio5000 LogixDesigner v34.