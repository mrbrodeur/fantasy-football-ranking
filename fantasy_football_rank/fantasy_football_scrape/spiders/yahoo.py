import scrapy
from scrapy_playwright.page import PageMethod

class FantasyProsSpider(scrapy.Spider):
    name = "fantasypros"
    allowed_domains = ["partners.fantasypros.com"]
    weeks = range(1,14)
    positions = ['QB', 'RB', 'WR', 'TE', 'FLX', 'OP', 'DST', 'K',]
    #positions = ['ALL', 'QB', 'RB', 'WR', 'TE', 'FLX', 'OP', 'DST', 'K', 'IDP', 'DL', 'IDL', 'DE', 'EDGE', 'DT', 'LB', 'DB', 'CB', 'S', 'OT', 'IOL', 'OG', 'C', 'P', 'RK', 'TQB', 'TRB', 'TWR', 'TTE', 'TK', 'HC', 'TOL', '1', '2', '3', '4', '5', '6', '7']

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_HANDLERS': {
                "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            },
        'TWISTED_REACTOR': "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }

    def start_requests(self):
        for week in self.weeks:
            print("week: ", week)
            for position in self.positions:
                meta = {
                    'playwright': True,
                    'position': position,
                    'week': week,
                }
                url = f"https://partners.fantasypros.com/external/widget/fp-widget.php?sport=NFL&wtype=ST&filters=7%3A9%3A285%3A747%3A2578%3A4338&scoring=HALF&expert=1663&affiliate_code=&year=2024&week={week}&auction=false&Notes=false&tags=false&cards=true&showPodcastIcons=false&format=table&promo_link=true&title_header=true&positions={position}&ppr_positions=&half_positions=&site=&fd_aff=&dk_aff=&fa_aff=&dp_aff=&hide_expert_columns=false&"
                yield scrapy.Request(url, meta=meta)

    def parse(self, response):
        experts = response.xpath("//thead/tr/th[@data-sort-method='number']/a/text()").getall()
        if 'FPROS All Experts' in experts: experts.remove('FPROS All Experts')
        num_experts = len(experts)

        contains_position = False
        if response.xpath("//thead/tr/th[4]/text()").get() == 'Pos':
            contains_position = True

        print("position: ", response.meta['position'], " // contains_position: ", contains_position)

        players = response.xpath("//tbody/tr")
        
        # print(players[0])

        for player in players:
            cells = player.xpath(".//td")

            player_yield = {
                'week': response.meta['week'],
                'position': response.meta['position'],
                'name': cells[1].xpath(".//text()").get(),
                'overall_rank': cells[0].xpath(".//text()").get(),
            }

            expert_column_offset = 3
            if contains_position:
                expert_column_offset = 4                

            for i in range(num_experts):
                player_yield[experts[i]] = cells[i+expert_column_offset].xpath(".//text()").get()

            yield player_yield
