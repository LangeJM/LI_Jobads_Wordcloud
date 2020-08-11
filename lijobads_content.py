'''Module to
    1. get LinkedIn search urls from search query and store to txt
    2. get job ad urls and store to txt
    3. get content from job ads and store to postgres db

'''
import random
import time
from datetime import datetime, timedelta
import msvcrt
import tkinter as tk
from tkinter import filedialog
import argparse
import sys
from dateutil import relativedelta

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


def get_login():
    ''' check if login details provided as arguments and if so store to vars
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "usr", nargs='?', default='', help="Provide your username for automated login", type=str
        )
    parser.add_argument(
        "pwd", nargs='?', default='', help="Provide your password for automated login", type=str
        )
    args = parser.parse_args()
    pwd = args.pwd
    usr = args.usr

    return usr, pwd

def login(driver, usr, pwd):
    '''Blinkist Login, with manual reCaptcha resolution'''
    usr, pwd = get_login()
    driver.get('https://www.linkedin.com/login')

    if usr != '' and pwd != '':

        time.sleep(random.uniform(0, 1.5))
        driver.find_element_by_id('username').send_keys(usr)
        time.sleep(random.uniform(0, 0.5))
        driver.find_element_by_id('password').send_keys(pwd)
        # print('\nClick "Sign in".\n')
        # msvcrt.getch()
        time.sleep(random.uniform(1, 2.5))
        driver.find_element_by_class_name('login__form_action_container').click()

    else:

        print('\nPlease log in manually and press any key in this terminal to continue.\n')
        msvcrt.getch()

def get_search_url():
    '''comma separated search urls from text file to list
    '''
    url_input = ''
    counter = 0
    while url_input == '' or 'linkedin.com/jobs/search/' not in url_input:

        if counter < 3:
            url_input = input(
                '\nPlease copy/paste the url of your LinkedIn job search and hit "Enter".\n'
                )

        else:
            print(
                '''\nThe program will shutdown as no valid link has been provided repeatedly.
                Please press any key.\n'''
                )
            msvcrt.getch()
            sys.exit()

        counter += 1

    if 'keywords=' in url_input:
        search_keywords = url_input.split('keywords=')[1].split('&')[0]
        if '%20' in search_keywords:
            search_keywords = search_keywords.replace('%20', ' ')

    if 'location=' in url_input:
        search_geo = url_input.split('location=')[1].split('&')[0]

    url_keyword = input(
        '\nYour current job search keywords are: ' + str(search_keywords) +
        '. \nLinkedIn suggests positions that are not necessarily a good fit.'
        ' Therefore, it is recommended to reenforce your search by providing a necessary keyword.'
        ' Please provide the keyword and hit "Enter".\n>> ').capitalize()
    print('\nYou chose to reenforce your jobsearch with the keyword: ' + str(url_keyword) + '\n')
    search_url = url_input + str('&start=')

    return search_url, url_keyword, search_keywords, search_geo

def joblinks_to_txt(driver, search_url, url_keyword, search_keywords, search_geo):
    ''' navigate to first search result page and get the number of total search results
    '''
    first_resultpage = search_url + str('0')
    driver.get(first_resultpage)
    time.sleep(random.uniform(2, 3))
    num_results = int(driver.find_element_by_class_name(
        'display-flex.t-12.t-black--light.t-normal').text.split(' ')[0])

    print('\nWe found ' + str(num_results) + ' jobs for your search.\n')

    counter = 0
    already_exists = False

    # store all search result pages in list object
    search_links = []
    for i in range(0, num_results, 25):
        search_links.append(search_url + str(i))

    print('\nList with all search page links:\n' + str(search_links) + '\n')

    # make filename from search keywords, search loaction and date
    filename = 'LI_jobads_' + str(search_keywords) + '_' + str(search_geo) + '.txt'

    # get all jobad urls and save to txt file
    for link in search_links:
        driver.get(link)
        time.sleep(random.uniform(2, 3))

        actions = ActionChains(driver)
        actions.move_to_element_with_offset(driver.find_element_by_tag_name('body'), 0, 0)
        actions.move_by_offset(100, 200).click().perform()

        for _ in range(5):
            actions.send_keys(Keys.SPACE).perform()
            time.sleep(1)

        jobad_links_raw = driver.find_elements_by_partial_link_text(url_keyword)

        for i in range(len(jobad_links_raw)):
            jobad_link = jobad_links_raw[i].get_attribute('href').split('/?')[0]

            if 'www.linkedin.com/jobs/view/' in jobad_link:

                print(jobad_link)

                try:
                    with open(filename, 'r', newline='') as file:
                        saved_urls = [line.strip() for line in file]
                        #print(saved_urls)
                        if jobad_link in saved_urls:
                            already_exists = True
                        else:
                            already_exists = False
                except:
                    print('New file created.')

                with open(filename, 'a') as file:
                    if already_exists is False:
                        file.write(jobad_link + '\n')
                        print('\nUrl saved to file..\n')
                        counter += 1
                    else:
                        print('\nUrl already exists and therefore has not been saved to file..\n')

                #print(str(counter) + ' urls added.\n')
            else:
                continue

    print('\nNumber of urls added: ' + str(counter) + '.\n')

    return filename

def joblinks_txt_to_list(*filename):
    ''' convert urls in txt to list iterable object
    '''
    print('Control print out of filename')
    print(filename)
    try:
        jobad_urls_raw = open(filename, 'r', newline='')
        jobad_urls = jobad_urls_raw.read().split()
        print('Control print out of jobad_urls list:\n' + str(jobad_urls))

    except TypeError:
        (filename, ) = filename
        jobad_urls_raw = open(filename, 'r', newline='')
        jobad_urls = jobad_urls_raw.read().split()
        print('Control print out of jobad_urls list:\n' + str(jobad_urls))

    except:
        raise
        print('\nPlease select the file with the job ad urls. Press "Enter" key to continue.')
        msvcrt.getch()

        filepath = ''
        while filepath == '':
            root = tk.Tk()
            root.withdraw()
            filepath = filedialog.askopenfilename()
            filename = filepath.split('/')[-1]

            jobad_urls_raw = open(filename, 'r', newline='')
            jobad_urls = jobad_urls_raw.read().split()

    return jobad_urls, filename

def get_jobad_header(driver):
    ''' get header content of job ad
    '''
    jobad_header = driver.find_element_by_class_name('mt6.ml5.flex-grow-1')

    jobad_role = jobad_header.text.split('\n')[0]
    jobad_company = jobad_header.text.split('\n')[2]
    jobad_location = jobad_header.text.split('\n')[4]
    jobad_retrieved = datetime.today()

    try:
        jobad_published = jobad_header.text.split('\n')[6]

        if jobad_published == 'Posted Date':
            jobad_published = datetime.today() - timedelta(
                hours=int(jobad_header.text.split('\n')[7].split(' ')[1])
                )
            jobad_published = jobad_published.strftime("%Y-%m-%d")
        elif 'day' in jobad_published:
            jobad_published = datetime.today() - timedelta(days=int(jobad_published.split(' ')[1]))
            jobad_published = jobad_published.strftime("%Y-%m-%d")
        elif 'week' in jobad_published:
            jobad_published = datetime.today() - timedelta(weeks=int(jobad_published.split(' ')[1]))
            jobad_published = jobad_published.strftime("%Y-%m-%d")
        elif 'month' in jobad_published:
            jobad_published = datetime.today()\
            - relativedelta.relativedelta(months=int(jobad_published.split(' ')[1]))
            jobad_published = jobad_published.strftime("%Y-%m-%d")
        elif 'year' in jobad_published:
            jobad_published = datetime.today()\
            - relativedelta.relativedelta(years=int(jobad_published.split(' ')[1]))
            jobad_published = jobad_published.strftime("%Y-%m-%d")
    except IndexError:
        jobad_published = None


    return jobad_role, jobad_company, jobad_location, jobad_published, jobad_retrieved

def get_jobad_content(driver):
    ''' get remaining job ad content
    '''
    # click 'see more' once to get all the content
    driver.find_element_by_class_name(
        'artdeco-button--icon-right.artdeco-button--2.artdeco-button--tertiary.ember-view'
        ).click()

    # get the job ad content
    job_details = driver.find_element_by_id('job-details').text

    # get job skills and return empty if skills section is missing
    try:
        job_skills_raw = driver.find_element_by_class_name(
            'js-criteria-skills.list-style-none'
            ).text
    except:
        job_skills_raw = ''
    # get job categories and return empty if section is missing
    try:
        job_categories_raw = driver.find_element_by_class_name(
            'jobs-description-details.ember-view'
            ).text
    except:
        job_categories_raw = ''

    # Clean skills and categories from unwanted entries
    job_skills = ''
    for line in job_skills_raw.split('\n'):
        if ((line != 'No match') and (line != 'Match')):
            job_skills += line + '\n'

    job_categories = ''
    for line in job_categories_raw.split('\n'):
        if line != 'Job Details':
            job_categories += line + '\n'

    return job_details, job_skills, job_categories
