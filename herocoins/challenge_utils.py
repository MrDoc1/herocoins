from herocoin_challenge_SQL import connect
import discord
from make_herocoin_embed import make_challenge, challenge_progress, complete_embed, incomplete_embed
from excel_to_challenges import insert_challenges_into_table
import random
import json
from datetime import datetime as dt
import datetime
import time
import requests


days = 7 #reset challenge to None if user has not completed the challenge in X days


challenge_cache = {} #for testing purposes
corsa_discord_id = 775256024633573408 #for testing purposes
corsa_uid = 49695069 #for testing purposes
filepath = "/Users/yd/Downloads/herocoinchallenges.xlsx" #excel file containing challenges
hacks = False #for testing purposes
include_self = False #for testing purposes


#get guild roster 
def get_guild_members()->dict:
    # t = time.time()
    r = requests.get('https://thehero.online/api/guild/guildlist')
    guild_members_json = r.json()
    # print(f"{time.time()-t:.2f}")
    return guild_members_json


#get user inventory from AQW Api
def get_user_inventory(uid:int)->dict:
    r = requests.get(f'https://account.aq.com/CharPage/Inventory?ccid={uid}')
    inventory_json = r.json()
    return inventory_json


#Only run this on bot startup. Returns a list of all challenges so you can update the challenge cache. 
def update_challenge_cache() -> dict: 
    db,cursor = connect()
    sql = "SELECT * FROM challenges"
    cursor.execute(sql)
    cache = {x[0]:x[1] for x in list(cursor.fetchall())}
    cursor.close(); db.close()
    return cache


#Gets other players doing the same challenge
def get_other_players(user_id:int, challenge_name:str) -> list:
    sql = "SELECT user_id FROM current_challenge WHERE challenge_name = %s ORDER BY timestamp DESC LIMIT 5"
    db,cursor = connect()
    cursor.execute(sql,(challenge_name,))
    data = cursor.fetchall()
    cursor.close(); db.close()
    if include_self:
        data = [i[0] for i in data]
        return(data)
    data = list(set([i[0] for i in data]) - set([user_id]))
    return(data)


#Get a new challenge and update user's current challenge based on user id
def get_new_challenge(user_id:int, challenge_list:dict) -> tuple[str, discord.Embed]:
    db,cursor = connect()
    sql1 = "SELECT challenge_name FROM completed_challenges WHERE user_id = %s"
    sql2 = "INSERT INTO current_challenge VALUES (%s,%s,%s) ON CONFLICT (user_id) DO UPDATE SET (challenge_name, timestamp) = (EXCLUDED.challenge_name, EXCLUDED.timestamp)"
    cursor.execute(sql1,(user_id,))
    options = list(set(challenge_list.keys()) - set([x for x in cursor.fetchall()])) #gets a challenge the user hasn't already completed
    options.remove("None")
    if len(options) == 0:
        return(None,None) #If they have completed all the challenges then return None
    challenge_name = random.choice(options)
    cursor.execute(sql2,(user_id,challenge_name,dt.utcnow()))
    db.commit()
    cursor.close(); db.close()
    others = get_other_players(user_id=user_id,challenge_name=challenge_name)
    embed = make_challenge(challenge_list[challenge_name], others)
    return(challenge_name,embed)


# Get the current challenge based on discord id
def get_current_challenge(user_id:int) -> str:
    db,cursor = connect()
    sql = "SELECT challenge_name FROM current_challenge WHERE user_id = %s"
    cursor.execute(sql,(user_id,))
    challenge = cursor.fetchall()
    if len(challenge) == 0 or challenge[0][0] == "None":
        return(None)
    cursor.close(); db.close()
    challenge = challenge[0][0]
    return(challenge)


#Get current challenge embed
def get_my_challenge(user_id:int, challenge_list:dict, in_hero:bool=True) -> str | discord.Embed:
    if in_hero:
        try:
            roster = get_guild_members() #gets list of hero members
        except Exception as e:
            return("Hero API currently down. Please try again later.")
        aqw_id = None; unm = None
        for member in roster: #finds AQW uid based on Hero API
            if member["discord_id"] == str(user_id):
                aqw_id = member["id"]
                unm = member["username"]
                break
        if aqw_id is None:
            return("You need to verify as a Hero member. Use `/verify!` in the <#982096210938707998> channel!")
        challenge_name = get_current_challenge(user_id=user_id)
        if challenge_name is None:
            return("You are currently not on any challenges! Use `/newchallenge` to get a new challenge!")
        challenge = challenge_list[challenge_name]
        requirements = {k.lower():v for k,v in challenge["requirements"].items()}
        ltoc = {k.lower():k for k in challenge["requirements"]}
        inventory = None
        try:
            inventory = {item["strName"].lower():item["intCount"] for item in get_user_inventory(aqw_id)}
        except requests.exceptions.JSONDecodeError:
            return("We are being rate-limited by AE servers. Please try again in 1 minuite.")
        progress = {item:None for item in challenge["requirements"]} #keeps track of unmet requirements
        for item in requirements:
            if item not in inventory:
                progress[ltoc[item]] = f"❌ 0/{int(requirements[item])}"
            elif int(inventory[item]) < int(requirements[item]):
                progress[ltoc[item]] = f"❌ {int(inventory[item])}/{int(requirements[item])}"
            else:
                progress[ltoc[item]] = f"✅ {int(inventory[item])}/{int(requirements[item])}"
        others = get_other_players(user_id=user_id,challenge_name=challenge_name)
        embed = challenge_progress(challenge=challenge,progress=progress, others = others)
        return(embed)
    elif not in_hero:
        #room for expansion incase we include guests
        return "WIP"


