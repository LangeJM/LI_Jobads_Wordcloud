# LI_Jobads_Wordcloud

### Create a word cloud from LinkedIn job ads

#### *Still in the beginning of my coding journey, so please bare with me.*

#### What the script does, step-by-step:
1. Starts selenium Firefox session and acquires job ads based on provided search url
2. Saves job ads content to postgres db 
3. Creates and saves word cloud as png file from job ads content

#### What you need to run the script: 
- LinkedIn login and search url <br />
(such as: https://www.linkedin.com/jobs/search/?geoId=101620260&keywords=qa%20automation%20lead&location=Israel)
- Run and tested on Windows environment and Python 3.8
- A bunch of libraries [(list with libraries to install)](https://github.com/LangeJM/Selenium_Blinkist/blob/master/requirements.txt)
- Selenium webdriver for Firefox, [Geckodriver](https://github.com/mozilla/geckodriver/releases)
- Run and tested with [postgreSQL 12](https://www.postgresql.org/about/news/1976/) and [pgAdmin4](https://www.pgadmin.org/download/)
```
#You will be prompted for a text file with db details, such as below:

database=postgres
user=username
password=1234pwd
host=localhost
port=5432
```


#### Installation:
I am using Anaconda and installed the libraries as needed while progressing with the code. 
Usually you can install all packages with: 
```
conda install --file requirements.txt
```
However, there seem to be conflicts between selenium and wordcloud. You should be able to resolve this by using 
``` 
pip install wordlcoud
``` 

#### Running the script:
You can provide command line arguments to automatically log in to LinkedIn with your credentials.
```
python lijobads_main.py username password
```
To not lose any information, the progress is saved to a txt file and to the db respectively. You will have the option to pick up from previous sessions by providing the respective [text file with the job ad urls](https://github.com/LangeJM/LI_Jobads_Wordcloud/blob/master/example_jobad_urls.txt) or [db details](https://github.com/LangeJM/LI_Jobads_Wordcloud/blob/master/example_db_details.txt), or to repeat the complete process.

Also, the results of the wordcloud will be much improved if you provide [stopwords](https://github.com/LangeJM/LI_Jobads_Wordcloud/blob/master/example_stopwords.txt) and [phrases/terms to exclude](https://github.com/LangeJM/LI_Jobads_Wordcloud/blob/master/example_exclusions.txt). These will be queried via file dialog as well.

#### Wordcloud Examples:

![](wordcloud.png)
<br />
<br />
<br />
![](wordcloud0.png)
