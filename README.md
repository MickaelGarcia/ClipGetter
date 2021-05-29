# ClipGetter
Get twitch clip list and download tool from discord logs

This application require Python 3, requests and qtpy with your favorite Qt library.

This tool have to be use with discord .txt logs, i recomand you to use [Discord Chat Exporter](https://github.com/Tyrrrz/DiscordChatExporter)


## Usage :

When You a .txt  file of discord logs, go to Files => Set Discord logs and locate your .txt file.
In the end of process, you will have a list of clips, with all usfull data. 
Right click on any selected clips to open them in your browser, or to add them to de download queue

When the clips that you wanted are all added to the queue, simply click to Execute button, then select a location.
This will create a directory for each streamer in the list, and download all clips renamed by date, Cliper and clip name.

You can also use Files => Download All, pick up a discord log, and a download location. 
That will download all clips found in the .txt file with the same rules than previous

### Beware : 

After used  'Set Discord Logs', if you use it again, you will lost all clips in 'Clips Found' tab !


## To do:

* BugFix : Possibility to add the same clip multiple time in download queue with multiple log files

* Feature : Load and save Clip Found tab to increase the efficiency on massive amount of items and to have only unused clips
* Feature : Drag and drop discord logs option
* Feature : Reaming options to get more or less info in the clips name files
* Feature : Quality download options
