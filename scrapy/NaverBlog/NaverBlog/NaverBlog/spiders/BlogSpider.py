
import scrapy
import pandas as pd
from datetime import date
import time
from NaverBlog.items import NaverblogItem

end = date.today()

class BlogspiderSpider(scrapy.Spider):
    name = 'BlogSpider'
    start_urls=[]

    for i in pd.date_range(periods=1, end=end):
        date=i.strftime('%Y%m%d')
        query='마라탕'
        # query = getattr(self, 'query', None)
        url='https://search.naver.com/search.naver?where=post&st=date&query={0}&date_from={1}&date_to={1}&date_option=8'.format(query, date)           
        start_urls.append(url)
                
    def parse(self, response):

        for item in response.css('li.sh_blog_top'):
            
            url = item.css('a::attr(href)').get()
            yield response.follow(url, self.parse_iframe)

        next_page=response.css('div.paging a.next::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_iframe(self, response):
        href = 'https://blog.naver.com' + response.xpath("//iframe/@src").get()
        yield response.follow(href, self.parse_details)  

    def parse_details(self, response):
        try:

            tempList = [ i.strip() for i in response.css('div.se-main-container *::text').getall() ]
            body = ' '.join(tempList).replace('\n\n','').replace('\u200b','').replace('\xa04','')
            title = response.css('span.se-fs-::text').get()
            nick = response.css('span.nick a.link::text').get()
            date = response.css('span.se_publishDate::text').get()

            item= NaverblogItem()

            item['title']= title
            item['nick']= nick
            item['date']= date
            item['body'] = body

            yield item

        except Exception as e:
            print('-'*50)
            print(e)
            print('-'*50)
            
        



        

