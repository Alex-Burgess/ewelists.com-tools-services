import pytest
import json
import mock
from tools import url_metadata, logger

log = logger.setup_test_logger()


# @pytest.fixture
# def query_response_full():
#     return {
#         "site_name": "The  White Company UK",
#         "title": "Snowman Knitted Romper | Newborn & Unisex | The  White Company",
#         "image": "https://whitecompany.scene7.com/is/image/whitecompany/Snowman-Knitted-Romper/SNTOO_15_MAIN_P?$D_PDP_412x525$",
#         "product:price:amount": "34.0",
#         "product:price:currency": "GBP"
#     }
#
#
# @pytest.fixture
# def parse_response_full():
#     return {
#         "site_name": "The  White Company UK",
#         "title": "Snowman Knitted Romper | Newborn & Unisex | The  White Company",
#         "image": "https://whitecompany.scene7.com/is/image/whitecompany/Snowman-Knitted-Romper/SNTOO_15_MAIN_P?$D_PDP_412x525$",
#         "price": "34.0",
#         "currency": "GBP"
#     }
#
#
# @pytest.fixture
# def query_response_no_price():
#     return {
#         "site_name": "The  White Company UK",
#         "title": "Snowman Knitted Romper | Newborn & Unisex | The  White Company",
#         "image": "https://whitecompany.scene7.com/is/image/whitecompany/Snowman-Knitted-Romper/SNTOO_15_MAIN_P?$D_PDP_412x525$"
#     }
#
#
# @pytest.fixture
# def parse_response_no_price():
#     return {
#         "site_name": "The  White Company UK",
#         "title": "Snowman Knitted Romper | Newborn & Unisex | The  White Company",
#         "image": "https://whitecompany.scene7.com/is/image/whitecompany/Snowman-Knitted-Romper/SNTOO_15_MAIN_P?$D_PDP_412x525$"
#     }


