from datetime import datetime, timedelta
from time import sleep, time
from pathlib import Path
from csv import writer
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

# Change saved values below. Pass the base url and label for data maintenance.
quick_url = 'https://www.otomoto.pl/osobowe/mercedes/?limit&page=42'

csv_headers = 'id,price,year,engine,fuel,mileage,brand,model,loc,url'

temp_path = Path('lib/temp.csv')
if not temp_path.exists():
    temp_path.touch()
    temp_path.write_text(csv_headers + '\n')


def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')


soup = get_soup(quick_url)


class Soup:
    def __init__(self, soup):
        self.soup = soup
        self.full_url = self.soup.find('a', href=True)['href']
        self.id = re.findall('(ID.*)(?:.html)', self.full_url)[0]
        self.url = 'https://www.otomoto.pl/pl/oferta/' + self.id
        # self.detail_soup = self.get_detail_soup()

    def get_detail_soup(self):
        response = requests.get(self.url)
        print(self.url, response.url)
        return BeautifulSoup(response.content, 'html.parser')


class OfferModel(Soup):
    def __init__(self, soup):
        super().__init__(soup)
        self.price = self.get_price('span', 'offer-price__number ds-price-number')
        self.brand = self.soup.find('a', 'offer-title__link')['title']
        self.year = self.get_basic('year')
        self.mileage = self.get_basic('mileage').rstrip(' km')
        self.engine = self.get_basic('engine_capacity').rstrip(' cm3')
        self.fuel = self.get_basic('fuel_type')
        self.model = 0
        self.loc = self.soup.find('span', 'ds-location-city').text + self.soup.find('span', 'ds-location-region').text

    def get_basic(self, select):
        try:
            return self.soup.find('li', {'data-code': select}).find('span').text
        except AttributeError:
            if select == 'mileage': return '0 km'
            elif select == 'engine_capacity': return '0 cm3'
            else: return 0

    def get_detail(self, select1, select2, text=None, regex=None):
        soup_select = self.detail_soup.findAll(select1, select2)
        if text is None:
            try:
                return self.detail_soup.find(select1, select2).text
            except AttributeError:
                return 0
        else:
            # print(soup_select)
            for i in range(len(soup_select)):
                if text in soup_select[i].text:
                    try:
                        # print(soup_select[i].text)
                        return re.findall(regex, soup_select[i].text)[0]
                    except IndexError:
                        # print('error')
                        return 0
                else:
                    pass

    def get_price(self, select_1, select_2):
        try:
            price = self.soup.find(select_1, select_2).text
            price = re.findall(r'(\d+\s*\d+\s*\d+\s*)', price)
            price = re.sub(r'\s', '', price[0])
            return int(price)
        except (AttributeError, IndexError):
            return 'ask for price'

    def csv_object(self):
        columns = (self.id, self.price, self.year, self.engine, self.fuel, self.mileage, self.brand,
                   self.model, self.loc, self.full_url)
        return columns


class Process:
    def __init__(self, url_site, query='test'):
        self.url_site = url_site
        self.query = query
        self.total = 0
        self.pagination()

    def validate_page(self):
        if '?' in self.url_site:
            url = re.sub(r'&page=\d*', '', self.url_site)
            if '&page=' in self.url_site:
                page_number = re.findall(r'(?<=&page=)\d*', self.url_site)
                return url, int(page_number[0])
            else:
                return url, 1
        else:
            return self.url_site + '?limit=250', 1

    def pagination(self):
        url, page = self.validate_page()
        while True:
            try:
                url_page = url.strip(' ') + '&page=' + str(page)
                print(url_page, end=' ')

                if page > 1 and url_page != requests.get(url_page).url:
                    raise KeyError
                else:
                    self.scrape_page(url_page)
                    page += 1

            except KeyError:
                print('Checked ' + str(page - 1) + ' pages.')
                break

    def scrape_page(self, url_page):
        search_url = requests.get(url_page)
        main_soup = BeautifulSoup(search_url.content, 'html.parser')
        self.iterate_search_results(main_soup.select('article.offer-item'))

    def iterate_search_results(self, soup_select):
        page_total = len(soup_select)
        print(str(page_total), 'listings found')
        print('+')
        if page_total == 0:
            raise KeyError
        else:
            self.total += page_total
        i = count = 0
        while i < len(soup_select):
            duplicates = pd.read_csv(temp_path, encoding='utf-8', usecols=['id'])
            offer = soup_select[i]

            soup = BeautifulSoup(str(offer), 'html.parser')
            offer = OfferModel(soup)

            # if offer.id in duplicates.index.values:
            if offer.id in duplicates['id'].values:
                print('> duplicate')
                count += 1
                i += 1
            else:
                row = offer.csv_object()
                print(row)
                with temp_path.open('a', newline='', encoding='utf-8') as temp:
                    csv_writer = writer(temp)
                    csv_writer.writerow(row)
                i += 1

        print('\n --> ' + str(count) + ' duplicates ' + str(page_total - count) + ' new offers ')
        sleep(0.01)


t = time()

Process(quick_url)

elapsed = time() - t
time_format = timedelta(seconds=elapsed)
print('>>> Executed in {} s'.format(time_format, 2))

# def write_and_clean(loc):
#     df = prepare_df(temp_path)
#     create_db(df, loc)
#     if Path(loc).exists():
#         temp_path.unlink()


# def main():
#     try:
#         t = time()
#         timestamp = datetime.fromtimestamp(t).strftime('_%Y%m%d_%H_%M_%S')
#
#         url, label = args_parser()
#         process = Process(url, label)
#
#         loc = 'out/{}_{}_total{}.csv'.format(label, process.total, timestamp)
#         write_and_clean(loc)

