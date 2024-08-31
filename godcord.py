import os
import json
import string
import discord
import aiohttp
from discord.ext import commands, tasks
import requests
from colorama import Fore
import asyncio
import sys
import random
from flask import Flask
from threading import Thread
import threading
import subprocess
import time
import re
from pystyle import Center, Colorate, Colors
import io
import webbrowser
from bs4 import BeautifulSoup
import datetime
import status_rotator
from pyfiglet import Figlet
from discord import Color, Embed, Member
import colorama
import urllib.parse
import urllib.request

colorama.init()

# Initialize intents and bot
intents = discord.Intents.default()
intents.presences = True
intents.guilds = True
intents.typing = True
intents.dm_messages = True
intents.messages = True
intents.members = True

bot = commands.Bot(description='GodCord', command_prefix='.', self_bot=True, intents=intents)
bot.remove_command('help')

# Global variables
status_task = None
bot.whitelisted_users = {}
bot.antiraid = False
red = Fore.RED
yellow = Fore.YELLOW
green = Fore.GREEN
blue = Fore.BLUE
pretty = "\033[95m"
reset = Fore.RESET

# Helper functions
def load_config(config_file_path):
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)
    return config

def get_time_rn():
    date = datetime.datetime.now()
    hour = date.hour
    minute = date.minute
    second = date.second
    timee = "{:02d}:{:02d}:{:02d}".format(hour, minute, second)
    return timee

time_rn = get_time_rn()

# Load configuration
config_file_path = "config.json"
config = load_config(config_file_path)

# Events
@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.lower().startswith('boosts'):
        await send_boost_count(message.channel, message.guild)
    # Add more command checks here...

    await bot.process_commands(message)

# Commands from both files
@bot.command()
async def boosts(ctx):
    await ctx.send(f"Server Boost Count: {ctx.guild.premium_subscription_count}")

@bot.command()
async def stream(ctx, *, message):
    stream = discord.Streaming(name=message, url="https://twitch.tv/someurl")
    await bot.change_presence(activity=stream)
    await ctx.send(f"Stream created with message: {message}")

@bot.command()
async def math(ctx, *, equation):
    api_endpoint = 'https://api.mathjs.org/v4/'
    response = requests.get(api_endpoint, params={'expr': equation})
    if response.status_code == 200:
        result = response.text
        await ctx.send(f'Result: {result}')
    else:
        await ctx.send('Failed to calculate the equation.')

# More commands
@bot.command()
async def antinuke(ctx, antiraidparameter=None):
    await ctx.message.delete()
    bot.antiraid = False
    if str(antiraidparameter).lower() == 'true' or str(antiraidparameter).lower() == 'on':
        bot.antiraid = True
        await ctx.send('`-` **ANTI-NUKE ENABLED...**')
    elif str(antiraidparameter).lower() == 'false' or str(antiraidparameter).lower() == 'off':
        bot.antiraid = False
        await ctx.send('`-` **ANTI-NUKE DISABLED**')
    else:
        await ctx.send(f'- **[! ERROR] ** `USAGE : {bot.command_prefix}antinuke [true/false]`')

@bot.command(aliases=['wl'])
async def whitelist(ctx, user: discord.Member = None):
    await ctx.message.delete()
    if user is None:
        await ctx.send(f'[ERROR]: USAGE :  {bot.command_prefix}whitelist <user>')
    else:
        if ctx.guild.id not in bot.whitelisted_users.keys():
            bot.whitelisted_users[ctx.guild.id] = {}
        if user.id in bot.whitelisted_users[ctx.guild.id]:
            await ctx.send("- `" + user.name.replace("*", "\*").replace("`", "\`").replace("_", "\_") + "#" + user.discriminator + "`-` ** ALREADY WHITELISTED [!]**")
        else:
            bot.whitelisted_users[ctx.guild.id][user.id] = 0
            await ctx.send("# GodCord\n`-` **WHITELISTED**" + user.name.replace("*", "\*").replace("`", "\`").replace("_", "\_") + "#" + user.discriminator + "`")

