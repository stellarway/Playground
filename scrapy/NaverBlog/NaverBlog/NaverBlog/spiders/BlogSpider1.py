# wonspider ver1.

import scrapy
import pandas as pd
from datetime import date
import time

end = date.today()

class BlogspiderSpider(scrapy.Spider):
    name = 'BlogDetailSpider'
    start_urls=[]

    for i in pd.date_range(periods=2, end=end):
        # date=str(i).replace('-','')[:9]
        date=i.strftime('%Y%m%d')
        # date= getattr(self, 'date', None)
        query='마라탕'
        # keyword = getattr(self, 'key', None)
        url='https://search.naver.com/search.naver?where=post&st=date&query={0}&date_from={1}&date_to={1}&date_option=8'.format(query, date)           
        start_urls.append(url)
                

    def parse(self, response):

        # print("="*100)
        # print(response.css('li.sh_blog_top').getall())
        # print("="*100)

        for item in response.css('li.sh_blog_top'):

            title = item.css('a.sh_blog_title::attr(title)').get()

            if item.css('a.sh_blog_title::attr(title)').get() == '':
                title = item.css('a.sh_blog_title::text').get()

            yield {
                'title': title,
                'author': item.css('span.inline a::text').get(),
                # 'content' : content,
                'date' : item.css('dd.txt_inline::text').get(),
                'url' : item.css('a::attr(href)').get()
            }
        
        next_page=response.css('div.paging a.next::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
