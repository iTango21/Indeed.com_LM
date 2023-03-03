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

    job_keys = []

    def get_indeed_search_url(self, keyword, location, offset=0):
        parameters = {"q": keyword, "l": location, "filter": 0, "start": offset}
        sc_ = '&sc=0bf%3Aexrec%28%29%3B'
        fromage_ = '&fromage=1'
        lang_ = '&lang=en'
        url_ = f"https://de.indeed.com/jobs?{urlencode(parameters)}{sc_}{fromage_}{lang_}"
        return url_

    def start_requests(self):
        keyword = 'english'
        location = ''

        indeed_jobs_url = self.get_indeed_search_url(keyword, location)
        yield scrapy.Request(url=indeed_jobs_url, callback=self.parse_search_results,
                             meta={'keyword': keyword, 'location': location, 'offset': 0})

    def parse_search_results(self, response):
        location = response.meta['location']
        keyword = response.meta['keyword']
        offset = response.meta['offset']

        script_tag = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', response.text)
        script_totalJobCount = re.findall(r'"totalJobCount":(.+?),"uniqueJobsCount"', response.text)

        if script_tag is not None:
            json_blob = json.loads(script_tag[0])

            # with open(f'_____parse_search_results_11111.json', 'w', encoding='utf-8') as file:
            #     json.dump(json_blob, file, indent=4, ensure_ascii=False)

            ## Extract Jobs From Search Page
            jobs_list = json_blob['metaData']['mosaicProviderJobCardsModel']['results']

            # with open(f'_____parse_search_results_22222.json', 'w', encoding='utf-8') as file:
            #     json.dump(jobs_list, file, indent=4, ensure_ascii=False)

            for index, job in enumerate(jobs_list):

                job_key_ = job.get('jobkey')

                if job_key_ is not None:
                    if job_key_ in self.job_keys:
                        print(f'\n\t\tLet`s skip! Such a key is already in the list.\n\n')
                    else:
                        self.job_keys.append(job_key_)
                        print(f'\n\t\t!!!!!!!!!!!!!!!!!! Job keys: {self.job_keys}\n\n')

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
                break

            # Paginate Through Jobs Pages
            if offset == 0:
                # meta_data = json_blob["metaData"]["mosaicProviderJobCardsModel"]["tierSummaries"]
                # num_results = sum(category["jobCount"] for category in meta_data)

                s = [str(integer) for integer in script_totalJobCount]
                a_string = "".join(s)
                num_results_ = int(a_string)
                num_results = round(num_results_ / 15) * 10

                print(f'\t-------------->>>>>>>>>>>>>  Found: {num_results_} jobs')

                if num_results > 100:
                    num_results = 100

                for offset in range(10, num_results + 10, 10):
                    url = self.get_indeed_search_url(keyword, location, offset)
                    yield scrapy.Request(url=url, callback=self.parse_search_results,
                                         meta={'keyword': keyword, 'location': location, 'offset': offset})


    def parse_job(self, response):
        # location = response.meta['location']
        # keyword = response.meta['keyword']
        # page = response.meta['page']
        # position = response.meta['position']
        jobKey = response.meta['jobKey']

        script_tag = re.findall(r"_initialData=(\{.+?\});", response.text)
        if script_tag is not None:
            json_blob = json.loads(script_tag[0])

            # with open(f'_____parse_job.json', 'w', encoding='utf-8') as file:
            #     json.dump(json_blob, file, indent=4, ensure_ascii=False)

            current_dateTime = datetime.now()
            dev_ = '=== IN DEVELOPING ==='

            job = json_blob["jobInfoWrapperModel"]["jobInfoModel"]

            try:
                job_type = job["jobDescriptionSectionModel"]["jobDetailsSection"]["contents"]["Job Type"][0]
                #job_type = job_type_[0] if job_type_[0] is not None else 'none'
            except:
                job_type = 'NONE'

            yield {
                'Job Title': job.get('jobInfoHeaderModel').get('jobTitle'),
                'Company Name': job.get('jobInfoHeaderModel').get('companyName'),
                'Location': job.get('jobInfoHeaderModel').get('formattedLocation'),
                'Job Type': job_type,
                #'Job Description': job.get('sanitizedJobDescription').get('content') if job.get('sanitizedJobDescription') is not None else '',
                'Email address': dev_,
                'Company Website URL': dev_,
                'Company Logo': job.get('jobInfoHeaderModel').get('companyImagesModel').get('logoUrl'),
                'Date fetched': current_dateTime,
                # 'keyword': keyword,
                # 'page': page,
                # 'position': position,
                # 'jobkey': response.meta['jobKey'],
            }