@bot.command(aliases=['showwl'])
async def whitelisted(ctx, g=None):
    await ctx.message.delete()
    if g == '-g' or g == '-global':
        whitelist = '# GodCord\n`-`**ALL WHITELISTED USERS:**`\n'
        for key in bot.whitelisted_users:
            for key2 in bot.whitelisted_users[key]:
                user = bot.get_user(key2)
                whitelist += f'• {user.mention} ({user.id}) IN {bot.get_guild(key).name}\n'
        await ctx.send(whitelist)
    else:
        whitelist = f'# GodCord\n`-` **WHITELISTED USERS IN {ctx.guild.name}:**`\n'
        for key in bot.whitelisted_users:
            if key == ctx.guild.id:
                for key2 in bot.whitelisted_users[ctx.guild.id]:
                    user = bot.get_user(key2)
                    whitelist += f'• {user.mention} ({user.id})\n'
        await ctx.send(whitelist)

@bot.command(aliases=['removewl'])
async def unwhitelist(ctx, user: discord.Member = None):
    if user is None:
        await ctx.send("`-` **[ERROR]: SPECIFY THE USER YOU WOULD LIKE TO UNWHITELIST !**`")
    else:
        if ctx.guild.id not in bot.whitelisted_users.keys():
            await ctx.send("- `" + user.name.replace("*", "\*").replace("`", "\`").replace("_", "\_") + "#" + user.discriminator + " IS NOT WHITELISTED`")
            return
        if user.id in bot.whitelisted_users[ctx.guild.id]:
            bot.whitelisted_users[ctx.guild.id].pop(user.id, 0)
            user2 = bot.get_user(user.id)
            await ctx.send('`-` **SUCCESSFULLY UNWHITELISTED**' + user2.name.replace('*', "\*").replace('`', "\`").replace('_', "\_") + '#' + user2.discriminator + '`')

@bot.command(aliases=['clearwl', 'clearwld'])
async def clearwhitelist(ctx):
    await ctx.message.delete()
    bot.whitelisted_users.clear()
    await ctx.send('`-` SUCCESSFULLY CLEARED WHITELIST`')

async def send_boost_count(channel, guild):
    await channel.send(f"# GodCord\n`-` **SERVER NAME** : `{guild.name}` \n`-` **BOOSTS** : `NUMBER - {guild.premium_subscription_count}`")

async def send_selfbotinfo_message(channel):
    await channel.send(f"# GodCord\n`-` **VERSION** : `SELFBOT V2` \n`-` **LANGUAGE** : `PYTHON & JS`\n`-` **NO. OF COMMANDS** : `75`\n`-` **ASKED BY** : `{bot.user.name}`\n`-` **CREATOR** : `ANIKET_72`\n\n`THERE ARE BOTH PREFIX & NON PREFIX COMMANDS`")

async def send_serverinfo_message(channel):
    guild = channel.guild
    await channel.send(f"# GodCord\n`-` **SERVER NAME** : __`{guild.name}`__ \n`-` **SERVER ID** : `{guild.id}`\n`-` **CREATION DATE** : `{channel.guild.created_at}`\n`-` **OWNER** : `{guild.owner_id} / `<@{guild.owner_id}>\n\n`-` **ASKED BY** : `{bot.user.name}`")

async def vouch(channel):
    await channel.send(f"# GodCord\n`-` **SERVER LINK** : {SERVER_LINK}\n`-` **VOUCH FORMAT** : `+rep (user) Legit Got (product) For (price) Thank You`")
    await channel.message.delete()

async def payments(channel):
    await channel.send(f"# GodCord\n__**PAYMENTS**__\n`-` **LTC** :  __`{LTC}`__ \n`-` **ETH** : __`{ETH}`__ \n`-` **BTC** : __`{BTC}`__\n`-` **UPI** :  __`{UPI}`__\n\n`-` **ASKED BY** : `{bot.user.name}`")
    await channel.message.delete()

async def link(channel):
    await channel.send("- `https://discord.gg/KVcxQEedSD`")

@bot.command()
async def massdmfriends(ctx, *, message):
    for user in bot.user.friends:
        try:
            time.sleep(.1)
            await user.send(message)
            time.sleep(.1)
            print(f'{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}MESSAGED :' + Fore.GREEN + f' @{user.name}')
        except:
            print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}COULDN'T MESSAGE @{user.name}")
            await ctx.message.delete()

