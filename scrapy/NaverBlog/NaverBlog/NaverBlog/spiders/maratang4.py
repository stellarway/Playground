# -*- coding: utf-8 -*-
import scrapy
import re
from urllib import parse
from NaverBlog.items import MaratangItem

class Maratang4Spider(scrapy.Spider):
    name = 'maratang4'
    allowed_domains = ['naver.com'] 
    start_urls = ['https://search.naver.com/search.naver?date_from=20190711&date_option=8&date_to=20190711&dup_remove=1&nso=so%3Add%2Cp%3Afrom20190711to20190711&post_blogurl=&post_blogurl_without=&query=%EB%A7%88%EB%9D%BC%ED%83%95&sm=tab_pge&srchby=all&st=date&where=post&start=1',
    'https://search.naver.com/search.naver?date_from=20190711&date_option=8&date_to=20190711&dup_remove=1&nso=so%3Add%2Cp%3Afrom20190711to20190711&post_blogurl=&post_blogurl_without=&query=%EB%A7%88%EB%9D%BC%ED%83%95&sm=tab_pge&srchby=all&st=date&where=post&start=11',
    'https://search.naver.com/search.naver?date_from=20190711&date_option=8&date_to=20190711&dup_remove=1&nso=so%3Add%2Cp%3Afrom20190711to20190711&post_blogurl=&post_blogurl_without=&query=%EB%A7%88%EB%9D%BC%ED%83%95&sm=tab_pge&srchby=all&st=date&where=post&start=21']
    
    def parse(self, response):
        for href in response.xpath("//ul[@class='type01']/li/dl/dt/a/@href").extract() :
            print(href)
            yield response.follow(href, self.parse_iframe)

    def parse_iframe(self, response):    
        iframe_url = response.xpath("//iframe/@src").get()
        if iframe_url != None :
            href = 'https://blog.naver.com' + response.xpath("//iframe/@src").get()
            yield response.follow(href, self.parse_details)

    def parse_details(self, response):  
        item = MaratangItem()
        item['url'] = response.url
        query_str = parse.parse_qs(parse.urlsplit(response.url).query)
        item['author'] = query_str['blogId'][0]

        titlecontent = ""
        title = ""

        if 'blog.naver.com' in response.url :
            title = str(response.xpath("//div[@class='se-module se-module-text se-title-text']/p/span/text()").get())
            item['date'] = response.xpath("//span[contains(@class, 'se_publishDate')]/text()").get()
            content = str(response.xpath("//div[@class='se-main-container']").get())

            if content == 'None' :
                title = str(response.xpath("//div[contains(@class,'se_title')]//h3").get())
                item['date'] = response.xpath("//span[contains(@class, 'se_publishDate')]/text()").get()
                content = str(response.xpath("//div[contains(@class, 'sect_dsc')]").get())

            if content == 'None' :
                title = str(response.xpath("//div[@class='htitle']/span/text()").get())
                item['date'] = response.xpath("//p[contains(@class,'_postAddDate')]/text()").get()
                content = str(response.xpath("//div[@id='postViewArea']/div").get())

        title = re.sub(' +', ' ', str(re.sub(re.compile('<.*?>'), ' ', title.replace('"','')).replace('\r\n','').replace('\n','').replace('\t','').replace('\u200b','').strip()))
        content = re.sub(' +', ' ', str(re.sub(re.compile('<.*?>'), ' ', content.replace('"','')).replace('\r\n','').replace('\n','').replace('\t','').replace('\u200b','').strip()))
        item['title'] = title 
        item['content'] = content  

        yield item
        
