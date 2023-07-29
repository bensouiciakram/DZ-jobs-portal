import scrapy
from scrapy import Request 
from scrapy.shell import inspect_response
from scrapy.http.response.html import HtmlResponse
from scrapy.loader import ItemLoader
from jobs_portal.items import JobsPortalItem
from urllib.parse import quote 
from re import findall 
from math import ceil 


class JobrapidoSpider(scrapy.Spider):
    name = "jobrapido"
    allowed_domains = ["jobrapido.com"]
    start_urls = ["https://jobrapido.com"]

    search_template = 'https://dz.jobrapido.com/?w={cleaned_keyword}'

    def __init__(self,keyword:str) :
        self.keyword = keyword 

    def start_requests(self):
        yield Request(
            self.search_template.format(
                cleaned_keyword=self.clean_keyword()
            ),
            callback=self.parse_total_pages,

        )

    def parse_total_pages(self,response):
        total_pages = self.get_total_pages(response)
        for page in range(1,total_pages+1):
            yield Request(
                response.url + f'&p={page}',
                callback=self.parse_jobs,
                dont_filter=True
            )

    def parse_jobs(self,response):
        jobs_urls = response.xpath('//a[@class="result-item__link"]/@href').getall()
        for job_url in jobs_urls :
            yield Request(
                job_url,
                callback=self.parse_job
            )

    def parse_job(self,response):
        loader = ItemLoader(JobsPortalItem(),response)
        loader.add_value('freelance_website',self.allowed_domains[0])
        loader.add_value('job_url',response.url)
        loader.add_xpath('job_title','string(//h1[@class="jpp-advert__title"])')
        loader.add_xpath('job_description','string(//div[@class="jpp-advert__description js-jpp-advert-description"])')
        yield loader.load_item()

    def clean_keyword(self):
        return quote(self.keyword)
    
    def get_total_pages(self,response:HtmlResponse) -> int :
        return ceil(int(findall('totalResults:\s(\d+)',response.text)[0])/8)
