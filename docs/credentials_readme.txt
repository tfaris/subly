OAuth credentials are encrypted using keyczar.

To create your own credentials, follow these steps:

1. Install the python-keyczar package:
   
   pip install python-keyczar
   
2. Create a directory at project root named 'keyset'. Run the python shell and run the following:
   
   >>> import keyczar
   >>> from keyczar import keyczart
   >>> keyczart.main(['create','--location=keyset','--purpose=crypt','--name=subly'])
   
   This creates a 'meta' file in the 'keyset' directory.
   
3. Run this command to add a key.

   >>> keyczart.main(['addkey','--location=keyset' ,'--status=primary'])
   