
'''
Main module to scrape and store LinkedIn search results
'''
import msvcrt
import time
import random
#import psycopg2
#import math
#import csv

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import (NoSuchElementException,
                                        TimeoutException,
                                        InvalidArgumentException)

from lijobads_content import get_login
from lijobads_content import login
from lijobads_content import get_search_url
from lijobads_content import joblinks_to_txt
from lijobads_content import joblinks_txt_to_list
from lijobads_content import get_jobad_header
from lijobads_content import get_jobad_content

from lijobads_postgres import postgres_config
from lijobads_postgres import setup_postgres_engine
from lijobads_postgres import ignore_ssl_cert
from lijobads_postgres import create_postgres_table
from lijobads_postgres import write_to_postgres

from lijobads_analysis import read_from_postgres
from lijobads_analysis import clean_content
from lijobads_analysis import tokenize_content
from lijobads_analysis import stopswords
from lijobads_analysis import colormap
from lijobads_analysis import create_and_store_wordcloud


print('''\n\nThis program provides an analysis of LinkedIn job ads. It includes three steps:
    \nAcquire job ad links \nAcquire job ad content and save to database \nProvide analysis of job ads.
    \nIf you already have finished one or more of the steps, you can now select to skip them.''')

usr_selection = None
while usr_selection != b'1' and usr_selection != b'2' and usr_selection != b'3':
    print('''
Press the "1" key to do the complete process
Press the "2" key to skip to the content acquisition. 
    Please note, that you have to provide the file with the previously acquired  job ad links.
Press the "3" key to directly start with analysis.
    ''')
    usr_selection = msvcrt.getch()

print('\nYou chose option: ' + str(usr_selection)[1:])

def start_li_session():
    '''
    start custom browser and navigate to linkedin.com
    '''
    options = Options()
    options.headless = False
    options.page_load_strategy = 'normal'
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
    driver_l = webdriver.Firefox(
        options=options,
        firefox_profile=firefox_profile,
        executable_path='geckodriver.exe'
        )
    driver_l.set_window_position(2000, 0)
    driver_l.maximize_window()
    return driver_l

if usr_selection == (b'1' or b'2'):
    # Start browser session and log in to LinkedIn
    driver = start_li_session()
    usr, pwd = get_login()
    login(driver, usr, pwd)

# get links list object
if usr_selection == b'1':
    search_url, url_keyword, search_keywords, search_geo = get_search_url()
    filename = joblinks_to_txt(driver, search_url, url_keyword, search_keywords, search_geo)

    jobad_urls, filename = joblinks_txt_to_list(filename)
    search_keywords = filename.split('_')[2]
    search_geo = filename.split('_')[3].strip('.txt')

elif usr_selection == b'2':
    jobad_urls, filename = joblinks_txt_to_list()
    search_keywords = filename.split('_')[2]
    search_geo = filename.split('_')[3].strip('.txt')


# Setup and start sql engine
db_config = postgres_config()
engine, cur = setup_postgres_engine(db_config)
ignore_ssl_cert()


if usr_selection == (b'1' or b'2'):
# Create new db table and populate
    table_name = create_postgres_table(cur, engine)

    # Get jobad content and store in postgres db
    COUNTER = 0

    print('This is a list with all job ad urls, before processing:\n'+ str(jobad_urls))

    for i in range(len(jobad_urls)):

        try:
            driver.get(jobad_urls[i])
            time.sleep(random.uniform(1.5, 2))

            jobad_role, jobad_company, jobad_location, jobad_published, jobad_retrieved = \
            get_jobad_header(driver)
            job_details, job_skills, job_categories = get_jobad_content(driver)
            jobad_url = jobad_urls[i]

            write_to_postgres(
                cur,
                engine,
                table_name,
                jobad_url,
                jobad_role,
                jobad_company,
                jobad_location,
                jobad_published,
                jobad_retrieved,
                job_details,
                job_skills,
                job_categories,
                search_keywords,
                search_geo
                )

            COUNTER += 1
        except NoSuchElementException:
            print('\nThe job ad at ' + str(jobad_urls[i]) + ' is not valid and has been skipped.')

        except InvalidArgumentException:
            print('\nThere was a problem prosessing url: ' + str(jobad_urls[i]) + '.')

        except TimeoutException:
            print('\nThere was a timeout when trying to acquire url: ' + str(jobad_urls[i]) + '.')


    driver.quit()
    print('\nWriting to data base finished with ' + str(COUNTER) + ' new entries.')

# Get search keywords for previous searches
if usr_selection == b'3':
    cur.execute('''select distinct search_keywords from lijobads''')
    col_items = cur.fetchall()
    
    print('Please choose the job search for which to create the word cloud from the list below. Type in the number followed by "Enter"')
    for x in range(len(col_items)):
        print(str(x+1) +'. ' + (col_items[x][0]))

    search_num = int(input())
    search_keywords = col_items[search_num-1][0]


job_details = read_from_postgres(cur, search_keywords)
content = clean_content(job_details)
content_tokens = tokenize_content(content)
filtered_words = stopswords(content_tokens)
cmap = colormap()
create_and_store_wordcloud(filtered_words, cmap)

cur.close()
engine.close()