#Completes the current challenge and logs to the DB that the current challenge is now None
def complete_challenge(user_id : int, challenge_name: str) -> None:
    sql1 = "INSERT INTO current_challenge VALUES (%s,%s,%s) ON CONFLICT (user_id) DO UPDATE SET (challenge_name, timestamp) = (EXCLUDED.challenge_name, EXCLUDED.timestamp)"
    sql2 = "INSERT INTO completed_challenges VALUES (%s,%s,%s)"
    db,cursor = connect()
    t = dt.utcnow()
    cursor.execute(sql1,(user_id,"None",t)) #set the current challenge to none
    db.commit()
    cursor.execute(sql2,(user_id,challenge_name,t)) #confirm the current challenge is completed
    db.commit()
    cursor.close(); db.close()
    return


def try_turnin(user_id: int, challenge_list:dict, in_hero:bool=True) -> str | tuple[int,discord.Embed]:
    if in_hero:
        try:
            roster = get_guild_members() #gets list of hero members
        except Exception as e:
            return("Hero API currently down. Please try again later.")
        aqw_id = None; unm = None
        for member in roster: #finds AQW uid based on Hero API
            if member["discord_id"] == str(user_id):
                aqw_id = member["id"]
                unm = member["username"]
                break
        if aqw_id is None:
            return("You need to verify as a Hero member. Use `/verify!` in the <#982096210938707998> channel!")
        challenge_name = get_current_challenge(user_id=user_id)
        if challenge_name is None:
            return("You are currently not on any challenges! Use `/newchallenge` to get a new challenge!")
        challenge = challenge_list[challenge_name]
        requirements = {k.lower():v for k,v in challenge["requirements"].items()}
        inventory = None
        try:
            inventory = {item["strName"].lower():item["intCount"] for item in get_user_inventory(aqw_id)}
        except requests.exceptions.JSONDecodeError:
            return("We are being rate-limited by AE servers. Please try again in 1 minuite.")
        complete = True
        incomplete_requirements, incomplete_inventory = {},{} #keeps track of unmet requirements
        for item in requirements:
            if item not in inventory:
                incomplete_requirements[item.capitalize()] = int(requirements[item])
                incomplete_inventory[item.capitalize()] = 0
                complete = False
            elif int(inventory[item]) < int(requirements[item]):
                incomplete_requirements[item.capitalize()] = int(requirements[item])
                incomplete_inventory[item.capitalize()] = int(inventory[item])
                complete = False
        if complete or hacks: #hacks is a manual override for testing puposes
            complete_challenge(user_id=user_id, challenge_name=challenge_name)
            embed = complete_embed(challenge=challenge)
            return (challenge["reward"], embed) #if completed, return the herocoin amount to be added and a success message.
        else: #not complete
            embed = incomplete_embed(challenge, incomplete_requirements, incomplete_inventory)
            return(-1,embed) #return -1 if not completed and a warning embed.
        return
    elif not in_hero:
        #room for expansion incase we include guests
        return "WIP"


#Reset challenges for inactive users
def reset_inactives():
    sql = "UPDATE current_challenge SET challenge_name = %s, timestamp = %s WHERE timestamp < %s;"
    now = dt.utcnow()
    before = now-datetime.timedelta(days=days)
    db,cursor = connect()
    cursor.execute(sql,("None",now,before))
    db.commit()
    cursor.close(); db.close()
    return


if __name__ == "__main__":
    start = time.time()
    insert_challenges_into_table(filepath=filepath) #Reloads the challenge list in the DB 
    print(f"Time to update challenge list: {time.time()-start:.2f}s")
    start = time.time()
    challenge_cache = update_challenge_cache()
    t1 = time.time()
    print(f"Time to update challenge cache: {t1-start:.2f}s")
    name, embed= get_current_challenge(user_id = corsa_discord_id,challenge_list=challenge_cache)
    t2 = time.time()
    print(f"Current Challenge: {name}, Time to get current challenge: {t2-t1:.2f}s")
    name, embed = get_new_challenge(user_id = corsa_discord_id, challenge_list=challenge_cache)
    t3 = time.time()
    print(f"New Random Challenge: {name}, Time to get new challenge: {t3-t2:.2f}s")
    name, embed = get_current_challenge(user_id = corsa_discord_id,challenge_list=challenge_cache)
    t4 = time.time()
    print(f"New Current Challenge: {name}, Time to get new current challenge: {t4-t3:.2f}s")
    for i in range(10):
        print(get_user_inventory(corsa_uid)[0])
    start = time.time()
    reply = try_turnin(corsa_discord_id, challenge_list=challenge_cache)
    if isinstance(reply,str):
        print(reply)
    else:
        i,emb = reply
        print(f"Reward: {i}")
        print(json.dumps(emb.to_dict()))
    t1 = time.time()
    print(f"Time to turnin: {t1-start:.2f}s")
    name, embed = get_new_challenge(user_id = corsa_discord_id, challenge_list=challenge_cache)
    start = time.time()
    reply = get_my_challenge(corsa_discord_id, challenge_list=challenge_cache)
    if isinstance(reply,str):
        print(reply)
    else:
        emb = reply
        print(json.dumps(emb.to_dict()))
    t1 = time.time()
    print(f"Time to get challenge: {t1-start:.2f}s")
    reset_inactives()