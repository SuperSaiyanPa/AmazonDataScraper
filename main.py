from flask import Flask, jsonify, request
from am_scrapper import Scrapper
import logging
import requests

# amazon url
url = "https://www.amazon.in/s?"
# request header
headers = ({'User-Agent': '', 'Accept-Language': 'en-US, en;q=0.5'})

app = Flask(__name__)
logging.basicConfig(filename='.\\logs\\record.log', level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


@app.route("/get_items", methods=["GET"])
def get_product_data():
    """
    method search and extract the given item from amazon
    :return: all matching items
    """
    app.logger.info('Info level log')
    app.logger.warning('Warning level log')

    try:
        item_name = request.args.get('item_name')
        pages = int(request.args.get('pages'))
        sc = Scrapper(url + f"k={item_name}", headers, logging)
        prod = sc.scrape_data(pages)
    except Exception as e:
        logging.error(e)
        return jsonify({
            "message": "un handled exception occurs",
            "error": str(e),
            "products": None
        }), 500
    else:
        return jsonify({
            "message": "successfully fetched all data",
            "products": prod
        }), 200


if __name__ == '__main__':
    app.run(port=8081)

    # print(requests.get("http://localhost:8081/get_items", params={'item_name': "tea", 'pages': 3}).text)
