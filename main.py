import os, sys
import time
import string, random
import io
#----Basics----#
from claptcha import Claptcha
#----Captcha---#
from utils import readdata, Hashify
from utils.verifyrole import validRole
from assets import emojis

#----Utilities-#
import discord
import discord.utils
from discord.ext import commands
from discord.ext.commands import has_permissions, has_guild_permissions
#----Discord--#
from flask import Flask
import threading
#--Keep Alive-#



DataJson = readdata.jsonload(r'Storage/data.json')
default_prefix = "dev.fm."
async def getPrefix(bot, message):
    return DataJson['prefix'].get(str(message.guild.id), default_prefix)

client = commands.Bot(command_prefix=getPrefix, case_insensitive=True)
client.remove_command('help')

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    async def checkerror(messag, errtxt):
        await messag.edit(embed = discord.Embed(title = errtxt, color = 0xFF0000))
        sys.exit()
    #Starting checks
    try:
        with open('restart', 'r+') as file:
            channelid = int(file.readline().strip())
            messageid = int(file.readline().strip())
        os.remove('restart')
        channel = client.get_channel(channelid)
        msg = await channel.fetch_message(messageid)
        loading = client.get_emoji(761611345241571339)
        await msg.edit(embed=discord.Embed(title=f"{loading} Starting verification checks...", color = 0xAAAAAA))
        if Hashify.BLAKE3(r"utils/Hashify.py") == "e43a35240df9940c40ff38bfd1f6986ff5f21672516d0ed0b555520d8c0d2687": await msg.edit(embed=discord.Embed(title=f"{loading} Hashify.py verified", color = 0xAAAAAA))
        else: await checkerror(msg, "Uh oh, it seems like Hashify is corrupted!!")
        if Hashify.BLAKE3(r"Storage/words.txt") == "4edacf9391117558587242ac10b5dc5e9920f511d05939d70ec1cc637b617f1c": await msg.edit(embed=discord.Embed(title=f"{loading} Words.txt verified", color = 0xAAAAAA))
        else: await checkerror(msg, "Uh oh, it seems like the word list is corrupted!!")
          
        await msg.edit(embed=discord.Embed(title=f"Bot restarted!", color = 0x00FF00))
          
        
        #----------------------------------------------------------------------------------------------------------DO THIS-----------------------------------------------------------------------------------------------#
    except FileNotFoundError:
        pass
    
#--------------------------------------HELP MESSAGES---------------------------------------------#
@client.command()
async def help(message):
    embed = discord.Embed(title="Help", description="All commands")
    embed.add_field(name="**`Help`**", value="Shows this help message", inline=True)
    embed.add_field(name="**`Info`**", value="Shows info about the bot", inline=True)
    embed.add_field(name="**`Settings`**", value="Configure the bot", inline=True)
    await message.channel.send(embed=embed)

@client.command()
async def info(message):
    embed = discord.Embed(title="Bot info")
    embed.set_author(name=message.author, icon_url=message.author.avatar_url)
    embed.add_field(name = 'API', value= "`Discord.py`", inline = True)
    embed.add_field(name = 'API Version', value = f"`{discord.__version__}`", inline = True)

    embed.add_field(name = 'Ping', value = f"`{round(client.latency*1000,1)} ms`", inline = True)
    embed.add_field(name = 'Python version', value = f"`{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}`", inline = True)
    embed.add_field(name = 'Support server', value = f"[`discord.gg/Zp2Ts3A`](https://discord.gg/Zp2Ts3A)", inline = True)
    embed.set_footer(text=u"❤️Made with love❤️")
    await message.channel.send(embed=embed)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.guild == None:
        return None

    if message.content == f"<@!{client.user.id}>":
        await message.channel.send(embed=discord.Embed(title="Frog", description=f"My prefix is: **`{DataJson['prefix'].get(str(message.guild.id), default_prefix)}`**"))

    await client.process_commands(message)

#--------------------------------------CONFIGURATION---------------------------------------------#

@client.command()
@has_guild_permissions(manage_guild=True)
async def setup(message):
    try:
        DataJson['setup'][str(message.guild.id)]
        embed=discord.Embed(title="Error", description="Already set up. Please use settings to configure", color=0xFF0000)
        await message.channel.send(embed=embed)
        return
    except KeyError:
        pass
    author = message.author
    def authorcheck(m): return m.author == author

    embed = discord.Embed(title="Setup", description="Please state the role users will get after verification")
    await message.channel.send(embed=embed)
    msg = await client.wait_for('message', check=authorcheck, timeout = 300)

    if not await validRole(message, msg.content):
        embed = discord.Embed(title="Error", description="Invalid role specified", color=0xFF0000)
        await message.channel.send(embed=embed)
        return False
    role = await validRole(message, msg.content)
    #save for future use
    gid = str(message.guild.id)
    DataJson['Verirole'][gid] = role.id
    DataJson['setup'][gid] = "True"
    DataJson['verification']['reaction'][gid] = "False"
    DataJson['verification']['word'][gid] = "False"
    DataJson['verification']['captcha'][gid] = "False"
    
    readdata.jsonsave(r'Storage/data.json', DataJson)
    print(DataJson)

    #current end state
    embed=discord.Embed(title="Success!", description="Successfully set up")
    await message.channel.send(embed=embed)
    
