#
#REQUIRES GNURADIO AND GR-MIXALOT TO BE INSTALLED AND THE SOCKET PDU RUNNING
#

import os, disnake, socket, sys, signal
from disnake.ext import commands

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True


#------------------------------------------ Variables --------------------------------------------
bot_token = 'add your own'
bot_description = "A Discord to POCSAG/FLEX bridge written in Python with RF side made in GNURadio."
capcode = 123456 #6- and 7-digit capcodes are supported (no leading zeros)
admin_userid = add_your_own
freq = 159.2 #in MHz
mode = 'pocsag1200'
ip = 'localhost' #remove ' if using an IP
port = 52001
#-------------------------------------------------------------------------------------------------

bot = commands.Bot(command_prefix=commands.when_mentioned_or("&"), description=bot_description, intents=intents)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (ip, port)

try:
    sock.connect(server_address)
except ConnectionRefusedError:
    print ("Flowchart refused the connection! Check whether or not it is running. Exiting!")
    sys.exit(1)
    
@bot.event
async def on_ready():
    print (f'Connected as {bot.user}!')
    user = await bot.fetch_user(admin_userid)
    await user.send("Bot ready!")


@bot.slash_command(description="Page me!", pass_context=True)
async def page(inter, msg: str):
    await inter.response.send_message("Paging...") #Send confirmation that we received the message
    msg_page = (f'{inter.author.name}#{inter.author.discriminator}\n{msg}') #The message to be paged
    pdu = (f'{mode} 0 {freq*1000000} alpha {capcode} {msg_page.encode("ascii").hex()}') #PDU for gr-mixalot (it suckysucky)
    print (f'{msg_page}\n\nGRC PDU: {pdu}\n--------------\n') #Print the debug info (message and PDU)
    sock.sendall(bytes(pdu, encoding='ascii')) #Shove it all down the TCPipe as ASCII

@bot.slash_command(description="Configure the bot and other stuff")
async def config(inter, freq: float, mode: str, ):
    if (inter.author.id == admin_userid): #Is the bot owner executing the command?
        await inter.response.send_message(f"New frequency: {freq}MHz, new mode: {mode}")
    else:
        await inter.response.send_message("You do not have the rights to configure the bot.")

@bot.slash_command(description="Shut the bot down")
async def shutdown(inter):
    if (inter.author.id == admin_userid): #Is the bot owner executing the command?
        await inter.response.send_message("Shutting down...")
        sock.shutdown(1)
        sock.close()
        sys.exit()
    else:
        await inter.response.send_message("You do not have the rights to shut the bot down.")

bot.run(bot_token)
