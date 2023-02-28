import re
import json
import scrapy
from urllib.parse import urlencode
from datetime import datetime


class IndeedJobSpider(scrapy.Spider):
    name = "indeed.com_LM"
    custom_settings = {
        'FEEDS': {'data/%(name)s_%(time)s.csv': {'format': 'csv', }}
    }

    def get_indeed_search_url(self, keyword, location, offset=0):
        parameters = {"q": keyword, "l": location, "filter": 0, "start": offset}
        return "https://www.indeed.com/jobs?" + urlencode(parameters)

    def start_requests(self):
        keyword_list = ['mechanical engineer']
        location_list = ['']
        for keyword in keyword_list:
            for location in location_list:
                indeed_jobs_url = self.get_indeed_search_url(keyword, location)
                yield scrapy.Request(url=indeed_jobs_url, callback=self.parse_search_results,
                                     meta={'keyword': keyword, 'location': location, 'offset': 0})

    def parse_search_results(self, response):
        location = response.meta['location']
        keyword = response.meta['keyword']
        offset = response.meta['offset']
        script_tag = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', response.text)
        if script_tag is not None:
            json_blob = json.loads(script_tag[0])

            with open(f'_____parse_search_results.json', 'w', encoding='utf-8') as file:
                json.dump(json_blob, file, indent=4, ensure_ascii=False)

            ## Extract Jobs From Search Page
            jobs_list = json_blob['metaData']['mosaicProviderJobCardsModel']['results']

            # with open(f'_____parse_search_results222222.json', 'w', encoding='utf-8') as file:
            #     json.dump(json_blob, file, indent=4, ensure_ascii=False)
            #
            # breakpoint()

            for index, job in enumerate(jobs_list):
                if job.get('jobkey') is not None:
                    job_url = 'https://www.indeed.com/m/basecamp/viewjob?viewtype=embedded&jk=' + job.get('jobkey')
                    yield scrapy.Request(url=job_url,
                                         callback=self.parse_job,
                                         meta={
                                             'keyword': keyword,
                                             'location': location,
                                             'page': round(offset / 10) + 1 if offset > 0 else 1,
                                             'position': index,
                                             'jobKey': job.get('jobkey'),
                                         })

            # Paginate Through Jobs Pages
            if offset == 0:
                meta_data = json_blob["metaData"]["mosaicProviderJobCardsModel"]["tierSummaries"]
                num_results = sum(category["jobCount"] for category in meta_data)
                if num_results > 1000:
                    num_results = 50

                for offset in range(10, num_results + 10, 10):
                    url = self.get_indeed_search_url(keyword, location, offset)
                    yield scrapy.Request(url=url, callback=self.parse_search_results,
                                         meta={'keyword': keyword, 'location': location, 'offset': offset})

    def parse_job(self, response):
        location = response.meta['location']
        keyword = response.meta['keyword']
        page = response.meta['page']
        position = response.meta['position']
        script_tag = re.findall(r"_initialData=(\{.+?\});", response.text)
        if script_tag is not None:
            json_blob = json.loads(script_tag[0])

            # with open(f'_____parse_job.json', 'w', encoding='utf-8') as file:
            #     json.dump(json_blob, file, indent=4, ensure_ascii=False)

            current_dateTime = datetime.now()
            dev_ = '=== IN DEVELOPING ==='

            job = json_blob["jobInfoWrapperModel"]["jobInfoModel"]
            job_type_ = job["jobDescriptionSectionModel"]["jobDetailsSection"]["contents"]["Job Type"]
            job_type = job_type_[0] if job_type_[0] is not None else 'none'

            yield {
                'Job Title': job.get('jobInfoHeaderModel').get('jobTitle'),
                'Company Name': job.get('jobInfoHeaderModel').get('companyName'),
                'Location': job.get('jobInfoHeaderModel').get('formattedLocation'),
                'Job Type': job_type,
                'jobDescription': job.get('sanitizedJobDescription').get('content') if job.get('sanitizedJobDescription') is not None else '',
                'Email address': dev_,
                'Company Website URL': dev_,
                'Company Logo': job.get('jobInfoHeaderModel').get('companyImagesModel').get('logoUrl'),
                'Date fetched': current_dateTime,
                # 'keyword': keyword,
                # 'page': page,
                # 'position': position,
                # 'jobkey': response.meta['jobKey'],
            }
