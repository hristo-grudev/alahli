import html
import json
import re

import scrapy

from scrapy.loader import ItemLoader
from w3lib.html import remove_tags

from ..items import AlahliItem
from itemloaders.processors import TakeFirst
import requests

url = "https://www.alahli.com/_layouts/15/NCB.SharePoint.WebParts.News/NewsService.asmx/GetNews"

payload="{\"spQuery\":\"<Where><And><And><And><Geq><FieldRef Name='News_x0020_Date' /><Value Type='DateTime' IncludeTimeValue='FALSE'>2014-01-01T00:00:00Z</Value></Geq><Leq><FieldRef Name='News_x0020_Date' /><Value Type='DateTime' IncludeTimeValue='FALSE'>2222-12-31T00:00:00Z</Value></Leq></And><Neq><FieldRef Name='Title' /><Value Type='Text'>News Overview</Value></Neq></And><Eq><FieldRef Name=\\\"IsArchive\\\" /><Value Type=\\\"Integer\\\">1</Value></Eq></And></Where><OrderBy><FieldRef Name='News_x0020_Date' Ascending='FALSE' /></OrderBy>\",\"ln\":\"Pages\",\"hostSiteUrl\":\"/ar-SA/about-us/News\"}"
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'Accept': '*/*',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
  'Content-Type': 'application/json',
  'Origin': 'https://www.alahli.com',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.alahli.com/ar-sa/about-us/news/Pages/News-Overview.aspx',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': 'NCB_Cookie=u0021kX+lk0000WB+4vFcLhmLDprvG284cDMaApw+VQrRhgxXrivsPte2zJ1EK83Paf1jHIB1APMZNXNIB30D5Un5sCuaDg9yNcgB9TNqYt8=; _ga=GA1.2.1133761850.1619178597; _gid=GA1.2.1138323743.1619178597; _scid=6fb86227-ff76-427c-854d-81078fca80da; WSS_FullScreenMode=false; TS01711cbd=0134df0051ef07d7e4bbf68279147f332e00dea895045fb8e3709772357dcbbffc6152a1de2908d9e3eee48381b64ac6c7c021028945dbfb29a308d23137740e7083b0f664; _gat=1; NCB_Cookie=!4YdolLRzSEyg5VZcLhmLDprvG284cJ2wcE1rdy93A/OgX93XWTmxSQZzOC4gTYVFw9qpnf8XhG7PCfuZcuk0Y4Y3OGvL1uZ4nz+C5Cw=; TS01711cbd=0134df0051c8ea568329b9390bcc825e147b7441aa045fb8e3709772357dcbbffc6152a1de2908d9e3eee48381b64ac6c7c02102892cce22999eeb853ae492a848c649fd18'
}


class AlahliSpider(scrapy.Spider):
	name = 'alahli'
	start_urls = ['https://www.alahli.com/ar-sa/about-us/news/Pages/News-Overview.aspx']

	def parse(self, response):
		data = requests.request("POST", url, headers=headers, data=payload)
		data = json.loads(data.text)['d']['news']
		post_links = re.findall(r':row\s(.*?)<z', data, re.DOTALL)
		for post in post_links:
			title = re.findall(r'ows_Title(.*)ows_PublishingPageLayout', post, re.DOTALL)[0][2:-2]
			description = re.findall(r'ows_News_x0020_Content(.*?)ows_Display_x0020', post, re.DOTALL)[0][1:-2]
			description = remove_tags(html.unescape(description))
			date = re.findall(r'ows_News_x0020_Date=(.*?)ows', post, re.DOTALL)[0][1:-2]

			item = ItemLoader(item=AlahliItem(), response=response)
			item.default_output_processor = TakeFirst()
			item.add_value('title', title)
			item.add_value('description', description)
			item.add_value('date', date)

			yield item.load_item()
