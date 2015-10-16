# Obama Speech Web Scraper
# 2015-10-05
# Nick McClure:  nfmcclure@gmail.com

from lxml import html
import requests
import re
import pandas as pd

speech_page = requests.get('http://www.americanrhetoric.com/barackobamaspeeches.htm')
speech_tree = html.fromstring(speech_page.text)

# Get Dates
date_list1 = speech_tree.xpath('//*[@id="AutoNumber1"]/tr/td/font/text()')
date_list2 = speech_tree.xpath('//*[@id="AutoNumber1"]/tr/td/p/font/text()')
date_list = date_list1 + date_list2

r = re.compile('[0-9]{2} [A-Za-z]* [0-9]{4}')
date_list = filter(r.match, date_list)

# Get Titles
titles = speech_tree.xpath('//*[@id="AutoNumber1"]/tr/td/font/a/text()|//*[@id="AutoNumber1"]/tr/td/p/font/a/text()')
titles = [x for x in titles if x not in ['\r\n\t\t', '\r\n']]
titles = [x.replace("\r\n","") for x in titles]
titles = [x.replace("\t","") for x in titles]
titles = [x for x in titles if x != '']
titles = titles[9:]

# Get HTML Links to speech texts
html_links = speech_tree.xpath('//*[@id="AutoNumber1"]/tr/td/font/a/@href|//*[@id="AutoNumber1"]/tr/td/p/font/a/@href')
# r_link = re.compile('speeches[//A-Za-z.0-9]+.htm')
# html_links = filter(r_link.match, html_links)
pdf_re = re.compile('(.pdf)|(.mp3)|(.swf)')
html_links = [x for x in html_links if not pdf_re.search(x)]
html_links = html_links[9:]
html_links = [x for x in html_links if x != '']
html_links = ['http://www.americanrhetoric.com/'+x for x in html_links]
del html_links[28]

# Save as pandas dataframe
obama_speech_frame = pd.DataFrame({'title': titles,
                                   'date': date_list,
                                   'html_link': html_links})

# Get speech text:
speech_text = []
for i,link in enumerate(obama_speech_frame['html_link']):
    try:
        text_page = requests.get(link)
        text_tree = html.fromstring(text_page.text)
        text = text_tree.xpath('//*[@id="AutoNumber1"]/tr/td/p/font/text()|' +
                               '//*[@id="AutoNumber1"]/tr/td/blockquote/blockquote/p/i/font/text()|' +
                               '//*[@id="AutoNumber1"]/tr/td/div/div/p/font/text()|' +
                               '//*[@id="AutoNumber1"]/tr/td/div/div/p/font/a/font/text()|' +
                               '//*[@id="AutoNumber1"]/tr/td/div/div/div/p/font/text()|' +
                               '//*[@id="AutoNumber1"]/tr/td/div/div/div/p/font/a/font/text()|' +
                               '//*[@id="AutoNumber1"]/tbody/tr/td/div/div/div/p/font/text()|' +
                               '//*[@id="AutoNumber1"]/tbody/tr/td/div/div/div/p/font/a/font/text()')
        text = ' '.join(text)
        text = text.replace(":\n \n :", "")
        text = text.replace("\n","")
        for n in range(80,100):
            text = text.replace(u'x'+str(n),"")
        text = text.replace(u'\xa0',"")
        text = text.replace('\'',"")
        text = text.replace('\r',"")
        text = text.replace('\t',"")
        text = text.replace('\n',"")
    except:
        text = ''
    try:
        first_trim = text.find('[ ')
        second_trim = text.find('] ')
        trim_point = max(first_trim, second_trim)
        if trim_point <= 350:
            text = text[(trim_point+2):]
    except:
        pass
    speech_text.append(text)

    print('Done with #' + str(i) + ' out of ' + str(len(obama_speech_frame)) + '.')

# Append dataframe with speech text
obama_speech_frame['speech'] = speech_text

# Save output
obama_speech_frame.to_csv('obama_speeches.csv', index=False, sep=',', encoding='utf-8')