@bot.command(aliases=["nitrogen"])
async def nitro(ctx):
    try:
        await ctx.message.delete()
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        await ctx.send(f'https://discord.gift/{code}')
        print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN}SUCCESSFULLY SENT NITRO CODE!")
    except Exception as e:
        print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({red}!{gray}) {pretty}{Fore.RED}ERROR: {str(e)}")

@bot.command()
async def hack(ctx, user: discord.Member = None):
    await ctx.message.delete()
    gender = ["Male", "Female", "Trans", "Other", "Retard"]
    age = str(random.randrange(10, 25))
    height = ['4\'6\"', '4\'7\"', '4\'8\"', '4\'9\"', '4\'10\"', '4\'11\"', '5\'0\"', '5\'1\"', '5\'2\"', '5\'3\"', '5\'4\"', '5\'5\"', '5\'6\"', '5\'7\"', '5\'8\"', '5\'9\"', '5\'10\"', '5\'11\"', '6\'0\"', '6\'1\"', '6\'2\"', '6\'3\"', '6\'4\"', '6\'5\"', '6\'6\"', '6\'7\"', '6\'8\"', '6\'9\"', '6\'10\"', '6\'11\"']
    weight = str(random.randrange(60, 300))
    hair_color = ["Black", "Brown", "Blonde", "White", "Gray", "Red"]
    skin_color = ["White", "Pale", "Brown", "Black", "Light-Skin"]
    religion = ["Christian", "Muslim", "Atheist", "Hindu", "Buddhist", "Jewish"]
    sexuality = ["Straight", "Gay", "Homo", "Bi", "Bi-Sexual", "Lesbian", "Pansexual"]
    education = ["High School", "College", "Middle School", "Elementary School", "Pre School", "Retard never went to school LOL"]
    ethnicity = ["White", "African American", "Asian", "Latino", "Latina", "American", "Mexican", "Korean", "Chinese", "Arab", "Italian", "Puerto Rican", "Non-Hispanic", "Russian", "Canadian", "European", "Indian"]
    occupation = ["Retard has no job LOL", "Certified discord retard", "Janitor", "Police Officer", "Teacher", "Cashier", "Clerk", "Waiter", "Waitress", "Grocery Bagger", "Retailer", "Sales-Person", "Artist", "Singer", "Rapper", "Trapper", "Discord Thug", "Gangster", "Discord Packer", "Mechanic", "Carpenter", "Electrician", "Lawyer", "Doctor", "Programmer", "Software Engineer", "Scientist"]
    salary = ["Retard makes no money LOL", "$" + str(random.randrange(0, 1000)), '<$50,000', '<$75,000', "$100,000", "$125,000", "$150,000", "$175,000", "$200,000+"]
    location = ["Retard lives in his mom's basement LOL", "America", "United States", "Europe", "Poland", "Mexico", "Russia", "Pakistan", "India", "Some random third world country", "Canada", "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
    email = ["@gmail.com", "@yahoo.com", "@hotmail.com", "@outlook.com", "@protonmail.com", "@disposablemail.com", "@aol.com", "@edu.com", "@icloud.com", "@gmx.net", "@yandex.com"]
    dob = f'{random.randrange(1, 13)}/{random.randrange(1, 32)}/{random.randrange(1950, 2021)}'
    name = ['James Smith', "Michael Smith", "Robert Smith", "Maria Garcia", "David Smith", "Maria Rodriguez", "Mary Smith", "Maria Hernandez", "Maria Martinez", "James Johnson", "Catherine Smoaks", "Cindi Emerick", "Trudie Peasley", "Josie Dowler", "Jefferey Amon", "Kyung Kernan", "Lola Barreiro", "Barabara Nuss", "Lien Barmore", "Donnell Kuhlmann", "Geoffrey Torre", "Allan Craft", "Elvira Lucien", "Jeanelle Orem", "Shantelle Lige", "Chassidy Reinhardt", "Adam Delange", "Anabel Rini", "Delbert Kruse", "Celeste Baumeister", "Jon Flanary", "Danette Uhler", "Xochitl Parton", "Derek Hetrick", "Chasity Hedge", "Antonia Gonsoulin", "Tod Kinkead", "Chastity Lazar", "Jazmin Aumick", "Janet Slusser", "Junita Cagle", "Stepanie Blandford", "Lang Schaff", "Kaila Bier", "Ezra Battey", "Bart Maddux", "Shiloh Raulston", "Carrie Kimber", "Zack Polite", "Marni Larson", "Justa Spear"]
    phone = f'({random.randrange(0, 10)}{random.randrange(0, 10)}{random.randrange(0, 10)})-{random.randrange(0, 10)}{random.randrange(0, 10)}{random.randrange(0, 10)}-{random.randrange(0, 10)}{random.randrange(0, 10)}{random.randrange(0, 10)}{random.randrange(0, 10)}'
    
    if user is None:
        user = ctx.author
    password = ['password', '123', 'mypasswordispassword', user.name + "iscool123", user.name + "isdaddy", "daddy" + user.name, "ilovediscord", "i<3discord", "furryporn456", "secret", "123456789", "apple49", "redskins32", "princess", "dragon", "password1", "1q2w3e4r", "ilovefurries"]
    
    message = await ctx.send(f"`Hacking {user}...\n`")
    await asyncio.sleep(1)
    await message.edit(content=f"`Hacking {user}...\nHacking into the mainframe...\n`")
    await asyncio.sleep(1)
    await message.edit(content=f"`Hacking {user}...\nHacking into the mainframe...\nCaching data...`")
    await asyncio.sleep(1)
    await message.edit(content=f"`Hacking {user}...\nHacking into the mainframe...\nCaching data...\nCracking SSN information...\n`")
    await asyncio.sleep(1)
    await message.edit(content=f"`Hacking {user}...\nHacking into the mainframe...\nCaching data...\nCracking SSN information...\nBruteforcing love life details...`")
    await asyncio.sleep(1)
    await message.edit(content=f"`Hacking {user}...\nHacking into the mainframe...\nCaching data...\nCracking SSN information...\nBruteforcing love life details...\nFinalizing life-span dox details\n`")
    await asyncio.sleep(1)
    await message.edit(content=f"```Successfully hacked {user}\nName: {random.choice(name)}\nGender: {random.choice(gender)}\nAge: {age}\nHeight: {random.choice(height)}\nWeight: {weight}\nHair Color: {random.choice(hair_color)}\nSkin Color: {random.choice(skin_color)}\nDOB
    {dob}\nLocation: {random.choice(location)}\nPhone: {phone}\nE-Mail: {user.name + random.choice(email)}\nPasswords: {random.choices(password, k=3)}\nOccupation: {random.choice(occupation)}\nAnnual Salary: {random.choice(salary)}\nEthnicity: {random.choice(ethnicity)}\nReligion: {random.choice(religion)}\nSexuality: {random.choice(sexuality)}\nEducation: {random.choice(education)}```")
    else:
        password = ['password', '123', 'mypasswordispassword', user.name + "iscool123", user.name + "isdaddy", "daddy" + user.name, "ilovediscord", "i<3discord", "furryporn456", "secret", "123456789", "apple49", "redskins32", "princess", "dragon", "password1", "1q2w3e4r", "ilovefurries"]
        message = await ctx.send(f"`Hacking {user}...\n`")
        await asyncio.sleep(1)
        await message.edit(content=f"`Hacking {user}...\nHacking into the mainframe...\n`")
        await asyncio.sleep(1)
        await message.edit(content=f"`Hacking {user}...\nHacking into the mainframe...\nCaching data...`")
        await asyncio.sleep(1)
        await message.edit(content=f"`Hacking {user}...\nHacking into the mainframe...\nCaching data...\nCracking SSN information...\n`")
        await asyncio.sleep(1)
        await message.edit(content=f"`Hacking {user}...\nHacking into the mainframe...\nCaching data...\nCracking SSN information...\nBruteforcing love life details...`")
        await asyncio.sleep(1)
        await message.edit(content=f"`Hacking {user}...\nHacking into the mainframe...\nCaching data...\nCracking SSN information...\nBruteforcing love life details...\nFinalizing life-span dox details\n`")
        await asyncio.sleep(1)
        await message.edit(content=f"```Successfully hacked {user}\nName: {random.choice(name)}\nGender: {random.choice(gender)}\nAge: {age}\nHeight: {random.choice(height)}\nWeight: {weight}\nHair Color: {random.choice(hair_color)}\nSkin Color: {random.choice(skin_color)}\nDOB: {dob}\nLocation: {random.choice(location)}\nPhone: {phone}\nE-Mail: {user.name + random.choice(email)}\nPasswords: {random.choices(password, k=3)}\nOccupation: {random.choice(occupation)}\nAnnual Salary: {random.choice(salary)}\nEthnicity: {random.choice(ethnicity)}\nReligion: {random.choice(religion)}\nSexuality: {random.choice(sexuality)}\nEducation: {random.choice(education)}```")
        print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN}SUCCESSFULLY HACKED 😁 ")

@bot.command(aliases=["streaming"])
async def stream(ctx, *, message):
    stream = discord.Streaming(
        name=message,
        url="https://twitch.tv/someurl",
    )
    await bot.change_presence(activity=stream)
    await ctx.send(f"`-` **STREAM CREATED** : `{message}`")
    print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN}STREAM SUCCESSFULLY CREATED✅ ")
    await ctx.message.delete()

@bot.command(aliases=["playing"])
async def play(ctx, *, message):
    game = discord.Game(name=message)
    await bot.change_presence(activity=game)
    await ctx.send(f"`-` **STATUS FOR PLAYZ CREATED** : `{message}`")
    print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN}PLAYING SUCCESSFULLY CREATED✅ ")
    await ctx.message.delete()

@bot.command(aliases=["watch"])
async def watching(ctx, *, message):
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=message,
    ))
    await ctx.send(f"`-` **WATCHING CREATED**: `{message}`")
    print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN}WATCH SUCCESSFULLY CREATED✅ ")
    await ctx.message.delete()

@bot.command(aliases=["listen"])
async def listening(ctx, *, message):
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name=message,
    ))
    await ctx.reply(f"`-` **LISTENING CREATED**: `{message}`")
    print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN}STATUS SUCCESSFULLY CREATED✅ ")
    await ctx.message.delete()

@bot.command(aliases=[
    "stopstreaming", "stopstatus", "stoplistening", "stopplaying",
    "stopwatching"
])
async def stopactivity(ctx):
    await ctx.message.delete()
    await bot.change_presence(activity=None, status=discord.Status.dnd)
    print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({red}!{gray}) {pretty}{Fore.RED}ACTIVITY SUCCESSFULLY STOPPED⚠️ ")

@bot.command()
async def i2c(ctx, amount: str):
    amount = float(amount.replace('₹', ''))
    inr_amount = amount * config.get("I2C_Rate", 1)
    await ctx.reply(f"`-` **AMOUNT IS** : `{inr_amount:.2f}$`")
    print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN}I2C DONE ✅ ")

@bot.command()
async def c2i(ctx, amount: str):
    amount = float(amount.replace('$', ''))
    usd_amount = amount * config.get("C2I_Rate", 1)
    await ctx.reply(f"`-` **AMOUNT IS** : `₹{usd_amount:.2f}`")
    print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN}C2I DONE ✅ ")

@bot.command()
async def loverate(ctx, User: discord.Member = None):
    if User is None:
        await ctx.reply(f"`-` **PROVIDE A USER**")
    else:
        await ctx.reply(
            f"`-` **YOU AND {User.mention} ARE 100% PERFECT FOR EACH OTHER <3**"
        )
        print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN}LOVERATE MEASURED 💖 ")

@bot.command()
async def define(ctx, *, word):
    api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            word_data = data[0]
            word_meanings = word_data['meanings']
            
            meanings_list = []
            for meaning in word_meanings:
                part_of_speech = meaning['partOfSpeech']
                definitions = meaning['definitions']
                
                def_text = f"**{part_of_speech.capitalize()}:**\n"
                for i, definition in enumerate(definitions, start=1):
                    def_text += f"{i}. {definition['definition']}\n"
                    if 'example' in definition:
                        def_text += f"   *Example: {definition['example']}*\n"
                
                meanings_list.append(def_text)
            
            result_text = f"**{word.capitalize()}**\n\n" + '\n'.join(meanings_list)
            await ctx.send(result_text)
        else:
            await ctx.send("`-` **NO DEFINITIONS FOR THAT WORD**")
    else:
        await ctx.send("`-` **FAILED TO RETRIEVE THAT WORD**")

@bot.command()
async def copyserver(ctx, source_guild_id: int, target_guild_id: int):
    source_guild = bot.get_guild(source_guild_id)
    target_guild = bot.get_guild(target_guild_id)

    if not source_guild or not target_guild:
        await ctx.send("`-` **GUILD NOT FOUND**")
        return

    for channel in target_guild.channels:
        try:
            await channel.delete()
            print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN} CHANNEL {channel.name} HAS BEEN DELETED ON THE TARGET GUILD")
            await asyncio.sleep(0)
        except Exception as e:
            print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({red}!{gray}) {pretty}{Fore.RED} ERROR DELETING CHANNEL {channel.name}: {e}")

    for role in target_guild.roles:
        if role.name not in ["here", "@everyone]
            try:
                await role.delete()
                print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN} ROLE {role.name} HAS BEEN DELETED ON THE TARGET GUILD")
                await asyncio.sleep(0)
            except Exception as e:
                print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({red}!{gray}) {pretty}{Fore.RED} ERROR DELETING ROLE {role.name}: {e}")

    roles = sorted(source_guild.roles, key=lambda role: role.position)

    for role in roles:
        try:
            new_role = await target_guild.create_role(
                name=role.name, permissions=role.permissions, 
                color=role.color, hoist=role.hoist, mentionable=role.mentionable
            )
            print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN} ROLE {role.name} HAS BEEN CREATED ON THE TARGET GUILD")
            await asyncio.sleep(0)
        except Exception as e:
            print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({red}!{gray}) {pretty}{Fore.RED} ERROR CREATING ROLE {role.name}: {e}")

    text_channels = sorted(source_guild.text_channels, key=lambda channel: channel.position)
    voice_channels = sorted(source_guild.voice_channels, key=lambda channel: channel.position)
    category_mapping = {}

    for channel in text_channels + voice_channels:
        try:
            if channel.category:
                if channel.category.id not in category_mapping:
                    category_perms = channel.category.overwrites
                    new_category = await target_guild.create_category_channel(
                        name=channel.category.name, overwrites=category_perms
                    )
                    category_mapping[channel.category.id] = new_category

                if isinstance(channel, discord.TextChannel):
                    new_channel = await category_mapping[channel.category.id].create_text_channel(name=channel.name)
                elif isinstance(channel, discord.VoiceChannel):
                    new_channel = await category_mapping[channel.category.id].create_voice_channel(name=channel.name)

                print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN} CHANNEL {channel.name} HAS BEEN CREATED ON THE TARGET GUILD")

                for overwrite in channel.overwrites:
                    if isinstance(overwrite.target, discord.Role):
                        target_role = target_guild.get_role(overwrite.target.id)
                        if target_role:
                            await new_channel.set_permissions(
                                target_role, overwrite=discord.PermissionOverwrite(
                                    allow=overwrite.allow, deny=overwrite.deny
                                )
                            )
                    elif isinstance(overwrite.target, discord.Member):
                        target_member = target_guild.get_member(overwrite.target.id)
                        if target_member:
                            await new_channel.set_permissions(
                                target_member, overwrite=discord.PermissionOverwrite(
                                    allow=overwrite.allow, deny=overwrite.deny
                                )
                            )
                await asyncio.sleep(0)
            else:
                if isinstance(channel, discord.TextChannel):
                    new_channel = await target_guild.create_text_channel(name=channel.name)
                elif isinstance(channel, discord.VoiceChannel):
                    new_channel = await target_guild.create_voice_channel(name=channel.name)
                    
                for overwrite in channel.overwrites:
                    if isinstance(overwrite.target, discord.Role):
                        target_role = target_guild.get_role(overwrite.target.id)
                        if target_role:
                            await new_channel.set_permissions(
                                target_role, overwrite=discord.PermissionOverwrite(
                                    allow=overwrite.allow, deny=overwrite.deny
                                )
                            )
                    elif isinstance(overwrite.target, discord.Member):
                        target_member = target_guild.get_member(overwrite.target.id)
                        if target_member:
                            await new_channel.set_permissions(
                                target_member, overwrite=discord.PermissionOverwrite(
                                    allow=overwrite.allow, deny=overwrite.deny
                                )
                            )
                await asyncio.sleep(0)

                print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN} CHANNEL {channel.name} HAS BEEN CREATED ON THE TARGET GUILD")
        
        except Exception as e:
            print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({red}!{gray}) {pretty}{Fore.RED} ERROR CREATING CHANNEL {channel.name}: {e}")

@bot.command()
async def change_hypesquad(ctx):
    choices = {1: "BRAVERY", 2: "BRILLIANCE", 3: "BALANCED"}
    
    await ctx.send("`[1] Bravery`\n`[2] Brilliance`\n`[3] BalanceD`")
    await ctx.send("`-` **ENTER YOUR CHOICE**: `1,2,3`")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=60)
        choice = int(msg.content)
    except asyncio.TimeoutError:
        await ctx.send("`-` **COMMAND TIMED OUT**")
        return
    except ValueError:
        await ctx.send("`-` **INVALID CHOICE, PLEASE ENTER 1, 2, OR 3**")
        return
    
    headerpost = {'Authorization': config.get("Token")}
    payload = {'house_id': choice}
    
    try:
        await ctx.send(f"`-` **CHANGING HYPESQUAD TO {choices.get(choice, 'Unknown')}**")
        async with aiohttp.ClientSession() as session:
            async with session.post("https://discord.com/api/v8/hypesquad/online", json=payload, headers=headerpost) as response:
                if response.status == 204:
                    await ctx.send("`-` **HYPESQUAD CHANGED SUCCESSFULLY**")
                elif response.status == 401:
                    await ctx.send("`-` **TOKEN INVALID OR EXPIRED**")
                elif response.status == 429:
                    await ctx.send("`-` **PLEASE WAIT FOR 2 MINUTES**")
                else:
                    await ctx.send("`-` **WE CAUGHT AN ERROR**")
    except Exception as e:
        await ctx.send(f"`-` **AN ERROR OCCURRED: {str(e)}`")

@bot.command(aliases=['help'])
async def help_command(ctx):
    message = (
        f"# GodCord \n**</>** **HELP COMMANDS**\n\n"
        "`-` **JOIN'S SERVER** : `+joinsrv <link> <token>`\n"
        "`-` **C2I** : `+c2i 10$`\n"
        "`-` **I2C** : `+i2c ₹100`\n"
        "`-` **SERVER CLONER** : `+copyserver <guild id to copy> <target guild id>`\n"
        "`-` **DEFINE** : `+define <word>`\n"
        "`-` **BACKUP** : `+backup`\n"
        "`-` **ASCI** : `+asci <text>`\n"
        "`-` **avatar** : `+avatar <user>`\n"
        "`-` **CREATE_ROLE** : `+create_role RoleName`\n"
        "`-` **CREATE_CHANNEL** : `+create_channel ChannelName`\n"
        "`-` **GITSEARCH** : `+gitsearch repository_name`\n"
        "`-` **GITUSER** : `+gituser username`\n"
        "`-` **AUTORESPONSE** : `+addar <trigger> , <response> | +removear <trigger name> | +lister`\n"
        "`-` **STATUS ROTATOR** : `+setrotator <msg1> , <msg2>`, `+stoprotator`\n"
        "`-` **BAL** : `+bal LTC_address`\n"
        "`-` **BANNER** : `+banner`\n"
        "`-` **STREAMING** : `+streaming Watchin Movies`\n"
        "`-` **WATCHING** : `+watching Coding`\n"
        "`-` **LISTENING** : `+listening to Music`\n"
        "`-` **PLAYING** : `+playing Games`\n"
        "`-` **STOPACTIVITY** : `+stopactivity`\n"
        "`-` **LINK** : `link`\n"
        "`-` **CONNECT VC** : `+connectvc <vc_id>`\n"
        "`-` **SPAM** : `+spam <no.> <msg>`\n"
        "`-` **HYPE SQUAD CHANGE** : `+change_hypesquad`\n"
        "`-` **NUKE** : `+nukezzz`\n"
        "`-` **IPLOOKUP** : `+iplookup <ip_address>`\n"
        "`-` **LTC PRICE** : `+ltcprice`\n"
        "`-` **MASDMFRIENDS** : `+masdmfriends`\n"
        "`-` **MASSREACT** : `+massreact`\n"
        "`-` **BOOSTS** : `boosts`\n"
        "`-` **LOVERATE** : `+loverate`\n"
        "`-` **HACK** : `+hack`\n"
        "`-` **GAYRATE** : `+gayrate`\n"
        "`-` **SELFBOT** : `Selfbot`\n"
        "`-` **YTSEARCH** : `+ytsearch video_title`\n"
        "`-` **CHECKPROMO** : `+checkpromo promo_links`\n"
        "`-` **WAIFU** : `+waifu`\n"
        "`-` **SEARCH** : `+search <query>`\n"
        "`-` **GUILDICON** : `+guildicon`\n"
        "`-` **CLEAR** : `+purge <no. of msg>`\n"
        "`-` **NITRO** : `+nitro`\n"
        "`-` **SAVE TRANSCRIPT** : `+savetranscript`\n"
        "`-` **MATH** : `+math <equation>`\n"
        "`-` **VOUCH** : `vouch`\n"
        "`-` **NITRO** : `+nitro`\n\n"
        "**・`TYPE [+antinuke_help] AND [+fun_help] FOR THEIR COMMANDS...`**\n\n"
        "**ASKED BY :** `{bot.user.name}`"
    )
    await ctx.send(message)
    print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN}HELP SENT SUCCESSFULLY✅ ")
    await ctx.message.delete()

@bot.command()
async def antinuke_help(ctx):
    message = (
        f"# GodCord\n**</>** __**ANTINUKE HELP CMD**__\n\n"
        "`-` **ANTINUKE ENABLE** : `+antinuke_true`\n"
        "`-` **ANTINUKE DISABLE** : `+antinuke_false`\n"
        "`-` **WHITELIST** : `+whitelist`\n"
        "`-` **UNWHITELIST** : `+unwhitelist`\n"
        "`-` **WHITELISTED** : `+whitelisted`\n"
        "`-` **CLEAR WHITE LIST** : `+clearwl`\n\n"
        "`-` **ASKED BY** : `{bot.user.name}`"
    )
    await ctx.send(message)
    print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN}ANTI-HELP SENT SUCCESSFULLY✅ ")
    await ctx.message.delete()

