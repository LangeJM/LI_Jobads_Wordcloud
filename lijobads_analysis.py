'''Module that takes text from job ads stored in postgres db and provides
a wordcloud protentially other analysis
'''


import os
import tkinter as tk
from tkinter import filedialog
import msvcrt

import nltk
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


def read_from_postgres(cur, search_keywords):
    ''' Get content from postgres db
    '''

    cur.execute('''select job_details, job_skills from lijobads where search_keywords = %s''', (search_keywords, ))
    job_details = cur.fetchall()

    return job_details

def clean_content(job_details):
    ''' Clean content from unwanted terms and phrases
    '''
    content = ''

    for job in range(len(job_details)):
        for i in range(len(job_details[job])):
            content = content + '\n' + job_details[job][i]

    print('''\nPlease select a txt file of comma separated exlusions terms or press "ESC" to continue without any exclusions. Please note, stopwords will be defined shortly. \nPress "Enter to continue.''')
    exclusions_sel = msvcrt.getch()
    if exclusions_sel != b'\x1b':
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename()
        if filepath != '':
            filename = filepath.split('/')[-1]
            file_exclusions = open(filename, 'r', newline='', encoding='utf-8')
            exclusions = file_exclusions.read().split(',')
            print('\nThis is you final list of exclusions: ' +str(exclusions))

        for i in exclusions:
            content = content.replace(i, '')

    return content

def tokenize_content(content):
    ''' Split up content into words and symbols respectively
    '''
    nltk.download('punkt')
    content_tokens = nltk.word_tokenize(content)

    return content_tokens


def stopswords(content_tokens):
    '''Clean content by defining and deleting stopwords
    '''
    stopwords = set(STOPWORDS)

    #ask for customized stopwords txt file opr standard
    print('''\nPlease select a txt file of comma separated stopwords or press "ESC" to continue with a set of standard stopwords only. \nPress "Enter" to continue.''')
    stopwords_sel = msvcrt.getch()
    if stopwords_sel != b'\x1b':
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename()
        if filepath != '':
            filename = filepath.split('/')[-1]
            file_stopwords = open(filename, 'r', newline='', encoding='utf-8')
            new_stopwords = file_stopwords.read().split(',')
            stopwords.update(new_stopwords)
            print('\nThis is you final list of stopwords: ' +str(stopwords))

    filtered_words = [word for word in content_tokens if word not in stopwords]

    return filtered_words

def colormap():
    ''' Query custom colormap or proceed with standard
    '''
    colors = ["#E61018", "#03B0F1", "#0913b3", "#000000"]
    cmap = LinearSegmentedColormap.from_list("mycmap", colors)

    user_input = input('''\nPlease type in the colormap of your choice or leave empty for the standard colormap. Press "Enter" to confirm. \nFor a list of available maps, navigate to https://matplotlib.org/3.3.0/tutorials/colors/colormaps.html.''')

    colormaps = ['Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3',
                 'tab10', 'tab20', 'tab20b', 'tab20c', 'twilight', 'twilight_shifted', 'hsv',
                 'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu', 'RdYlGn',
                 'Spectral', 'coolwarm', 'bwr', 'seismic', 'binary', 'gist_yarg', 'gist_gray',
                 'gray', 'bone', 'pink', 'spring', 'summer', 'autumn', 'winter', 'cool',
                 'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper', 'Greys', 'Purples', 'Blues',
                 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu',
                 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 'viridis',
                 'plasma', 'inferno', 'magma', 'cividis']
    if user_input in colormaps:
        cmap = '"' + user_input + '"'
    else:
        cmap = cmap

    return cmap


def create_and_store_wordcloud(filtered_words, cmap):
    ''' Create and store wordcloud as png file in working directory
    '''
    #cloud = WordCloud(width=1600, height=1000, collocations=True, max_words = 500, stopwords=stopwords, background_color='white', min_font_size=8, max_font_size=None, colormap=cmap1).generate(' '.join(filtered_words))
    cloud = WordCloud(width=1000, height=600, background_color='white', colormap=cmap).generate(' '.join(filtered_words))

    plt.figure(figsize=(20, 10), facecolor='white')
    plt.imshow(cloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    #plt.show()
   
    # Do not overwrite existing png files
    i = 0
    for fname in os.listdir('.'):
        if fname.endswith('.png'):
            i += 1
            
    wordlcloud_fn = "wordcloud" + str(i) + ".png"
    
    cloud.to_file(wordcloud_fn)
    print('\nThe wordcloud has been saved as png file: ' + str(wordcloud_fn))