@setup.error
async def setup_error(message, error):
    embedVar = discord.Embed(title="Error", description=str(error),
                             color=0xFF0000)
    await message.channel.send(embed=embedVar)

@client.command()
@has_guild_permissions(manage_guild=True)
async def settings(message, arg1 = None, arg2 = None, arg3 = None):
    try: #test if user ran setup
        DataJson['setup'][str(message.guild.id)]
    except KeyError:
        embed=discord.Embed(title="Error", description="Please run setup first", color=0xFF0000)
        await message.channel.send(embed=embed)
        return

    #settings help command

    if (not arg1 and not arg2) or (arg1.lower() == "help"):
        embed=discord.Embed(title="Settings help", description="**`help`**: Show this help message\n**`role`**: Configure the verification role\n**`prefix`**: Configure the server's prefix for the bot\n**`levels`**: Configure the verification system")
        await message.channel.send(embed=embed)

    if arg1 and not arg2:
        if arg1.lower() == "role":
            embed = discord.Embed(title="Verification role", description='**Description**: The role users will get after they verify\n**Usage**: `settings role @Role`\n *Note*: If a role has more than 1 word, and you are not mentioning it, wrap it in double quotes\nEx: `settings role "two words"`')
            await message.channel.send(embed=embed)
        elif arg1.lower() == "prefix":
            embed = discord.Embed(title="Server prefix", description='**Description**: The prefix for the bot this server will use\n **Usage**: `settings prefix [prefix]`')
            await message.channel.send(embed=embed)
        elif arg1.lower() == "levels":
            embed = discord.Embed(title="Verification Levels", description='**Description**: What types of verification users will go through\n **Usage**: Please use `settings levels help` to get a comprehensive list of all commands')
            await message.channel.send(embed=embed)
            
    if arg1 and arg2: #settings commands
        #ROLE CONFIGURATION
        if arg1.lower() == "role":
            role = await validRole(message.guild.roles, arg2)
            if not role:
                embed = discord.Embed(title="Error", description="Invalid role specified", color=0xFF0000)
                await message.channel.send(embed=embed)
                return False
            DataJson['Verirole'][str(message.guild.id)] = role.id
            readdata.jsonsave(r'Storage/data.json', DataJson)
            embed = discord.Embed(title="Success!", description="Successfully configured role")
            await message.channel.send(embed=embed)
            
        #PREFIX CONFIGURATION
        elif arg1.lower() == "prefix":
            DataJson['prefix'][str(message.guild.id)] = arg2
            readdata.jsonsave(r'Storage/data.json', DataJson)
            embed = discord.Embed(title="Prefix", description=f"Changed prefix of this server to: **`{arg2}`**")
            await message.channel.send(embed=embed)
            
        #VERIFICATION CONFIGURATION
        elif arg1.lower() == "levels":
            vlev = arg2.lower()
            
            if vlev == "help":
                embed = discord.Embed(title="Commands", description="**`Reaction`**: Users must react to a specific message with a check mark\n**`Word`**: users must say a randomly chosen word\n **`Captcha`**: Users must pass a captcha of distorted letters (*Recommended*)\n***NOTE**: You can have multiple systems active at once (A user must pass a Reaction verification AND a Word verification)*")
                await message.channel.send(embed=embed)
            
            if not arg3:
                return
            stat = arg3.lower()
            
            yes = ['yes', 'true', 'on', 'active']
            no = ['no', 'false', 'off', 'inactive']
            
            if vlev == "reaction":
                if stat in yes:
                    DataJson['verification']['reaction'][str(message.guild.id)] = "True"
                    embed = discord.Embed(title = "Success!", description="Activated Reaction verification")
                if stat in no:
                    DataJson['verification']['reaction'][str(message.guild.id)] = "False"
                    embed = discord.Embed(title = "Success!", description="Deativated Reaction verification")
            
            elif vlev == "word":
                if stat in yes:
                    DataJson['verification']['word'][str(message.guild.id)] = "True"
                    embed = discord.Embed(title = "Success!", description="Activated Word verification")
                if stat in no:
                    DataJson['verification']['word'][str(message.guild.id)] = "False"
                    embed = discord.Embed(title = "Success!", description="Deactivated Word verification")
                    
            elif vlev == "captcha":
                if stat in yes:
                    DataJson['verification']['captcha'][str(message.guild.id)] = "True"
                    embed = discord.Embed(title = "Success!", description="Activated Captcha verification")
                if stat in no:
                    DataJson['verification']['captcha'][str(message.guild.id)] = "False"
                    embed = discord.Embed(title = "Success!", description="Deactivated Captcha verification")
            
            readdata.jsonsave(r'Storage/data.json', DataJson)
            await message.channel.send(embed=embed)
                
                
                
            
