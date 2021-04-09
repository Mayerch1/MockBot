# MockBot

This is the MockBot for discord.


Key features:
* mock other users with the spongebob meme

In contrast to other solutions, this bot uses the correct image for the meme. It does NOT only send plain text when using the commands.


This bot is a subset of the bigger [ModBot](https://top.gg/bot/602236567574020133)

![example image](readme_example.png)



## Some users cannot use the bot?

Make sure the user has the permission to perform `slash`-commands.
This is a recently introduced discord permission, and can control the access to bot commands.


## Setup

You can use `/mock manage` to put users onto an auto-mock list. The bot will perform the `/mock` command automatically on every message they send.

If you accidently set all admins of a server onto that list, you can kick and re-invite the bot, as it deletes all settings when it gets kicked. 

## Commands


|Commands||
|---|---|
|```mock last```  | take the last message and create the spongebob mocking meme  | 
|```mock user <user>``` | take the last message of `<user>` and create the spongebob mocking meme |
| ```mock manage [compl.]```  | manage the list of auto-mocked users (admin only)




## MockManage

When putting a user onto the auto-mock, the bot will automatically apply the 'mock' command to his messages.

NOTE: this can prevent the user from using other commands, depending on which bot is faster in processing.

```
*mock manage <mode>
	available modes
	• list - list all users on the mock-list
	• add <user> -add the given user to the list
	• remove <user> - remove the given user from the list
```




### Github
https://github.com/Mayerch1/MockBot