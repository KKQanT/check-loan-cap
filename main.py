from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv


app = FastAPI()

origins = [
  "http://localhost:3000",
  "https://atadia-lending-lab.xyz"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

@app.get('/')

#def get_total_optin():
#  MIN_ID = os.getenv('MIN_ID_TO_CAL_CAP')
#  return {'ss':MIN_ID}

def get_total_optin():
  MIN_ID = os.getenv('MIN_ID_TO_CAL_CAP')
  MIN_ID = int(MIN_ID)

  DB_HOST = os.getenv('DB_HOST')
  DB_USER = os.getenv('DB_USER')
  DB_PASSWORD = os.getenv('DB_PASSWORD')
  
  MAX_PEOPLE = os.getenv('MAX_PEOPLE')
  MAX_PEOPLE = int(MAX_PEOPLE)
  is_exceed = False

  connection = mysql.connector.connect(
  host=DB_HOST,
  user=DB_USER,
  password=DB_PASSWORD
  )

  cursor = connection.cursor()
  cursor.execute(f"SELECT * FROM lendSubmitV1 WHERE id >= {MIN_ID}")
  records = cursor.fetchall()
  df = pd.DataFrame(data=records, columns=[c[0] for c in cursor.description])

  df = df.drop_duplicates(subset=['discordId'], keep='last')
  df = df.drop_duplicates(subset=['walletAddress'], keep='last').reset_index(drop=True)

  sol_to_send = {
    1:np.nan,
    2:1,
    3:2,
    4:3,
    5:4
  }

  df['solLend'] = df['loanPackage'].map(sol_to_send)
  df = pd.DataFrame(df[df['solLend'].isna() == False]).reset_index(drop=True)
  
  num_opt_in = int(len(df))

  if num_opt_in > MAX_PEOPLE:
    is_exceed = True
  else:
    is_exceed = False

  return {'numOptIn':num_opt_in, "isExceed":is_exceed}