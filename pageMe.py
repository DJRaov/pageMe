#
#REQUIRES GNURADIO AND GR-MIXALOT TO BE INSTALLED AND THE SOCKET PDU RUNNING
#

import os
import disnake
import socket
import sys

from disnake.ext import commands

TOKEN = 'add your own'
description = "A Discord to POCSAG/FLEX bridge written in Python with RF side made in GNURadio."
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 52001)
intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("&"), description=description, intents=intents)

capcode = '0123456' #6- and 7-digit capcodes are supported (no leading zeros)
admin_userid = add_your_own

sock.connect(server_address)

@bot.event
async def on_ready():
    print (f'{bot.user} has connected to Discord.')
    user = await bot.fetch_user(admin_userid)
    await user.send("Bot ready!")


@bot.slash_command(description="Page me!", pass_context=True)
async def page(inter, msg: str):
    await inter.response.send_message("Paging...") #Send confirmation that we received the message
    msg_page = (f'{inter.author.name}#{inter.author.discriminator}\n{msg}') #The message to be paged
    pdu = (f'pocsag1200 0 159200000 alpha {capcode} {msg_page.encode("ascii").hex()}') #PDU for gr-mixalot (it suckysucky)
    print (f'{msg_page} \n \n  GRC PDU: {pdu} \n -------------- \n') #Print the debug info (message and PDU)
    sock.sendall(bytes(pdu, encoding='ascii')) #Shove it all down the TCPipe

@bot.slash_command(description="Shut the bot down")
async def shutdown(inter):
    wait_pass = 0
    if (inter.author.id == admin_userid):
        await inter.response.send_message("Shutting down...")
        sock.shutdown(1)
        sock.close()
        sys.exit()

bot.run(TOKEN)
