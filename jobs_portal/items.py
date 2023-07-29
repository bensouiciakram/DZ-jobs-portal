# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst 


class JobsPortalItem(scrapy.Item):
    freelance_website = scrapy.Field(
        output_processor=TakeFirst()
    )
    job_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    job_title = scrapy.Field(
        output_processor=TakeFirst()
    )
    job_description = scrapy.Field(
        output_processor=TakeFirst()
    )
