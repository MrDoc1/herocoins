import discord
import random


def make_challenge(challenge:dict, others:list) -> discord.Embed:
    e = discord.Embed()
    e.title = challenge["challenge_name"]
    e.color = random.randint(0, 0xFFFFFF)
    e.description = challenge["description"] + "\n\n Gather the items below and __keep them in your inventory__. Ensure you have badges and items shown. You can check your progress using `/mychallenge`. When you are ready to turnin, type `/turnin`. You can re-roll this challenge by typing `/newchallenge`."
    e.set_thumbnail(url=get_embed_thumbnail(challenge["rank"]))
    helpers = "**Potential helpers**: You are the only one on this challenge!"
    if len(others) != 0:
        helpers = ""
        for helper in [f"<@{id}>," for id in others]:
            helpers+=helper
        helpers.rstrip(',')
    e.add_field(name=f"Reward: {challenge['reward']} 🪙",value=helpers,inline=False)
    for item in challenge["requirements"]:
        e.add_field(name=item, value=f"Qty: {challenge['requirements'][item]}", inline=True)
    return e


def challenge_progress(challenge:dict, progress:dict, others:list) -> discord.Embed:
    e = discord.Embed()
    e.title = f"Progress on challenge: {challenge['challenge_name']}"
    e.color = 0xFFD700
    e.description = challenge["description"] + "\n\n Gather the items below and __keep them in your inventory__. Ensure you have badges and items shown. You can check your progress using `/mychallenge`. When you are ready to turnin, type `/turnin`. You can re-roll this challenge by typing `/newchallenge`."
    e.set_thumbnail(url=get_embed_thumbnail(challenge["rank"]))
    helpers = "**Potential helpers**: You are the only one doing this challenge!"
    if len(others) != 0:
        helpers = "**Potential helpers**: "
        for helper in [f"<@{id}>" for id in others]:
            helpers+=helper
        helpers.rstrip(',')
    e.add_field(name=f"Reward: {challenge['reward']} 🪙",value=helpers,inline=False)
    for item in progress:
        e.add_field(name=item, value=progress[item], inline=True)
    return e


def complete_embed(challenge:dict) -> discord.Embed:
    e = discord.Embed()
    e.title = f"🎉Nice Job!🎉 You have completed challenge: {challenge['challenge_name']} ({challenge['rank']} Rank)"
    e.description = f"Hero coins have been deposited into your wallet! Type `/newchallenge` to get a new challenge!"
    e.color = 0x00FF00
    e.set_thumbnail(url="https://cdn.discordapp.com/attachments/998809820935237712/1057111792238739507/image.png")
    e.add_field(name=f"Reward: {challenge['reward']} 🪙 have been desposited.",value="\u200b",inline=False)
    for item in challenge["requirements"]:
        e.add_field(name=item.capitalize(), value=f"Qty: {challenge['requirements'][item]} ✅", inline=True)
    return e


def incomplete_embed(challenge:dict, i_req:dict, i_inv:dict) -> discord.Embed:
    e = discord.Embed()
    e.title = f"You have not met the requirements for challenge: {challenge['challenge_name']}."
    e.description = "Make sure that all the required items are __in your inventory__. Also ensure that you are showing items/badges on your character page. If you would like to see the challenge again, type `/mychallenge`. Below are the missing requirements."
    for item in i_req:
        e.add_field(name=f"{i_req[item]}x {item}",value=f"> You have: {i_inv[item]}x",inline=True)
    e.color = 0xFF0000
    e.set_thumbnail(url="https://cdn.discordapp.com/attachments/998809820935237712/1057119021729841212/image.png")
    return e


def get_embed_thumbnail(rank: str) -> str:
    assert rank in ["S","A","B","C","D"]
    if rank == "S":
        return("https://cdn.discordapp.com/attachments/998809820935237712/1057010487054843944/image.png")
    if rank == "A":
        return("https://cdn.discordapp.com/attachments/998809820935237712/1057010474903949413/image.png")
    if rank == "C":
        return("https://cdn.discordapp.com/attachments/998809820935237712/1057010455916335144/image.png")
    if rank == "B":
        return("https://cdn.discordapp.com/attachments/998809820935237712/1057010433518747658/image.png")
    if rank == "D":
        return("https://cdn.discordapp.com/attachments/998809820935237712/1057010406645829653/image.png")


