import discord
import youtube_dl
import json
import asyncio
import os
from mutagen.mp3 import MP3
from subprocess import call

key = ''

class client(discord.Client):
    data = {}
    settings = {}
    directory = ''
    sounds = []
    com = '>'
    queue = []
    creator_id = ''
    
#Background functions
    #Loads user information into self.data
    async def on_ready(self):
        try:
            file = open("data.json")
            self.data = json.load(file)
        except:
            file = open("data.json","w+")
        file.close()
        try:
            file = open("sounds.json")
            self.sounds = json.load(file)
        except:
            file = open("sounds.json","w+")
        file.close()
        print("Setup Complete")

    async def on_logout(self):
        print("logging out")
    async def on_disconnect(self):
        print("disconnected")

#Json writing
    #Writes data to file
    def write_data(self):
        print("writing to data")
        with open("data.json","w") as file:
            json.dump(self.data,file)
            file.close()
    #Writes sound to file
    def write_sounds(self):
        print("writing to sounds")
        with open("sounds.json","w") as file:
            json.dump(self.sounds,file)
            file.close()

#Helping Functions
    #Used to format a given time into ffmpeg needed notation
    def set_time(self,time):
        spot = int(time.find('.'))
        length = int(len(time[:spot]))
        if spot != -1:
            switch = {
                0:'00:00:00'+time,
                1:'00:00:0'+time,
                2:'00:00:'+time,
                3:'00:0'+ time[:1] + ':' + time[1:],
                4:'00:'+ time[:2] + ':' + time[2:],
            }.get(length)
            return switch
        return time

    #Adds a user into our dictionary if they aren't in it
    # "Profile creation" -> used for assigning hotbar sounds
    async def check_user(self,author):
        if str(author.id) not in self.data:
            print("Adding user " + author.name)
            self.data[author.id] = ['']*10
            self.write_data()

    #Checks if given sound is in our sound list -> adds it
    async def check_sound(self,sound):
        if str(sound) not in self.sounds:
            print("Adding sound " + sound)
            self.sounds.append(sound)
            self.write_sounds()

    #Handles incoming messages, checks for command symbol then sends the rest to command_list()
    async def on_message(self,message):
        if message.content == '>stop' and message.author.id == self.creator_id: 
            await self.logout() #Stop bot if '>stop' command is called by creator
        if not message.author.bot and message.content[:len(self.com)] == self.com:
            await self.check_user(message.author)
            vals = message.content[len(self.com):].split(' ')
            await self.command_list(vals[0],vals[1:],message.author,message)

#List of commands in class that handle bot functionality
    async def command_list(self,i,vals,user,msg):
        switch = {
            'add' : self.add_sound,
            'play': self.play_sound,
            'sounds': self.help_sounds,
            'refresh': self.refresh_sounds
        }
        func = switch.get(i,lambda vals,user,msg: print("Invalid command"))
        return await func(vals,user,msg)
        
#~~~~~~~~~~~COMMANDS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Two different features
    # ->Takes (sound_name, spot(0-9)) and adds it to a user's hotbar  
    # ->Takes (sound_name, link, start(optional), end(optional)) to download audio from link and add to sounds folder
    async def add_sound(self,vals,user,msg):
        print("add_sound called")
        print(vals[1])
        if str(vals[1]).isdigit(): #add to user bar
            if int(vals[1]) >= 0 and int(vals[1]) <= 9:
                self.data[str(user.id)][int(vals[1])] = str(vals[0])
                self.write_data()
        else:
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
            if len(vals) > 2: #start and end time passed in
                start = self.set_time(str(vals[2]))
                end = self.set_time(str(vals[3]))
                call(["ffmpeg","-y","-ss", start, "-to", end,"-i", self.directory + name + ".mp3", self.directory + name[:-5] + ".mp3"])
                call(["rm", self.directory + name +".mp3"])
                await self.check_sound(name[:-5])
            else:
                await self.check_sound(name)

    #Bot will join voice channel and play given sound
    async def play_sound(self,vals,user,msg):
        print("play_sound called")
        if user.voice.channel != None:
            if str(vals[0]).isdigit(): #If sound is being chosen from user bar
                vals[0] = self.data[str(user.id)][int(vals[0])]
            length = MP3(self.directory + str(vals[0]) + ".mp3")
            length = length.info.length
            vc = await user.voice.channel.connect()
            vc.play(discord.FFmpegPCMAudio(self.directory + str(vals[0]) + ".mp3"))
            await asyncio.sleep(float(length))
            await vc.disconnect()
        else:
            print("User is not in a channel")

    #Bot will pm user and give a list of sounds in sounds folder
    async def help_sounds(self,vals,user,msg):
        print("help_sound called")
        sound_msg = "Sounds\n```\n"
        for sound in self.sounds:
            sound_msg = sound_msg + sound + '\n'
        sound_msg = sound_msg + "```"
        print(sound_msg)
        await user.send(sound_msg)

    #Bot will search through sounds folder to build a complete list of sounds for sounds.json
    async def refresh_sounds(self,vals,user,msg):
        if str(user.id) == self.creator_id:
            for file in os.listdir(self.directory):
                if file.endswith('.mp3'):
                    await self.check_sound(file[:-4])

c = client()
c.run(key)