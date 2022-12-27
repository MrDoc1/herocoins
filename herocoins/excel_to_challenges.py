import pandas as pd
from herocoin_challenge_SQL import connect
from datetime import datetime as dt
import json 
filepath = "/Users/yd/Downloads/herocoinchallenges.xlsx" #excel file containing challenges
challengename = "Challenge Name"
rewardname = "Hero Coin Rewards"
rankname = "Difficulty Rank"
itemname = "Item"
quantityname = "Item Qty"
descriptionname = "Description"
max_items = 6
insert = False

def read_excel_to_dataframe(file_path:str) -> pd.DataFrame:
  df = pd.read_excel(file_path, sheet_name='Sheet1', header=0, index_col=None, usecols=None)
  return df

def row_to_dict(row):
  if pd.isnull(row[challengename]):
    return None
  r = {"challenge_name": row[challengename], "reward":int(row[rewardname]), "rank":row[rankname], "description": row[descriptionname]}
  requirements = {}
  for i in range(max_items):
    if pd.isnull(row[itemname + f" {i+1}"]):
      break
    requirements[row[itemname + f" {i+1}"].strip()] = int(row[quantityname + f" {i+1}"])
  r["requirements"] = requirements
  return r

def get_challenges(filepath:str) -> list:
  t = dt.utcnow()
  df = read_excel_to_dataframe(filepath)
  r = [(x['challenge_name'],json.dumps(x),t) for x in list(df.apply(row_to_dict,axis=1)) if x is not None]
  return r

def insert_challenges_into_table(filepath:str) -> None:
  challenges = get_challenges(filepath)
  db,cursor = connect()
  tuples = ','.join(cursor.mogrify("(%s,%s,%s)",x).decode('utf-8') for x in challenges)
  sql = "INSERT INTO challenges VALUES " + tuples + " ON CONFLICT (name) DO UPDATE SET (info, modified) = (EXCLUDED.info, EXCLUDED.modified)"
  cursor.execute(sql)
  cursor.close()
  db.commit()
  db.close()

if __name__ == "__main__":
  if insert:
    insert_challenges_into_table(filepath=filepath)
    print("Updated Challenges.")