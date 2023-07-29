import scrapy
from scrapy import Request
from scrapy.shell import inspect_response
from scrapy.loader import ItemLoader
from jobs_portal.items import JobsPortalItem
from re import sub 
from math import ceil 
from scrapy.http.response.html import HtmlResponse



class EmploiticSpider(scrapy.Spider):
    name = "emploitic"
    allowed_domains = ["emploitic.com"]
    start_urls = ["https://emploitic.com"]

    search_template = 'https://www.emploitic.com/offres-d-emploi?q={cleaned_keyword}'

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
        for page in range(total_pages):
            yield Request(
                self.search_template.format(
                    cleaned_keyword=self.keyword
                ) + f'&start={page*20}',
                dont_filter=True,
                callback=self.parse_jobs,
            )

    def parse_jobs(self,response):
        jobs_urls = response.xpath('//h2[contains(@class,"ellipsis")]/ancestor::a/@href').getall()
        for job_url in jobs_urls :
            yield Request(
                job_url,
                callback=self.parse_job 
            )

    def parse_job(self, response):
        loader = ItemLoader(JobsPortalItem(),response)
        loader.add_value('freelance_website',self.allowed_domains[0])
        loader.add_value('job_url',response.url)
        loader.add_xpath('job_title','string(//a[contains(text(),"Postuler")]/ancestor::div/preceding-sibling::h1)')
        loader.add_xpath('job_description','string(//div[contains(@class,"details-description")])')
        yield loader.load_item()

    def clean_keyword(self) -> str :
        return sub('\s+','+',self.keyword)
    
    def get_total_pages(self,response:HtmlResponse) -> int :
        return ceil(
            int(response.xpath('string(//span[@data-meta-total])').re_first('\d+'))/20
        )
