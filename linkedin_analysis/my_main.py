import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def main():
    config = CrawlerRunConfig(
        # e.g., first 30 items from Hacker News
        css_selector="jobs-search__job-details--container"
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.linkedin.com/jobs/search/?currentJobId=4195690629&geoId=106343449&keywords=data%20scientist&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true",
            config=config,
        )
        print("Partial HTML length:", len(result.cleaned_html))

if __name__ == "__main__":
    asyncio.run(main())