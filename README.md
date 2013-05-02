# FTMan

_Google Fusiontables Management System_

FTMan is a platform that allows end users to manage their Google Fusiontables in a user-friendly form. It basiclly provides the CRUD operations for any Fusiontable in simple 3 forms (Listing Form - Adding Form - Editing Form).

FTMan allows you to define your fusiontables in an XML file which is located in *backend/tables.xml*. In this file you can:
1. Determine which tables you want to manage with FTMan.
2. Rename the columns names to be more firendly.
3. Define the fields types (Textarea - Date - ForignKey - etc).
4. Define the validation types for each column (Required - Mail - URL - Date - etc)


## Installation

Based on Python 2.7 and Django 1.4.1

### Getting the app up

1. fork the and clone the repo.
2. rename the file *project/settings.py.example* to *project/settings.py* and change the credentials of your Google App. 
3. Start the app using under development via:
```
 ./manage.py runserver 127.0.0.1:8000 --settings=settings
```
4. Login using your gmail account

## Notes

FTMan allows you to manage all fusiontables that you already have access to it.
