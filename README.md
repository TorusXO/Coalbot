# Coalbot Aiogram 3.4.1
Telegram bot repo for tracking coal changes in shisha cafe
This bot makes coal changes for a set of tables from 2 to 11, before that the cafe had tables 1-10 so I changed that to this.

Bot will count 15 mins for each active shisha on each table, there may be as many shishas as you want on a table. 
Also bot counts total amount of shishas and how many changes of coals were made for specific shisha. That way shisha master alwyas know where he needs to change coals and when.
Color of the emojis is changing according to the time, first it will change from green to yellow after 8 mins, then to red when 2 mins remaining, so that is easy to visually find which shishas are expiring their time for a change. 

There is several commands that can be done by / in telegram:
/reset_count - resets count and gives you the amount of shishas deleted today in the bot(that's how counting of total shishas made)
/minus - -1 from total shishas count in case you added and deleted unneccasary shisha.


This repo is ready to be hosted on Amvera for example. 
Bot works for multiple users and the amount of tables as well as their names could be edited in the files. 
