import os
import json
import pytest
import mock
from tools import check_details, logger

log = logger.setup_test_logger()


class TestHandler:
    @mock.patch("tools.check_details.post_request", mock.MagicMock(return_value=[{
      "product": {
        "brand": "Gaia Baby",
        "name": "Gaia Baby Serena Nursing Rocking Chair, Oat",
        "mainImage": "https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$",
        'images': [
            'https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$',
            'https://johnlewis.scene7.com/is/image/JohnLewis/238364338alt2?$rsp-pdp-port-1440$',
            'https://johnlewis.scene7.com/is/image/JohnLewis/238364338alt3?$rsp-pdp-port-1440$',
            'https://johnlewis.scene7.com/is/image/JohnLewis/238364338alt1?$rsp-pdp-port-1440$'
        ],
        "url":"https://www.johnlewis.com/gaia-baby-serena-nursing-rocking-chair-oat/p4797478",
        "offers":[{"price": "399.99", "currency": "£", "availability": "InStock"}],
        "probability": 0.9961216
      }
    }]))
    def test_check_details(self, api_check_details_event, monkeypatch, ssm_mock):
        monkeypatch.setitem(os.environ, 'API_KEY_PATH', '/Test/APIKey')

        response = check_details.handler(api_check_details_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body == {
            "retailer": "johnlewis.com",
            "brand": "Gaia Baby",
            "details": "Serena Nursing Rocking Chair, Oat",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$",
            "price": "399.99",
            "availability": "InStock"
        }, "Product object not correct."

    @mock.patch("tools.check_details.post_request", mock.MagicMock(return_value=[{
      "product": {
        "probability": 0.09
      }
    }]))
    def test_check_too_low_probability(self, api_check_details_event, monkeypatch, ssm_mock):
        monkeypatch.setitem(os.environ, 'API_KEY_PATH', '/Test/APIKey')

        response = check_details.handler(api_check_details_event, None)
        assert response['statusCode'] == 500
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body['error'] == 'API Query returned with too low probability.', "response did not contain the correct error message."


class TestCheckProbability:
    def test_greater_than_threshold(self, scraping_hub_response):
        assert check_details.check_probability(scraping_hub_response, '0.1'), "Response was not True"

    def test_lower_than_threshold(self, scraping_hub_response):
        scraping_hub_response['product']['probability'] = 0.01
        with pytest.raises(Exception) as e:
            check_details.check_probability(scraping_hub_response, '0.1')
        assert str(e.value) == "API Query returned with too low probability.", "Exception not as expected."


class TestParseDetails:
    def test_no_brand(self):
        data = {
            "details": "Gaia Baby Serena Nursing Rocking Chair, Oat",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$",
            "price": "399.99",
            "availability": "InStock"
        }

        return_details = check_details.parse_details(data)
        assert return_details == {
            "details": "Gaia Baby Serena Nursing Rocking Chair, Oat",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$",
            "price": "399.99",
            "availability": "InStock"
        }

    def test_no_details(self):
        data = {
            "brand": "Gaia Baby",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$",
            "price": "399.99",
            "availability": "InStock"
        }

        return_data = check_details.parse_details(data)
        assert return_data == {
            "brand": "Gaia Baby",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$",
            "price": "399.99",
            "availability": "InStock"
        }

    def test_no_details_update_required(self):
        data = {
            "brand": "Gaia Baby",
            "details": "Serena Nursing Rocking Chair, Oat",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$",
            "price": "399.99",
            "availability": "InStock"
        }

        return_data = check_details.parse_details(data)
        assert return_data == {
            "brand": "Gaia Baby",
            "details": "Serena Nursing Rocking Chair, Oat",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$",
            "price": "399.99",
            "availability": "InStock"
        }

    def test_details_update_required(self):
        data = {
            "brand": "Gaia Baby",
            "details": "Gaia Baby Serena Nursing Rocking Chair, Oat",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$",
            "price": "399.99",
            "availability": "InStock"
        }

        return_data = check_details.parse_details(data)
        assert return_data == {
            "brand": "Gaia Baby",
            "details": "Serena Nursing Rocking Chair, Oat",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$",
            "price": "399.99",
            "availability": "InStock"
        }


class TestCreateData:
    def test_create_data(self, scraping_hub_response):
        data = check_details.create_data(scraping_hub_response)
        assert data == {
            "brand": "Gaia Baby",
            "details": "Gaia Baby Serena Nursing Rocking Chair, Oat",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$",
            "price": "399.99",
            "availability": "InStock"
        }

    def test_missing_brand(self, scraping_hub_response):
        scraping_hub_response['product'].pop('brand', None)

        data = check_details.create_data(scraping_hub_response)
        assert data == {
            "details": "Gaia Baby Serena Nursing Rocking Chair, Oat",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$",
            "price": "399.99",
            "availability": "InStock"
        }

    def test_missing_availability(self, scraping_hub_response):
        scraping_hub_response['product']['offers'][0].pop('availability', None)

        data = check_details.create_data(scraping_hub_response)
        assert data == {
            "brand": "Gaia Baby",
            "details": "Gaia Baby Serena Nursing Rocking Chair, Oat",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$",
            "price": "399.99"
        }

    def test_missing_price(self, scraping_hub_response):
        scraping_hub_response['product']['offers'][0].pop('price', None)

        data = check_details.create_data(scraping_hub_response)
        assert data == {
            "brand": "Gaia Baby",
            "details": "Gaia Baby Serena Nursing Rocking Chair, Oat",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/238364338?$rsp-pdp-port-1440$",
            "availability": "InStock"
        }


class TestGetUrl:
    def test_get_url(self, api_check_details_event):
        url = check_details.get_url(api_check_details_event)
        assert url == "https://www.johnlewis.com/gaia-baby-serena-nursing-rocking-chair-oat/p4797478", "Url returned from API event was not as expected."

    def test_product_id_not_present(self, api_check_details_event):
        api_check_details_event['pathParameters'] = None

        with pytest.raises(Exception) as e:
            check_details.get_url(api_check_details_event)
        assert str(e.value) == "API Event did not contain a Url in the path parameters.", "Exception not as expected."


class TestGetKey:
    def test_get_key(self, ssm_mock):
        key = check_details.get_key('/Test/APIKey')
        assert key == "12345678"

    def test_path_does_not_exist(self, ssm_mock):
        with pytest.raises(Exception) as e:
            check_details.get_key('/Test2/APIKey')
        assert str(e.value) == "Could not retrieve API secret from parameter store.", "Exception not as expected."


class TestCallApi:
    @mock.patch("tools.check_details.post_request", mock.MagicMock(return_value=[{
      "product": {
        "name": "A Light in the Attic",
        "description": "It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary with this special edition. Silverstein's humorous and creative verse can amuse the dowdiest of readers. Lemon-faced adults and fidgety kids sit still and read these rhythmic words and laugh and smile and love th It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary with this special edition. Silverstein's humorous and creative verse can amuse the dowdiest of readers. Lemon-faced adults and fidgety kids sit still and read these rhythmic words and laugh and smile and love that Silverstein. Need proof of his genius? RockabyeRockabye baby, in the treetopDon't you know a treetopIs no safe place to rock?And who put you up there,And your cradle, too?Baby, I think someone down here'sGot it in for you. Shel, you never sounded so good. ...more",
        "mainImage": "http://books.toscrape.com/media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg",
        "images": ["http://books.toscrape.com/media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg"],
        "url":"http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "offers":[{"price": "51.77", "currency": "£", "availability": "InStock"}],
        "probability": 0.9961216
      }
    }]))
    def test_get_key(self):
        url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
        key = "123456768"
        response = check_details.call_api(url, key)
        assert response['product']['name'] == "A Light in the Attic"

    @mock.patch("tools.check_details.post_request", mock.MagicMock(return_value={"title": "Authentication token not provided or invalid", "type": "http://errors.xod.scrapinghub.com/unauthorized.html"}))
    def test_no_api_key(self):
        url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
        key = "123456768"

        with pytest.raises(Exception) as e:
            check_details.call_api(url, key)
        assert str(e.value) == "there was an issue with the Scrape Hub API call.", "Exception not as expected."
