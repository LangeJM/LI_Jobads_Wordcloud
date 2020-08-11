'''module to start postgrsql engine and write list objects to postgres table specified y user'''
#import json
import ssl
import tkinter as tk
from tkinter import filedialog
import msvcrt
from psycopg2 import connect, sql



def postgres_config():
    '''get postgres configuration data
    '''
    print('\nPlease select the file with the database configuration. Press "Enter" to continue.')
    msvcrt.getch()

    fp_db_config = ''
    while fp_db_config == '':
        root = tk.Tk()
        root.withdraw()
        fp_db_config = filedialog.askopenfilename()

    with open(fp_db_config) as file:
        db_config = [x.strip().split('=', 1) for x in file]


    return db_config

def setup_postgres_engine(db_config):
    '''Retrieve path to json file with db details'''

    engine = connect(
        database=db_config[0][1],
        user=db_config[1][1],
        password=db_config[2][1],
        host=db_config[3][1],
        port=db_config[4][1]
        )
    cur = engine.cursor()

    return engine, cur

def ignore_ssl_cert():
    '''Ignore SSL certificate errors'''
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

#from TwitterAPI import TwitterAPI

def create_postgres_table(cur, engine):
    '''get table name by user input'''
    table_name = 'lijobads'
    table_path = 'postgres.dbo.' + str(table_name)

    cur.execute('''
                
        CREATE TABLE IF NOT EXISTS {} (

        id                  SERIAL PRIMARY KEY,
        
        job_url             TEXT UNIQUE,
        jobad_role          TEXT NOT NULL,
        jobad_company       TEXT NOT NULL,
        jobad_location      TEXT NOT NULL,
        jobad_published     DATE ,
        jobad_retrieved     TIMESTAMP NOT NULL,
        job_details         TEXT NOT NULL,
        job_skills          TEXT NOT NULL,
        job_categories      TEXT NOT NULL,
        search_keywords     TEXT NOT NULL,
        search_geo          TEXT NOT NULL

    );

    '''.format(table_name))
    engine.commit()


    print('\nData base table "' + str(table_path) + '" has been created.')

    return table_name


def write_to_postgres(
        cur, engine, table_name, job_url, jobad_role, jobad_company,
        jobad_location, jobad_published, jobad_retrieved, job_details,
        job_skills, job_categories, search_keywords, search_geo):
    '''write content to postgres db
    '''

    cur.execute(
        sql.SQL('''
                INSERT INTO {} (job_url, jobad_role, jobad_company, jobad_location, jobad_published,
                jobad_retrieved, job_details, job_skills, job_categories, search_keywords, search_geo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                ''').format(sql.Identifier(table_name)), [job_url, jobad_role, jobad_company,
                                                          jobad_location, jobad_published,
                                                          jobad_retrieved, job_details,
                                                          job_skills, job_categories,
                                                          search_keywords, search_geo])

    engine.commit()
    print('\nJob ad "' + str(jobad_role) + ' at ' + str(jobad_company) +
          '" has been saved to the data base.')
