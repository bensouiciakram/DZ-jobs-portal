import scrapy
from scrapy import Request 
from scrapy.shell import inspect_response
from scrapy.http.response.html import HtmlResponse
from math import ceil 
from scrapy.loader import ItemLoader 
from jobs_portal.items import JobsPortalItem



class EmploialgerieSpider(scrapy.Spider):
    name = "emploialgerie"
    allowed_domains = ["emploialgerie.com"]
    start_urls = ["https://emploialgerie.com"]

    search_template = 'http://www.emploialgerie.com/search?q={cleaned_keyword}'

    def __init__(self,keyword:str):
        self.keyword= keyword

    def start_requests(self):
        yield Request(
            self.search_template.format(
                cleaned_keyword=self.clean_keyword()
            ),
            callback=self.parse_total_pages
        )

    def parse_total_pages(self,response):
        total_pages = self.get_total_pages(response)
        for page in range(total_pages):
            yield Request(
                self.search_template.format(
                    cleaned_keyword=self.clean_keyword(),
                ) + f'&start={page*20}',
                callback=self.parse_jobs
            )

    def parse_jobs(self, response):
        jobs_urls = [response.urljoin(url) for url in response.xpath('//a[@class="offretitle"]/@href').getall()]
        for job_url in jobs_urls :
            yield Request(
                job_url,
                callback=self.parse_job,
            )

    def parse_job(self,response):
        loader = ItemLoader(JobsPortalItem(),response)
        loader.add_value('freelance_website',self.allowed_domains[0])
        loader.add_value('job_url',response.url)
        loader.add_xpath('job_title','string(//h3)')
        loader.add_xpath('job_description','string(//div[@id="jobDesc"])')
        yield loader.load_item()

    def clean_keyword(self) -> str :
        keyword_list= self.keyword.split()
        return '%20AND%20'.join(
            keyword_list
        )
    
    def get_total_pages(self,response:HtmlResponse) -> int :
        return ceil(max([int(number) for number in response.xpath('//h3[contains(text(),"offres")]').re('\d+')])/15)
