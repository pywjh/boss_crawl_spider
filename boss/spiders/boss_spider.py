# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from ..items import BossItem

class BossSpiderSpider(RedisSpider):
    name = 'boss_spider'
    # start_urls = ['https://www.zhipin.com/c101200100/?query=python&']
    redis_key = 'zp_start:urls'

    def parse(self, response):
        # 下一页
        next_url = response.xpath('//a[@class="next"]/@href').extract_first()
        yield scrapy.Request(url='https://www.zhipin.com'+next_url)

        job_title = response.xpath('//div[@class="job-title"]/text()').extract()
        wage = response.xpath('//span[@class="red"]/text()').extract()
        info = response.xpath('//div[@class="info-primary"]/p/text()').extract()
        infomations = [info[i:i+3] for i in range(0, len(info), 3)]
        infomation = [''.join(i) for i in infomations]
        companys = response.xpath('//div[@class="company-text"]/h3/a/text()').extract()
        company = [company for company in companys if '\n' not in company]
        public_time = response.xpath('//div[@class="info-publis"]/p/text()').extract()
        detail_urls = response.xpath('//div[@class="info-primary"]//h3/a/@href').extract()
        detail_urls = ['https://www.zhipin.com' + detail_url for detail_url in detail_urls]

        for url, job_title, wage, infomation, company, public_time in zip(detail_urls, job_title, wage, infomation, company, public_time):
            item = BossItem()
            item['job_title'] = job_title,
            item['wage'] = wage,
            item['infomation'] = infomation,
            item['company'] = company,
            item['public_time'] = public_time

            yield scrapy.Request(url=url, callback=self.detail_parse, meta={'item':item})

    def detail_parse(self, response):
        item = response.meta.get('item')
        requirements = response.xpath('string(//div[@class="text"])').extract_first()
        print(requirements.strip())
        item['requirements'] = requirements

        yield item