class TestHandler:
    @mock.patch("tools.url_metadata.query", mock.MagicMock(return_value={
      "og": {
        "title": "Snowman Knitted Romper | Newborn & Unisex | The  White Company",
        "description": "The perfect Christmas gift, our bestselling cosy knitted bodysuit has adorable pom-poms at the front to mimic a chilly snowman. With fastenings on the shoulder and leg openings, changing baby is easy. The bodysuit is footless with long sleeves and looks even cuter when paired with our novelty Snowman Hat for a complete outfit. Design & Fit \u2022 Long-sleeved romper \u2022 Pom-poms down the front \u2022 Button fastening on shoulder and legs \u2022 Pair with matching hat for full outfit Fabric & Care \u2022 100% cotton \u2022 Machine wash \u2022 Safety warning: keep away from fire See more: Newborn, The Little White Company",
        "image": "https://whitecompany.scene7.com/is/image/whitecompany/Snowman-Knitted-Romper/SNTOO_15_MAIN_P?$D_PDP_412x525$",
        "image:width": "200",
        "image:height": "200",
        "url": "https://www.thewhitecompany.com/uk/Snowman-Knitted-Romper/p/SNTOO?swatch=White",
        "type": "product",
        "locale": "en_GB",
        "site_name": "The  White Company UK"
      },
      "meta": {
        "description": "The perfect Christmas gift, our bestselling cosy knitted bodysuit has adorable pom-poms at the front to mimic a chilly snowman. With fastenings on the shoulder and leg openings, changing baby is easy. The bodysuit is footless with long sleeves and looks even cuter when paired with our novelty Snowman Hat for a complete outfit. Design & Fit \u2022 Long-sleeved romper \u2022 Pom-poms down the front \u2022 Button fastening on shoulder and legs \u2022 Pair with matching hat for full outfit Fabric & Care \u2022 100% cotton \u2022 Machine wash \u2022 Safety warning: keep away from fire See more: Newborn, The Little White Company",
        "product:price:amount": "34.0",
        "product:price:currency": "GBP",
        "": [
          "Snowman Knitted Romper | Newborn & Unisex | The  White Company",
          "The perfect Christmas gift, our bestselling cosy knitted bodysuit has adorable pom-poms at the front to mimic a chilly snowman. With fastenings on the shoulder and leg openings, changing baby is easy. The bodysuit is footless with long sleeves and looks even cuter when paired with our novelty Snowman Hat for a complete outfit. Design & Fit \u2022 Long-sleeved romper \u2022 Pom-poms down the front \u2022 Button fastening on shoulder and legs \u2022 Pair with matching hat for full outfit Fabric & Care \u2022 100% cotton \u2022 Machine wash \u2022 Safety warning: keep away from fire See more: Newborn, The Little White Company",
          "https://whitecompany.scene7.com/is/image/whitecompany/Snowman-Knitted-Romper/SNTOO_15_MAIN_P?$D_PDP_412x525$",
          "200",
          "https://www.thewhitecompany.com/uk/Snowman-Knitted-Romper/p/SNTOO?swatch=White",
          "product",
          "en_GB",
          "The  White Company UK",
          "1851456161814830"
        ]
      },
      "dc": {},
      "page": {
        "title": "Snowman Knitted Romper | Newborn & Unisex | The  White Company UK",
        "canonical": "https://www.thewhitecompany.com/uk/Snowman-Knitted-Romper/p/SNTOO"
      }
    }))
    def test_all_data_found(self, api_query_metadata_event):
        response = url_metadata.handler(api_query_metadata_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body == {
            "site_name": "The  White Company UK",
            "title": "Snowman Knitted Romper",
            "image": "https://whitecompany.scene7.com/is/image/whitecompany/Snowman-Knitted-Romper/SNTOO_15_MAIN_P?$D_PDP_412x525$",
            "price": "34.00",
            "currency": "GBP"
        }

    @mock.patch("tools.url_metadata.query", mock.MagicMock(return_value={
      'og': {},
      'meta': {
        'description': 'Buy Aqua Mini Micro Deluxe Scooter, 2-5 years from our Wheeled Toys & Bikes range at John Lewis & Partners. Free Delivery on orders over £50.',
        'og:image': 'https://johnlewis.scene7.com/is/image/JohnLewis/235862595?',
        'og:type': 'product',
        'og:title': 'Mini Micro Deluxe Scooter, 2-5 years, Aqua',
        'og:locale': 'en_GB',
        'og:image:type': 'image/jpeg',
        'og:url': 'https://www.johnlewis.com/mini-micro-deluxe-scooter-2-5-years/aqua/p3567221',
        'og:description': 'Buy Aqua Mini Micro Deluxe Scooter, 2-5 years from our Wheeled Toys & Bikes range at John Lewis & Partners. Free Delivery on orders over £50.',
        'og:site-name': 'John Lewis'
      },
      'dc': {},
      'page': {
        'title': 'Mini Micro Deluxe Scooter, 2-5 years at John Lewis & Partners',
        'canonical': 'https://www.johnlewis.com/mini-micro-deluxe-scooter-2-5-years/p3567221'
      }
    }))
    def test_no_price_in_data(self, api_query_metadata_event):
        response = url_metadata.handler(api_query_metadata_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body == {
            "site_name": "John Lewis",
            "title": "Mini Micro Deluxe Scooter, 2-5 years, Aqua",
            "image": "https://johnlewis.scene7.com/is/image/JohnLewis/235862595?"
        }

    @mock.patch("tools.url_metadata.query", mock.MagicMock(return_value={
        'og': {},
        'meta': {},
        'dc': {},
        'page': {}
    }))
    def test_no_data_found(self, api_query_metadata_event):
        response = url_metadata.handler(api_query_metadata_event, None)
        assert response['statusCode'] == 200
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body == {}

    def test_blocked_url(self, api_query_metadata_event):
        api_query_metadata_event['pathParameters'] = {'url': 'https%3A%2F%2Fwww.amazon.co.uk%2FBABYBJ%C3%96RN-Bouncer-Bliss-Jersey-Friends%2Fdp%2FB07NNTZGPS%3Fref_%3Dast_sto_dp'}
        response = url_metadata.handler(api_query_metadata_event, None)
        assert response['statusCode'] == 500
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body['error'] == 'Metadata query failed.'

    def test_not_authorized_url(self, api_query_metadata_event):
        api_query_metadata_event['pathParameters'] = {'url': 'https%3A%2F%2Fwww.jdsports.co.uk%2Fproduct%2Fred-adidas-wales-2020-home-shirt-junior%2F15963540%2F'}
        response = url_metadata.handler(api_query_metadata_event, None)
        assert response['statusCode'] == 500
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

        body = json.loads(response['body'])
        assert body['error'] == 'Metadata query failed.'


class TestParseData:
    def test_wc(self, metadata_response_wc):
        data = url_metadata.parse_data(metadata_response_wc)
        assert data == {
            "site_name": "The  White Company UK",
            "title": "Snowman Knitted Romper",
            "image": "https://whitecompany.scene7.com/is/image/whitecompany/Snowman-Knitted-Romper/SNTOO_15_MAIN_P?$D_PDP_412x525$",
            "price": "34.00",
            "currency": "GBP"
        }

    def test_jl(self, metadata_response_jl):
        data = url_metadata.parse_data(metadata_response_jl)
        assert data == {
            "site_name": "John Lewis",
            "title": "Mini Micro Deluxe Scooter, 2-5 years, Aqua",
            "image": "https://johnlewis.scene7.com/is/image/JohnLewis/235862595?"
        }

    def test_jojo(self, metadata_response_jojo):
        data = url_metadata.parse_data(metadata_response_jojo)
        assert data == {
            "site_name": "JoJo Maman Bebe",
            "title": "Kids' Penguin Towelling Dressing Gown",
            "image": "https://www.jojomamanbebe.co.uk/media/catalog/product/cache/e8cfbc35dc14c111e189893c9b8f265c/h/1/h1182_e2883.jpg",
            "price": "18.00",
            "currency": "GBP"
        }

    def test_gltc(self, metadata_response_gltc):
        data = url_metadata.parse_data(metadata_response_gltc)
        assert data == {
            "site_name": "Great Little Trading Co.",
            "title": "Woodland Christmas Advent Calendar",
            "image": "https://cdn.shopify.com/s/files/1/2341/5115/products/l4978_1_1200x1200.png?v=1603200782",
            "price": "45.00",
            "currency": "GBP"
        }

    def test_sb(self, metadata_response_sb):
        data = url_metadata.parse_data(metadata_response_sb)
        assert data == {
            "site_name": "Scandibørn",
            "title": "Plum Play Discovery Woodland Treehouse",
            "image": "https://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-320911_grande.jpg?v=1584688457",
            "price": "399.95",
            "currency": "GBP"
        }

    def test_mp(self, metadata_response_mp):
        data = url_metadata.parse_data(metadata_response_mp)
        assert data == {
            "site_name": "Mamas & Papas",
            "title": "Santa Christmas Jumper",
            "image": "https://media.mamasandpapas.com/i/mamasandpapas/S22LXY2_HERO_SANTA XMAS JUMPER",
            "price": "14.25",
            "currency": "GBP"
        }

    def test_k(self, metadata_response_k):
        data = url_metadata.parse_data(metadata_response_k)
        assert data == {
            "site_name": "KIDLY",
            "title": "The KIDLY Label Recycled Gilet",
            "image": "https://kidlycatalogue.blob.core.windows.net/products/9993/product-images/brown-toffee-1/kidly-puffa-gilet-brown-toffee-500x500_02.jpg"
        }

    def test_empty(self):
        metadata = {
            'og': {},
            'meta': {},
            'dc': {},
            'page': {}
        }
        data = url_metadata.parse_data(metadata)
        assert data == {}


class TestUpdateResponse:
    def test_add_to_empty_response(self):
        assert url_metadata.update_response({}, 'site_name', 'new value') == 'new value'

    def test_add_to_exist_response(self):
        assert url_metadata.update_response({'site_name': 'Existing value'}, 'site_name', 'new value') == 'Existing value'

    def test_add_array(self):
        assert url_metadata.update_response({}, 'image', ['new value1', 'new value2']) == 'new value1'

    def test_add_existing_array(self):
        assert url_metadata.update_response({'image': 'existing image'}, 'image', ['new value1', 'new value2']) == 'existing image'


class TestExceptionRules:
    def test_get_site_name_from_page_title(self, metadata_response_jojo):
        value = url_metadata.get_site_name_from_page_title(metadata_response_jojo)
        assert value == 'JoJo Maman Bebe'

    def test_check_price(self):
        assert url_metadata.check_price('34') == '34.00'
        assert url_metadata.check_price('34.0') == '34.00'
        assert url_metadata.check_price('34.5') == '34.50'

    def test_check_title(self):
        assert url_metadata.check_title('Snowman Knitted Romper') == 'Snowman Knitted Romper'
        assert url_metadata.check_title('Snowman Knitted Romper | Newborn & Unisex | The  White Company') == 'Snowman Knitted Romper'

    def test_check_title_regex_rules(self):
        assert url_metadata.check_title_regex_rules('Buy the KIDLY Label Recycled Gilet at KIDLY UK') == 'The KIDLY Label Recycled Gilet'


class TestGetUrl:
    def test_get_url(self, api_query_metadata_event):
        url = url_metadata.get_url(api_query_metadata_event)
        assert url == "https://www.thewhitecompany.com/uk/Snowman-Knitted-Romper/p/SNTOO", "Url returned from API event was not as expected."

    def test_product_id_not_present(self, api_query_metadata_event):
        api_query_metadata_event['pathParameters'] = None

        with pytest.raises(Exception) as e:
            url_metadata.get_url(api_query_metadata_event)
        assert str(e.value) == "API Event did not contain a Url in the path parameters.", "Exception not as expected."


class TestBlockedUrls:
    def test_not_blocked(self):
        assert not url_metadata.blocked_urls('https://www.thewhitecompany.com/uk/Snowman-Knitted-Romper/p/SNTOO')

    def test_amazon_blocked(self):
        with pytest.raises(Exception) as e:
            url_metadata.blocked_urls('https://www.amazon.co.uk/dp/B01H24LM58/ref=tsm_1_fb_lk')
        assert str(e.value) == "Metadata query failed.", "Exception not as expected."


class TestQuery:
    @pytest.mark.skip("Can't find a way to effectively mock the MetadataParser returned object and the helper functions are too useful to just use the raw metadata.")
    def test_query_url(self, metadata_response_wc):
        result = url_metadata.query('https://www.thewhitecompany.com/uk/Snowman-Knitted-Romper/p/SNTOO')
        assert result == metadata_response_wc

    def test_query_returns_error(self):
        with pytest.raises(Exception) as e:
            url_metadata.query('https://www.amazon.co.uk/dp/B01H24LM58/ref=tsm_1_fb_lk')
        assert str(e.value) == "Metadata query failed.", "Exception not as expected."