@bot.command(aliases=['fun_help'])
async def fun(ctx):
    message = (
        f"# GodCord\n**</>** __**FUN CMD. HELP**__\n\n"
        "`-` **CUDDLE** : `+cuddle <user>`\n"
        "`-` **PAT** : `+pat <user>` \n"
        "`-` **KISS** : `+kiss <user>` \n"
        "`-` **SLAP** : `+slap <user>`\n"
        "`-` **HUG** : `+hug <user>`\n"
        "`-` **SMUG** : `+smug <user>`\n"
        "`-` **FEED** : `+feed <user>`\n\n"
        "`-` **ASKED BY** : `{bot.user.name}`"
    )
    await ctx.send(message)
    print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN}FUN-HELP SENT SUCCESSFULLY✅ ")
    await ctx.message.delete()

# More commands
@bot.command(aliases=['pat'])
async def pat_command(ctx, user: discord.Member = None):
    await ctx.message.delete()
    if user is None:
        user = ctx.author
    r = requests.get("https://nekos.life/api/v2/img/pat")
    res = r.json()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(res['url']) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(user.mention, file=discord.File(file, f"godcord_pat.gif"))
    except:
        em = discord.Embed(description=user.mention)
        em.set_image(url=res['url'])
        await ctx.send(embed=em)
        print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN}PATTED ✅ ")

@bot.command(aliases=['kiss'])
async def kiss_command(ctx, user: discord.Member = None):
    await ctx.message.delete()
    if user is None:
        user = ctx.author
    r = requests.get("https://nekos.life/api/v2/img/kiss")
    res = r.json()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(res['url']) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(user.mention, file=discord.File(file, f"godcord_kiss.gif"))
    except:
        em = discord.Embed(description=user.mention)
        em.set_image(url=res['url'])
        await ctx.send(embed=em)
        print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN}KISS SUCCESSFUL✅ ")

@bot.command(aliases=['slap'])
async def slap_command(ctx, user: discord.Member = None):
    await ctx.message.delete()
    if user is None:
        user = ctx.author
    r = requests.get("https://nekos.life/api/v2/img/slap")
    res = r.json()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(res['url']) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(user.mention, file=discord.File(file, f"godcord_slap.gif"))
    except:
        em = discord.Embed(description=user.mention)
        em.set_image(url=res['url'])
        await ctx.send(embed=em)
        print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}{Fore.GREEN}SLAPPING SUCCESSFUL✅ ")

# More fun commands here...

# Running the bot
bot.run(config.get("Token"), bot=False)