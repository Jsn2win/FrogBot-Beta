import discord.utils

async def validRole(message, msg):
    try:
        id = int(msg.replace("<@&", "").replace(">", ""))
        role = discord.utils.get(message.guild.roles, id=id)
        return role
    except ValueError: #the user did not mention. test if he stated it & its valid
        name = msg
        try:
            role = discord.utils.get(message.guild.roles, name=name)
            return role
        except AttributeError: #The user did not mention or specify a valid role
            return False #Prevent further action
    return False #Unknown error