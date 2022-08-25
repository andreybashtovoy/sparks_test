import bs4
import requests
from flask import Flask
from multiprocessing import Pool

from config import database_uri
from models import db, Offer

app = Flask(__name__, static_url_path='',
            static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
db.init_app(app)


def proceed_page(page):
    print(f'Page: {page}')
    html = requests.get(f'https://www.olx.ua/uk/transport/legkovye-avtomobili/?page={page}&order=created_at:desc').text
    soup = bs4.BeautifulSoup(html, 'html.parser')

    for elem in soup.find_all(class_="offer-wrapper"):
        try:
            price = int(elem.find(class_="price").text.strip().replace(" ", "").split('грн')[0])
        except ValueError:
            price = None

        details_elem = elem.find(class_='detailsLink')
        details_link = details_elem['href']

        with app.app_context():
            offer = Offer.query.filter(Offer.details_link == details_link).first()

        if offer is not None:
            continue

        details_html = requests.get(details_link).text

        img_src = details_elem.find('img')['src'] if details_elem.find('img') else 'https://via.placeholder.com/300'

        ds = bs4.BeautifulSoup(details_html, 'html.parser')
        e = ds.find(class_='css-1rbjef7-Text')
        seller_name = e.text.strip() if e is not None else ""

        ne = ds.find(class_='css-r9zjja-Text')
        name = ne.text.strip() if ne is not None else ""

        with app.app_context():
            db.session.add(Offer(
                details_link=details_link,
                seller_name=seller_name,
                name=name,
                image_link=img_src,
                price=price
            ))

            db.session.commit()

            print(f'Saved: {name}')


if __name__ == '__main__':
    with Pool(16) as pool:
        res = pool.map(proceed_page, range(24))
