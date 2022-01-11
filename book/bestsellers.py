from bs4 import BeautifulSoup as bs
import requests
import re
import xml.etree.ElementTree as ET


def aladin_get_bestseller():
    url = "https://www.aladin.co.kr/shop/common/wbest.aspx?BestType=Bestseller&BranchType=1&CID=0"
    req = requests.get(url)
    content = req.content

    soup = bs(content,'html.parser')
    book_name = soup.select('a.bo3 b')
    book_price = soup.select('span.ss_p2 span')

    book_names = map(lambda x: x.text, book_name)
    book_prices = map(lambda x: x.text,book_price)

    return list(zip(book_name, book_price))

    # result = aladin_get_bestseller()
    # pattern = '<[^>]*>'
    # for index,item in enumerate(result):
    #     print('[{:2}]위 {} / {}원'.format(index +1,
    #                                 re.sub(pattern = pattern, repl=' ',string=str(item[0])),
    #                                 re.sub(pattern = pattern, repl=' ',string=str(item[1]))))



def kyobo_get_bestseller():
     url = "http://m.kyobobook.co.kr/digital/ebook/ajaxBestList.ink"
     post_data = {
          'count1' : 1,
          'item_position' : 1,
          'listCateGubun' :1,
          'listSortType' : 0,
          'listSortType2' : 0,
          'listSortType3' : 0,
          'listSortType4' : 0,
          'class_code' : '',
     }
     req = requests.post(url,data=post_data)
     content = req.content

     xml = ET.fromstring(content)

     book_names = map(lambda x : x.text, xml.iter('titlen'))
     book_authors = map(lambda x : x.text, xml.iter('author'))
     book_prices = map(lambda x : x.text, xml.iter('salePrice'))

     return list(zip(book_names, book_authors, book_prices))

# result = kyobo_get_bestseller()
# for index, item in enumerate(result):
#      print('[{:2}위] {} / {} / {} '.format(index+1,item[0],item[1],item[2]))


def yes24_get_bestseller():
     url = "http://www.yes24.com/_par_/welcome/TodayBook/BestSeller/W_R6_TodayBook_BestSeller_DomesticBook.htm"
     req =requests.get(url)
     content = req.content

     soup = bs(content,'html.parser')
     elements = soup.find_all('span',class_ = 'rnk_info')

     return list(map(lambda x : (x.strong.text, x.em.text), elements))

# result = yes24_get_bestseller()

# for index, item in enumerate(result):
#      print('[{:2}위] {} / {}'.format(index+1,item[0],item[1]))

def youngpoong_get_content():
     url = 'http://ypbooks.co.kr/m_bestseller.yp'
     req = requests.get(url)
     content = req.content

     soup = bs(content,'html.parser')
     book_name = soup.find_all('span',class_= 'info-tit')
     book_price = soup.find_all('span',class_ = 'de price')

     #book_name = re.sub('<.+?>','',str(book_name),0).strip()     
     #book_price = re.sub('<.+?>', '', str(book_price), 0).strip()
     
     book_names = map(lambda x : x.text, book_name)
     book_prices = map(lambda x: x.text, book_price)

     
     return list(zip(book_name,book_price))

# result = get_content()
# pattern = '<[^>]*>'
# for index, item in enumerate(result):
#      print('[{:2}]위 {} / {}'.format(index+1,
#                                     re.sub(pattern=pattern,repl=' ',string=str(item[0])),
#                                     re.sub(pattern=pattern,repl=' ',string=str(item[1]))))