@settings.error
async def settings_error(message, error):
    embedVar = discord.Embed(title="Error", description=str(error),
                             color=0xFF0000)
    await message.channel.send(embed=embedVar)
#--------------------------------------VERIFICATION---------------------------------------------#

@client.command()
async def verify(message):
    author = message.author
    try:
        DataJson['setup'][str(message.guild.id)]
    except KeyError:
        embed = discord.Embed(title="Error", description="Bot not set up, please contact a server administrator", color=0xFF0000)
        await message.channel.send(embed=embed)
        return False
    role = discord.utils.get(message.guild.roles, id=DataJson['Verirole'][str(message.guild.id)])
    if role in author.roles:
        embed = discord.Embed(title="Error", description="You are already verified in this server", color=0xFF0000)
        await message.channel.send(embed=embed)
        return False
    try:
        role.id
    except AttributeError:
        embed= discord.Embed(title="Error", description="Specified role not found, please contact a server administrator", color=0xFF0000)
        await message.channel.send(embed=embed)
        return False
    embed = discord.Embed(title="Verification", description="Check your DM's to continue the verification process", color=0x808080)
    await message.channel.send(author.mention, embed=embed)
    channel = await author.create_dm()
    #create captcha
    captchatext = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(6))
    c = Claptcha(captchatext, r'assets/Carlito-Regular.ttf')
    #send captcha
    embed = discord.Embed(title="Verification", description=f"Hello. Welcome to the {message.guild} server.\nPlease complete the following captchas to get access to the server.")
    if DataJson['verification']['captcha'][str(message.guild.id)] == "True":
        image = discord.File(c.bytes[1], filename="captcha.png")
        embed.set_image(url="attachment://captcha.png")
    await channel.send(file=image, embed=embed)

    if DataJson['verification']['captcha'][str(message.guild.id)] == "True":
        msg = await client.wait_for('message', check = lambda m: m.author==author)
        if msg.content != captchatext:
            embed = discord.Embed(title="Captcha Failed", color=0xFF0000)
            await channel.send(embed=embed)
            return

    if DataJson['verification']['reaction'][str(message.guild.id)] == "True":
        check = random.randint(1, 3)
        if check == 1: reaction = u"\u2705"
        if check == 2: reaction = u"\u2611"
        if check == 3: reaction = u"\u2714"
        msgc = 'React to this message with the check emoji'
        msg = await channel.send(msgc)
        emojiarr = [reaction]
        oldemoji = ""
        for c in range(3):
            emoji = random.choice(emojis.emojistring)
            while emoji == oldemoji:
                emoji = random.choice(emojis.emojistring)
            emojiarr += [emoji]
        random.shuffle(emojiarr)
        for e in emojiarr:
            await msg.add_reaction(e)
        def authorCheck(reaction, user): return user == author
        msgreaction, user = await client.wait_for('reaction_add', timeout=180.0, check=authorCheck)
        if not msgreaction.emoji == reaction:
            embed = discord.Embed(title="Captcha Failed", color=0xFF0000)
            await channel.send(embed=embed)
            return
          
    randomWord = random_line('Storage/words.txt')
    def check(message): return message.content == randomWord
    await channel.send(f"Please say the magic word: `{randomWord}`")
    msg = await client.wait_for('message', check = check, timeout = 180.0)      
    
    role = discord.utils.get(message.guild.roles, id=DataJson['Verirole'][str(message.guild.id)])
    await author.add_roles(role)
    await channel.send(f"Congratulations, you have been verified in the {message.guild} server!")
    
#--------------------------------------OWNER COMMANDS---------------------------------------------#

async def __is_owner(message):
    return message.author.id == 722249619177996400

@client.command(pass_context=True)
@commands.check(__is_owner)
async def __restart__(message):
    await message.message.delete()
    for x in range(4):
        await message.channel.send(f"Snipe Protect #{x}", delete_after=0)
    embedvar = discord.Embed(title = "Restarting...")
    messageemb = await message.channel.send(embed=embedvar)
    with open('restart', 'w') as file:
        file.write(str(message.channel.id) + "\n" + str(messageemb.id))
    raise SystemExit

@__restart__.error
async def restart_error(message, error):
    embedvar = discord.Embed(title = "Error", description = str(error), color = 0xFF0000)
    await message.channel.send(embed=embedvar)

#-------------------------------------KEEP ALIVE--------------------------------------------------#
flapp = Flask(__name__)


@flapp.route('/')
def Frogwebalive():
    return "FrogBot"
  
class flaskThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        flapp.run()

  
fthread = flaskThread()
fthread.daemon = True
fthread.start()

#--------------------------------------START------------------------------------------------------#

client.run(os.environ.get('APIToken'))

