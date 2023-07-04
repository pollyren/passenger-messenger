# passenger-messenger

Prerequisites: You must [create a service account](https://docs.gspread.org/en/latest/oauth2.html), save the service account json file as service_account.json in the same directory as assign_cars.py, and share the Google Sheet with the service account email.

The Google Sheet should be formatted as follows:
------------------------------------------------------------------------------------------
|  pickup-location |    name       | Mon | Tue | Wed | Thu | Fri | Sat | Sun | car-spots |
------------------------------------------------------------------------------------------
|     Woodlawn     | first1 last1  |  d  |  d  |  d  |  d  |  x  |  d  |  x  |    12     |
|       Crown      | first2 last2  |  x  |     |  x  |     |  x  |  x  |  x  |           |
|       53rd       | first3 last3  |  d  |  d  |  d  |  d  |  d  |     |     |     5     |
|         .        |       .       |  .  |  .  |  .  |  .  |  .  |  .  |  .  |     .     |
|         .        |       .       |  .  |  .  |  .  |  .  |  .  |  .  |  .  |     .     |
|         .        |       .       |  .  |  .  |  .  |  .  |  .  |  .  |  .  |     .     |
------------------------------------------------------------------------------------------


**Usage: python assign_cars.py [-d \<day of week>] [-s \<worksheet name>] [-b \<workbook name>]**

By default, day of week is the next day, worksheet name is "crew_attendance" and workbook name is "attendance". 
