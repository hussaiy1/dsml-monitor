import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from mail import *
import os
import logging

##Remove log file it it exists
if os.path.isfile('DSML_log.log'):
    os.remove("DSML_log.log")
else:
    pass

#CREATE LOG FILE
logger = logging.getLogger('DSML_log.log')
logger.setLevel(logging.DEBUG)

#CREATE THE FORMAT OF THE LOG HANDLER
fh = logging.FileHandler('DSML_log.log')
formatter = logging.Formatter('%(asctime)s -  %(message)s')

fh.setFormatter(formatter)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

#HEADERS USED FOR THE REQUES
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Connection': 'keep-alive',
           }
logger.info('Starting new session')

#START REQUEST SESSION TO SOUP DATA
with requests.Session() as s:
    r = s.get('https://london.doverstreetmarket.com/new-items', headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    logger.info(str(r.status_code) + ' - Status Code')

logger.info('Scraping data from DSML')

#SCRAPE THE DSML BLOCK AND THEN SEARCH FOR THE BLOCK IDS
DCMP_Block = soup.find('div', attrs={'data-block-id': '122616'})
data_block_ids = [div['data-block-id'] for div in DCMP_Block.find_all('div', {'data-block-id': True})]


block_ids=[]

logger.info('Appending DSML Block ID to list')

#PLACE ALL THE BLOCK ID'S INTO A LIST
for i in range(len(data_block_ids)):
    block_ids.append(data_block_ids[i])
    logger.info(data_block_ids[i] + ' - Appended to list')

#CHECK IF A FILE WITH THE BLOCKID'S EXISTS ELSE CREATE A FILE WITH THE IDS
if os.path.isfile('dsml_id.txt'):
    pass
else:
    with open('dsml_id.txt', 'w') as f:
        for id in block_ids:
            f.write('%s\n' % id)
            logger.info('Creating dsml_id.txt with Block Id')
            f.close

dsmlID_Fromfile=[]

#APPEND THE ID'S FROM THE FILE TO THE dsmlID_Fromfile LIST
with open('dsml_id.txt', 'r') as file:
    for line in file:
        line=line.strip()
        dsmlID_Fromfile.append(line)
        logger.info(line + 'Appending to dsmlID_Fromfile')

#COMPARE dsmlID_Fromfile WITH block_ids, IF TRUE NO NEW PRODUCTS HAVE BEEN FOUND, ELSE THERE IS A NEW PRODUCT
if dsmlID_Fromfile == block_ids:
    print('No New Products')
    logger.info('No New Products')
else:
    newItems = list(set(block_ids) - set(dsmlID_Fromfile))
    logger.info('New items found, adding them to New Items list')
    #NEW PRODUCT WILL NEED TO BE SENT AS AN EMAIL AND AND A NEW FILE NEEDS TO BE CREATED TO MATCH THE BLOCK IDS
    for i in range(len(newItems)):
        item = DCMP_Block.find('div', attrs={'data-block-id': str(newItems[i])})
        image = item.find('img', {'src': True})
        header = item.find('p', attrs={'class': ""})
        send_mail(image['src']+ ' ' + header.get_text())
        logger.info('Sending email for - ' + str(header))
    with open('dsml_id.txt', 'w') as f:
        for id in block_ids:
            f.write('%s\n' % id)
            logger.info('Creating dsml_id.txt with new Block Id')
            f.close





#with open('block_id.txt', 'a') as f:
#    f.write(str(data_block_ids))
#    f.close()
#
#with open('block_id.txt', 'r') as f:
#    file_contents=f.read()
#    f.close()
#
#if os.path.isfile('output.html'):
#    os.remove("output.html")
#else:
#    pass
#
#
#for i in range (len(data_block_ids)):
#    block = DCMP_Block.find('div', attrs={'data-block-id': data_block_ids[i]})
#    content= str(block.get_text())
#    with open('output.html', 'a') as f:
#        f.write(content)
#        f.close()
#
#with open('output.html', 'r') as f :
#    file_contents = f.read()
#    send_mail(str(file_contents))
#    f.close()

#Each block has an id number, 
# if i output the id numbers to a new file in a list, 
# then everytime the script runs it will use the scraped id's to compare id's in the file
# if there is a miss match it means new product has been added.
# the data of the new product will then be sent in an email
# this id can then be appended to the file
