Privacy Notice for **MockBot**

Please note that this bot is **not** a service provided by or affiliated with Discord Inc.
This notice is only affecting the isolated service "MockBot", please consult the *Discord Privacy notice* independently.

__**Implicite data collection**__
During *normal* operation, this service will not persist any user information.

All data required for operation (e.g. message content), is only stored in volatile memory during the execution of the requested command.
After completion of the command, no user data remains in memory.

The service does not log command invocation*.

**__Explicit data Collection__**
The service does not store any user information (as of 22nd November 2026). Previously stored data (in relation to the removed `automock` feature) have been deleted.

__Server Settings__
Settings changed with the `/settings` command are stored into a database linked to the guild the command was invoked on.
These settings do not contain any user information.

__Deletion of Data__
All stored server settings will be deleted when the bot is removed from a guild, without possibility for recovery.

*__**Error case**__
In case a command causes an unexpected error, a so called `Stack-Trace` is dumped into log files.
This stack trace does log the invocation of a command, but does not contain any personal information.


This privacy policy itself may be updated or extended without prior warning or notification.
