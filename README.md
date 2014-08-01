WIRL
====

Writing Implementation Resource Locator


The two main apps are located in the controllers/ directory:

- wirl.py - allows the user to specify a resource ID and download appropriate items

- wirledit.py - allows editing of the resource database


The Wirl and WirlEditor apps are built on web2py. To use this code:

(1) Download and install web2py: http://www.web2py.com/init/default/download.

(2) Navigate to the web2py/applications/ directory and clone the Wirl repository from GitHub:

git clone https://github.com/silnrsi/wirl.

To run using the web2py controller:

(3) Run the web2py application (eg, on Windows: C:/web2py/web2py.exe).

(4) Choose a password to get admin/debugging capabilities.

(5) Click "start server". This will start up a welcome page that can be ignored.

To try the Wirl applications:

(6) In a browser, go to http://127.0.0.1:8000/wirl/wirl/findResource.

		To download a resource, go to http://127.0.0.1:8000/wirl/wirl/findResource?resid=<resource>.
		Eg, http://127.0.0.1:8000/wirl/wirl/findResource?resid=Andika.
		
(7) To see the resource database, go to: http://127.0.0.1:8000/wirl/wirlEdit/editor.