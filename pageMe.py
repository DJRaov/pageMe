#
#REQUIRES GNURADIO AND GR-MIXALOT TO BE INSTALLED AND THE SOCKET PDU RUNNING
#

import os
import disnake
import socket
import sys

from disnake.ext import commands

TOKEN = 'insert your own'
description = "A Discord to POCSAG/FLEX bridge written in Python with RF side made in GNURadio."
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 52001)
intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

capcode = '0123456' #6- and 7-digit capcodes are supported (no leading zeros)
bot = commands.Bot(command_prefix=commands.when_mentioned_or("&"), description=description, intents=intents)

sock.connect(server_address)

@bot.event
async def on_ready():
    print (f'{bot.user} has connected to Discord.')


@bot.slash_command(description="Page me!", pass_context=True)
async def page(inter, msg: str):
    await inter.response.send_message("Paging...") #Send confirmation that we received the message
    msg_page = (f'{inter.author.name}#{inter.author.discriminator}\n{msg}') #The message to be paged
    pdu = (f'pocsag1200 0 159200000 alpha {capcode} {msg_page.encode("ascii").hex()}') #PDU for gr-mixalot (it suckysucky)
    print (f'{msg_page} \n \n  GRC PDU: {pdu} \n -------------- \n') #Print the debug info (message and PDU)
    sock.sendall(bytes(pdu, encoding='ascii')) #Shove it all down the TCPipe

bot.run(TOKEN)
