import os
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, LLMExtractionStrategy
from models.job_info import JobDescription


async def crawl_job_description():
    """
    Crawl job description from a given URL (Linkedin).
    """
    # initializing the crawler configurations
    browser_config = get_browser_config()
    llm_strategy = get_llm_strategy()
    session_id = "session_id"

    # Initializing state variables
    page_number = 1
    all_job_descriptions = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        while True:
            job_description_data, no_text_found = await fetch_and_process_page()


async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.linkedin.com/jobs/search/?currentJobId=4195690629&geoId=106343449&keywords=data%20scientist&origin=JOBS_HOME_KEYWORD_AUTOCOMPLETE&refresh=true"
        )
        print(result.markdown)


if __name__ == '__main__':
    asyncio.run(main())
