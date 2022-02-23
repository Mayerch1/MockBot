Privacy Notice for **MockBot**

Please note that this bot is **not** a service provided by or affiliated with Discord Inc.
This notice is only affecting the isolated service "MockBot", please consult the *Discord Privacy notice* independently.

__**Implicite data collection**__
During *normal* operation, this service will not persist any user information.

All data required for operation (e.g. message content), is only stored in volatile memory during the execution of the requested command.
After completion of the command, no user data remains in memory.

The service does not log command invocation*.

**__Explicit data Collection__**
Some commands will store user data after an explicit invocation by the user. These functionalities are (as of 16th December 2021) 
* automock
* automock excemption

__Automock__
Once a user was added to the *automock* list, the ID of the user will be stored into a database linked to the guild the command was invoked on.
Upon removal of the *automock* entry, the database entry is removed. It is not possible to see which users have been *automocked* in the past.

__Automock Excemption__
If a user was *automocked* and *opts-out* of the feature to prevent being *automocked*, his ID will be stored into a blacklist which is linked towards the 
guild the *automock* was activated on.
Upon deactivation of the excemption, the database entry is removed.

__Deletion of Data__
All collected user information
* User ID
* linked guild ID
will be deleted when the bot is removed from a guild, without possibility for recovery.

*__**Error case**__
In case a command causes an unexpected error, a so called `Stack-Trace` is dumped into log files.
This stack trace does log the invocation of a command, but does not contain any personal information.


This privacy policy itself may be updated or extended without prior warning or notification.
