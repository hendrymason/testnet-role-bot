## discord
import discord
import os
## google sheets authentication / credentials
import gspread
from keep_alive import keep_alive
gc = gspread.service_account(filename='service-key.json')

## sheet mgmt
response_sheet_id = '1lcYwfA9lbMvpRmc7oI2W9hyKsl8E87JX0fPAfAXQkKc' 
spartan_sheet = gc.open_by_key(response_sheet_id).worksheet("Spartans")
architect_sheet = gc.open_by_key(response_sheet_id).worksheet("Architects")
citizen_sheet = gc.open_by_key(response_sheet_id).worksheet("Citizens")

## column values for each sheet
username_column = 3
spartanUsers = spartan_sheet.col_values(username_column)
architectUsers = architect_sheet.col_values(username_column)
citizenUsers = citizen_sheet.col_values(username_column)

# citizens key, spartan key, architect key -> [citizens], [spartans], [architects]
formUsers = {}
formUsers['Spartans'] = spartanUsers[1:]
formUsers['Architects'] = architectUsers[1:]
formUsers['Citizens'] = citizenUsers[1:]

## discord client
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
## global vars for bot use
bronzeAge_roles = ['Spartans', 'Architects', 'Citizens']
channel_id = 941166997851484220
## Bot output responses
wrong_reaction_notification = "Please react with the role you signed up for in the Bronze Age Testnet"
spartanForm = "https://forms.gle/e8kVFi6bRMLsGPif9"
architectForm = "https://forms.gle/xMX8e2Kyydrb45qT6"
citizenForm = "https://forms.gle/6xAnRmQ8XMdPMakR9"
signUpDict = {}
signUpIntro = "It doesn't appear you are signed up for this role in the Bronze Age Testnet."
signUpDict['Architects'] = signUpIntro + "\n\n" + "To be rewarded for building on Quai Network as a ARCHITECT: " + architectForm
signUpDict['Citizens'] = signUpIntro + "\n" + "To be rewarded for participating in transactions and other testnet events as a CITIZEN: " + citizenForm
completeSignUp = "Signup for the Spartan Role has been maxxed out. Please wait until next testnet to claim your SPARTAN role. In the meantime, Sign up for the ARCHITECT role or CITIZEN Role during this testnet to earn $QUAI." + "\n\n" + "To be rewarded for building on Quai Network as a ARCHITECT: " + architectForm + "\n\n" + "To be rewarded for participating in transactions and other testnet events as a CITIZEN: " + citizenForm
signUpDict['Spartans'] = completeSignUp

## Bot
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    print("Citizens in form: " + str(formUsers['Citizens']))
    print("Spartans in form: " + str(formUsers['Spartans']))
    print("Architects in form: " + str(formUsers['Architects']))

@client.event
async def on_raw_reaction_add(payload):
  message_id = payload.message_id
  if message_id == 941462842513707089:
    
    guild_id = payload.guild_id
    guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)
    channel = client.get_channel(channel_id)

    if payload.emoji.name == 'spartan':
      role = discord.utils.get(guild.roles, name='Spartans')
    elif payload.emoji.name == 'architect':
       role = discord.utils.get(guild.roles, name='Architects')
    elif payload.emoji.name == 'citizen':
      role = discord.utils.get(guild.roles, name='Citizens')
    else:
      role = None
      await channel.send(content=wrong_reaction_notification, delete_after=30.00, mention_author=True)
    
    if role is not None:
      member = await guild.fetch_member(payload.user_id)
      member_username = str(member)
      if member is not None:
        ## update sheet values for new sign ups 
        updatedUsers = gc.open_by_key(response_sheet_id).worksheet(role.name).col_values(username_column)
        formUsers[role.name] = updatedUsers[1:]
        ## check for users in dict values
        inList = False
        for member_list in formUsers.values():
          if member_username in member_list:
            inList = True
        if inList == False:
          print(member_username)
          print(formUsers.values())
          await channel.send(content=f"{member.mention}" + completeSignUp, delete_after=45.00, mention_author=True)
        ## when user inList for selected role
        elif role.name in bronzeAge_roles and member_username in formUsers[role.name]:
          already_assigned = False
          ## check if user already has role to assign or not
          for r in member.roles:
            if r.name == role.name:
              already_assigned = True
          if already_assigned == False:
            await member.add_roles(role)
            print("added role: " + str(role.name))
          await channel.send(content=f"Congratulations {member.mention}! you've been added as part of the "+ str(role.name).upper() + " for the Bronze Age Testnet!", delete_after=30.00, mention_author=True)
        ## when user inList, but not in role specific list
        elif role.name in bronzeAge_roles and member_username not in formUsers[role.name]:
          await channel.send(content=f"Sorry {member.mention}" + signUpDict[role.name], delete_after=30.00, mention_author=True)
        ## handler for unfamiliar events
        else:
          await channel.send(content="Not sure what you did there.", delete_after=30.00, mention_author=True)
          print("User did something unexpected")



@client.event
async def on_raw_reaction_remove(payload):
  message_id = payload.message_id
  if message_id == 941462842513707089:
    
    guild_id = payload.guild_id
    guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)

    if payload.emoji.name == 'spartan':
      role = discord.utils.get(guild.roles, name='Spartans')
    elif payload.emoji.name == 'architect':
       role = discord.utils.get(guild.roles, name='Architects')
    elif payload.emoji.name == 'citizen':
      role = discord.utils.get(guild.roles, name='Citizens')
    else:
      role = None
    
    if role is not None:
      member = await guild.fetch_member(payload.user_id)
      if member is not None:
            for r in member.roles:
              if r.name == role.name:
                await member.remove_roles(role)
          
keep_alive()
client.run(os.getenv('TOKEN'))

## TODO
# build a handler for removing reactions
# build a handler for assigning roles to users that already have the role
# ensure that the bot is constantly checking sheets when reaction given
