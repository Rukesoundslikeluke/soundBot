import discord
import youtube_dl
import json
from subprocess import call

class client(discord.Client):
    data = {}
    settings = {}
    directory = ''
    sounds = {}
    com = ''
    
    #Loads user information into self.data
    async def on_ready(self):
        try:
            file = open("settings.json")
            self.settings = json.load(file)
            self.com = str(settings['com'])
        except:
            self.com = '!'
            file = open("settings.json","w+")
        file.close()
        try:
            file = open("data.json")
            self.data = json.load(file)
            print(type(self.data))
        except:
            file = open("data.json","w+")
        file.close()
        print("Setup Complete")

    #Writes data to file
    def write_data(self):
        print("writing to data")
        with open("data.json","w") as file:
            json.dump(self.data,file)
            file.close()
    def write_settings(self):
        print("writing to settings")
        with open("settings.json","w") as file:
            json.dump(self.settings,file)
            file.close()

    #Adds a user into our dictionary if they aren't in it
    # "Profile creation"
    async def check_user(self,author):
        if str(author.id) not in self.data:
            print("Adding user " + author.name)
            self.data[author.id] = ['']*10
            self.write_data()

    async def on_message(self,message):
        if not message.author.bot and message.content[:len(self.com)] == self.com:
            await self.check_user(message.author)
            vals = message.content[len(self.com):].split(' ')
            if len(vals) > 1:
                self.command_list(vals[0],vals[1:])

    async def on_disconnect(self):
        print("disconnected")

#List of commands in class that handle bot functionality
    def command_list(self,i,vals):
        switch = {
            'add' : self.add_sound,
            'com' : self.change_com,
            'ass' : self.assign_bar
        }
        func = switch.get(i,lambda vals: print("Invalid command"))
        return func(vals)
        
#~~~~~~~~~~~COMMANDS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def add_sound(self,vals):
        print("add_sound called")
        
        name = str(vals[0])
        link = str(vals[1])
        if len(vals) > 2: #start and end time
            name = name + "_temp"
        ydl_opts = {'format': 'bestaudio/best',
                    'outtmpl': self.directory + name + '.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',}]}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        if len(vals) > 2: #start and end time
            start = str(vals[2])
            end = str(vals[3])
            call(["ffmpeg","-y","-ss", start, "-to", end,"-i", self.directory + name + ".mp3", self.directory + name[:-5] + ".mp3"])

    def change_com(self,vals):
        print("change_com called")
        self.com = str(vals[0])
        self.settings['com'] = str(vals[0])
        self.write_settings()

    def assign_bar(self,vals):
        print("assign_bar called")

    

    

c = client()
c.run(key)