import scrapy
import re

class FootballdbSpider(scrapy.Spider):
    name = "footballdb"
    allowed_domains = ["www.footballdb.com"]
    start_urls = ["https://www.footballdb.com/games/index.html"]

    custom_settings = {
        'DOWNLOAD_DELAY': .25,
        'ROBOTSTXT_OBEY': False,
    }

    custom_headers = {
            "Sec-Ch-Ua-Platform": "\"Linux\"",
            "User-Agent": "Mozilla/5.0 (Linux; x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            }
    

    def return_kicker(self, kicker, week):
        '''
        Parses the cells from the table for each kicker in the "Kicking" section in the boxscore
        1 point for a PAT
        3 points for FG under 40 yds
        4 points for FG 40-49 yds
        5 points for FG 50+ yds
        '''
        one_point = int(re.sub(r'/\d', '', kicker[1].xpath(".//text()").get()))
        three_points = 0
        for fg in kicker[3:6]:
            three_points += int(re.sub(r'/\d', '', fg.xpath(".//text()").get()))
        four_points = int(re.sub(r'/\d', '', kicker[6].xpath(".//text()").get()))
        five_points = int(re.sub(r'/\d', '', kicker[7].xpath(".//text()").get()))
            
        return {
            'week': week,
            'position': 'K',
            'name': kicker[0].xpath(".//span/a/text()").get(),
            'points': one_point + three_points*3 + four_points*4 + five_points*5,
        }
    

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers=self.custom_headers, callback=self.parse)


    def parse(self, response):
        weeks = response.xpath("//div[@class='ltbluediv']")
        for week in weeks:
            weeknumber = int(re.sub(r'\D', '', week.xpath(".//span/text()").get()))
            game_links = week.xpath(".//following-sibling::table[1]/tbody/tr//a/@href").getall()
            
            for link in game_links:
                yield response.follow(
                    link, 
                    headers=self.custom_headers, 
                    callback=self.parse_boxscore, 
                    meta={'week': weeknumber}
                    )


    def parse_boxscore(self, response):
        kicker_header = response.xpath("//div[@class='divider']/h2[contains(text(), 'Kicking')]/parent::div")
        yield self.return_kicker(kicker_header.xpath(".//following-sibling::*[1]/table/tbody/tr/td"), response.meta.get('week'))    
        yield self.return_kicker(kicker_header.xpath(".//following-sibling::*[2]/table/tbody/tr/td"), response.meta.get('week'))

        
