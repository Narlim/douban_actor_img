# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from actor_img.items import ActorImgItem
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest


class ImgspiderSpider(scrapy.Spider):
    name = 'imgspider'
    
    def __init__(self, actor=None, **kwargs):
        super().__init__(**kwargs)
        self.actor = actor
        self.script = f'''
        function main(splash, args)
            splash.private_mode_disable = false
            splash:on_request(function(request)
            request:set_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:72.0) Gecko/20100101 Firefox/72.0")')
            end)
            url = args.url
            assert(splash:go(url))
            assert(splash:wait(5))
            input_box = assert(splash:select("#inp-query"))
            input_box:focus()
            input_box:send_text("{self.actor}")
            assert(splash:wait(0.5))
            input_box:send_keys("<Enter>")
            assert(splash:wait(10))
            return splash:html()
        end
        '''

    def start_requests(self):
        yield SplashRequest(url="http://movie.douban.com/",
                            callback=self.parse,
                            endpoint="execute",
                            args={'lua_source': self.script})


    def parse(self, response):
        actor_url = response.xpath(
            "//div[@class='detail']/div/a/@href").extract_first()
        all_photos_url = actor_url + 'photos/'
        yield Request(url=all_photos_url, callback=self.img_parse)


    def img_parse(self, response):        
        image_urls = response.xpath("//li/div[@class='cover']/a/img/@src").getall()
        for image_url in image_urls:
            loader = ItemLoader(item=ActorImgItem(), response=response)
            replaced_image_url = image_url.replace('/m/', '/l/')
            loader.add_value('image_urls', replaced_image_url)
            yield loader.load_item()

        next_page = response.xpath("//span[@class='next']/a/@href").get()
        if next_page:
            yield Request(url=next_page, callback=self.img_parse)