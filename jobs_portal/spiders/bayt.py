import scrapy
from scrapy import Request 
from scrapy.shell import inspect_response
from scrapy.loader import ItemLoader 
from jobs_portal.items import JobsPortalItem
from scrapy.http.response.html import HtmlResponse
from re import sub 
from math import ceil 


class BaytSpider(scrapy.Spider):
    name = "bayt"
    allowed_domains = ["bayt.com"]
    start_urls = ["https://bayt.com"]

    search_template = 'https://www.bayt.com/en/algeria/jobs/{cleaned_keyword}-jobs/'

    def __init__(self,keyword:str) :
        self.keyword = keyword 

    def start_requests(self):
        yield Request(
            self.search_template.format(
                cleaned_keyword=self.clean_keyword()
            ),
            callback=self.parse_total_pages 
        )

    def parse_total_pages(self,response):
        total_pages= self.get_total_pages(response)
        for page in range(1,total_pages+1):
            yield Request(
                self.search_template.format(
                    cleaned_keyword=self.clean_keyword()
                ) + f'?page={page}',
                callback=self.parse_jobs,
                dont_filter=True,
            )

    def parse_jobs(self,response):
        jobs_urls = [response.urljoin(url) for url in response.xpath('//a[@data-js-aid="jobID"]/@href').getall()]
        for job_url in jobs_urls :
            yield Request(
                job_url,
                callback=self.parse_job 
            )

    def parse_job(self,response):
        loader = ItemLoader(JobsPortalItem(),response)
        loader.add_value('freelancer_website',self.allowed_domains[0])
        loader.add_value('job_url',response.url)
        loader.add_xpath('job_title','string(//h1)',lambda x:[value.strip() for value in x])
        loader.add_xpath('job_description','string(//h2[contains(text(),"Job Description")]/following-sibling::div[1])')
        yield loader.load_item()

    def clean_keyword(self) -> str :
        return sub('\s+','-',self.keyword)

    def get_total_pages(self,response:HtmlResponse) -> int :
        return ceil(int(response.xpath('//span[contains(text(),"Jobs Found")]/text()').re_first('\d+'))/20)
    