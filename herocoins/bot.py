import discord
from discord import app_commands
from config import TOKEN
import challenge_utils as cu
from discord.ext import tasks


challenge_cache = {} #add this


class Bot(discord.Client):

    def __init__(self):
        global challenge_cache
        super().__init__(intents=discord.Intents.all())
        challenge_cache = cu.update_challenge_cache() #add this
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            # This is the Hero Discord ID
            await tree.sync(guild=discord.Object(id=950516939472666684))
            self.synced = True
        print("We have logged in as {}.".format(self.user))


bot = Bot()
tree = app_commands.CommandTree(bot)


#Sets the current quest for inactive challengers to "None" 
@tasks.loop(minutes=30)
async def clear_inactives():
    cu.reset_inactives()


# slash command to see if bot is online
@tree.command(name="ping", description="Check that the bot is active.", guild=discord.Object(id=950516939472666684))
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")
    return


@tree.command(name="newchallenge", description="Get a new herocoin challenge.", guild=discord.Object(id=950516939472666684))
async def newchallenge(interaction: discord.Interaction):
    await interaction.response.defer()
    _, embed = cu.get_new_challenge(user_id=interaction.user.id,challenge_list=challenge_cache)
    await interaction.followup.send(embed=embed)
    return


@tree.command(name="mychallenge", description="Get your current challenge progress.", guild=discord.Object(id=950516939472666684))
async def mychallenge(interaction: discord.Interaction):
    await interaction.response.defer()
    response = cu.get_my_challenge(user_id=interaction.user.id,challenge_list=challenge_cache)
    if isinstance(response,str):
        await interaction.followup.send(content=response)
    else:
        await interaction.followup.send(embed=response)
    return


@tree.command(name="turnin", description="Try to turnin your current challenge", guild=discord.Object(id=950516939472666684))
async def turnin(interaction: discord.Interaction):
    await interaction.response.defer()
    user_id = interaction.user.id
    response = cu.try_turnin(user_id=user_id,challenge_list=challenge_cache)
    if isinstance(response,str):
        await interaction.followup.send(content=response)
    else:
        coins, embed = response
        await interaction.followup.send(embed=embed)
        if coins > 0:
            #ADD coins to user --> TAGG DO THIS
            return
    return


if __name__ == "__main__":
    bot.run(TOKEN)
