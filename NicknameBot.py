import discord
from discord.ext import commands, tasks
import os
import asyncio
import json
import re
#Setup these enviorment names with the variable name being the name in the quotes
BOT_ID = os.environ.get('BOT_ID')

client = commands.Bot(command_prefix="+")
with open('EmojiToCountry.json', encoding='utf8') as json_file:
    data = json.load(json_file)

with open('CountryStateCodes.json', encoding='utf8') as Country_State:
    Country_State_JSON = json.load(Country_State)

Country_State.close()
json_file.close()

SpecialCharacterPattern = re.compile(r"^[_A-z0-9]*((-|\s)*[_A-z0-9])*$")


@client.event
async def on_ready():
    print('Bot is ready.')

@client.event
async def on_member_join(member):
    print(f'{member.display_name} just joined')
    for channel in member.guild.channels:
        if channel.name == "general":
            await channel.send(f'Please type `+nickname (Username)` to change your username')

@client.command(aliases=["nick","Nick","Nickname"])
async def nickname(ctx, *, nickname):
    if len(nickname) <= 20 and SpecialCharacterPattern.match(nickname):
        get_flag = await ctx.send(f"Okay {nickname}, react to this message with your country's flag.")
        def check(reaction,user):
            return user == ctx.message.author and user != client.user and reaction.emoji in data.keys()

        try:
            reaction, user = await client.wait_for("reaction_add",timeout=60.0,check=check)
        except asyncio.TimeoutError:
            await get_flag.delete()
            await ctx.send(f"{ctx.message.author.display_name} you did not respond with a valid flag in time, terminating command.")

        USER_COUNTRY_ID = data[reaction.emoji]
        USER_COUNTRY_INFO = Country_State_JSON[USER_COUNTRY_ID]
        USER_COUNTRY_NAME = USER_COUNTRY_INFO["name"]
        DIVISIONS = USER_COUNTRY_INFO['divisions']
        KEYS = sorted(list(DIVISIONS))
        EMBEDS = []
        await get_flag.delete()
        State_Info = await ctx.send(f'You stated that you live in {USER_COUNTRY_NAME}, please select a State/City/Province. Here are some valid codes.')
        if len(DIVISIONS) > 25:
            NumEmbeds = len(DIVISIONS)//25
            for i in range(NumEmbeds):
                embedVar = discord.Embed(title=f"{USER_COUNTRY_NAME}", description="Key ~ (State Code):(State Name)", color=0x00b8ff)
                for j in range(25*i,25+25*i):
                    embedVar.add_field(name=KEYS[j].replace(f'{USER_COUNTRY_ID}-',''), value=DIVISIONS[KEYS[j]], inline=True)
                embeded_item = await ctx.send(embed=embedVar)
                EMBEDS.append(embeded_item)
            embedVar = discord.Embed(title=f"{USER_COUNTRY_NAME}", description="Key ~ (State Code):(State Name)", color=0x00b8ff)
            for j in range(25*NumEmbeds,len(USER_COUNTRY_INFO["divisions"])):
                embedVar.add_field(name=KEYS[j].replace(f'{USER_COUNTRY_ID}-',''), value=DIVISIONS[KEYS[j]], inline=True)
            embeded_item = await ctx.send(embed=embedVar)
            EMBEDS.append(embeded_item)
        else:
            embedVar = discord.Embed(title=f"{USER_COUNTRY_NAME}", description="Key ~ (State Code):(State Name)", color=0x00b8ff)
            for item in DIVISIONS:
                embedVar.add_field(name=item.replace(f'{USER_COUNTRY_ID}-',''), value=DIVISIONS[item], inline=True)
            await ctx.send(embed=embedVar)


        try:
            StateSelect = await client.wait_for("message", timeout=60.0, check=lambda message: message.author == ctx.author)
            if len(StateSelect.content) <= 3 and USER_COUNTRY_ID+"-"+StateSelect.content in DIVISIONS.keys():
                Complete_Nickname = f"{nickname} | {StateSelect.content} | {USER_COUNTRY_ID}"
                await ctx.message.author.edit(nick=Complete_Nickname)
                await ctx.send(f"Sucess! Your nickname has successfully been changed to {Complete_Nickname}.")
            else:
                await ctx.send(f"Command was unsuccessful, make sure the Code matches the ones offered exactly.")
            for embed_item in EMBEDS:
                await embed_item.delete()
            await State_Info.delete()
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.message.author.display_name} you did not respond with a valid Code in time, terminating command.")
            for embed_item in EMBEDS:
                await embed_item.delete()
            await State_Info.delete()
    else:
        await ctx.send("Your nickname is too long, please keep it within 20 letters. Special Characters (Excluding Spaces) are not permitted.")


@nickname.error
async def nickname_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Use this command to change your nickname, type `{ctx.prefix}nickname (Username)`')


@tasks.loop(seconds=20.0)
async def NicknameCollection():
    async for guild in client.fetch_guilds():
        for member in guild.members:
            print(member.display_name)

@NicknameCollection.before_loop
async def wait_for_NicknameCollection():
    await client.wait_until_ready()

NicknameCollection.start()
client.run(BOT_ID)