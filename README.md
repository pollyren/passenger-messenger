# passenger-messenger

Prerequisites: You must [create a service account](https://docs.gspread.org/en/latest/oauth2.html), save the service account json file as service_account.json in the same directory as assign_cars.py, and share the Google Sheet with the service account email.

**Usage: python assign_cars.py [-d \<day of week>] [-s \<worksheet name>] [-b \<workbook name>]**

By default, day of week is the next day, worksheet name is "crew_attendance" and workbook name is "attendance". 
