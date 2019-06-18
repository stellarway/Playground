#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os

Intro='안녕하세요. 웹툰 선호도를 조사 중입니다.'
maker='wony'
BASE_DIR=os.getcwd()

class crl():
    
    def __init__(self, base_dir):
        self.base_dir=BASE_DIR
    

    def get_naverToon_info():

        naverToon_url="https://comic.naver.com/webtoon/creation.nhn"
        naver_resp=requests.get(naverToon_url)
        naver_soup=BeautifulSoup(naver_resp.content,'html.parser')
        all_list=naver_soup.find('div', class_="all_list").find_all('li')
    #     start=time.time()
        all_info=[]
        for item in all_list:
            a_tag=item.find('a')
            title=a_tag['title']

            link=a_tag['href']
            item_resp=requests.get("https://comic.naver.com/"+link)
            item_soup=BeautifulSoup(item_resp.content,'html.parser')

            toon_info=item_soup.find('div', class_="webtoon")
            if item_soup.find('div', class_="webtoon").find('ul',class_="category_tab"):
                day=toon_info.find('ul',class_="category_tab").find('li',class_="on").text
            else:                
                day_temp=item_soup.find('table', class_="viewList").find('td',class_="num").text.split('.')
                day_temp[2]='완결'
                day=" ".join(day_temp)

            author_info=toon_info.find('span',class_='wrt_nm')
            author=author_info.text.strip()

    #         detail_info=toon_info.find('p')
    #         detail=detail_info.text.decode('utf-8')

    #         all_info.append([title,author,day,detail])

            print('{}에 대한 정보를 가져오는 중입니다.'.format(title))
            df=pd.DataFrame({'제목':[title],'작가':[author],'연재상태':[day]})
            if all_list.index(item)==0:            
                df.to_csv('all_info.csv', index=False, columns=['제목','작가','연재상태'],encoding='cp949')

            else:
                df.to_csv('all_info.csv', index=False, header=False,encoding='cp949',mode='a')
        print("모든 웹툰 정보가 저장되었습니다.")
    #     df_all_info=pd.DataFrame(all_info, columns=['제목','작가','연재상태','상세설명'])
    #         all_info.append([title,author,day])

    #     df_all_info=pd.DataFrame(all_info, columns=['제목','작가','연재상태'])
    #     df_all_info.to_csv('all_info_detail.csv', encoding='cp949')

    #         print("Runtime: %0.3f"%(time.time() - start))
    def pick(*args):# 0<args<839
        pick_toon=pd.read_csv('all_info.csv', encoding='cp949')

    #     pick_toon=pd.DataFrame(pick_toon, columns=['제목','작가','연재상태'])
        pick_title=[]
        for arg in args:
            pick_title.append(pick_toon.loc[arg-1,'제목'])
    #     return pick_toon
        return pick_title

    # pick_title=pick(1,11,445)
    def find_genre(title):
        genre_url='https://comic.naver.com/webtoon/genre.nhn'
        genre_list=['episode','omnibus','story','daily','comic','fantasy','action','drama','pure','sensibility','thrill','historical','sports']
        title_genre=[]
        for genre in genre_list:
            params={
                'genre': genre
            }
            genre_resp=requests.get(genre_url, params=params)
            genre_soup=BeautifulSoup(genre_resp.content,'html.parser')
    #         for title in pick_title:
    #             print("{}은 {}장르입니다.".format(title, genre)
            if genre_soup.find_all('a',text=title):
                title_genre.append(genre)
            else:
                pass
        return title_genre

