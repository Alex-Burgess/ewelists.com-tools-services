from tools.common_entities import Notfound, Product
from tools import logger

log = logger.setup_test_logger()


class TestNotfound:
    def test_get_details(self):
        item = {
            "productId": {"S": "12345678-notf-0010-1234-abcdefghijkl"},
            "createdBy": {"S": "12345678-user-0001-1234-abcdefghijkl"},
            "brand": {"S": "JL"},
            "details": {"S": "Safari Mobile"},
            "productUrl": {"S": "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165"}
        }

        product = Notfound(item).get_product()

        assert product == {
            "productId": "12345678-notf-0010-1234-abcdefghijkl",
            "createdBy": "12345678-user-0001-1234-abcdefghijkl",
            "brand": "JL",
            "details": "Safari Mobile",
            "productUrl": "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165"
        }, "Product object not correct."

    def test_get_all_details(self):
        item = {
            "productId": {"S": "12345678-notf-0020-1234-abcdefghijkl"},
            "createdBy": {"S": "12345678-user-0001-1234-abcdefghijkl"},
            "brand": {"S": "JL"},
            "details": {"S": "Safari Mobile"},
            "price": {"S": "9.00"},
            "imageUrl": {"S": "https://johnlewis.scene7.com/is/image/JohnLewis/002955092?$rsp-pdp-port-640$"},
            "productUrl": {"S": "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165"}
        }

        product = Notfound(item).get_product()

        assert product == {
            "productId": "12345678-notf-0020-1234-abcdefghijkl",
            "createdBy": "12345678-user-0001-1234-abcdefghijkl",
            "brand": "JL",
            "details": "Safari Mobile",
            "productUrl": "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/002955092?$rsp-pdp-port-640$",
            "price": "9.00"
        }, "Product object not correct."


class TestProduct:
    def test_get_details(self):
        item = {
            "productId": {"S": "12345678-prod-0010-1234-abcdefghijkl"},
            "brand": {"S": "John Lewis & Partners"},
            "retailer": {"S": "johnlewis.com"},
            "details": {"S": "Baby Sleeveless Organic GOTS Cotton Bodysuits, Pack of 5, White"},
            "price": {"S": "9.00"},
            "priceCheckedDate": {"S": "2020-08-27 16:00:00"},
            "productUrl": {"S": "https://www.johnlewis.com/john-lewis-partners-baby-sleeveless-organic-gots-cotton-bodysuits-pack-of-5-white/p3182352"},
            "imageUrl": {"S": "https://johnlewis.scene7.com/is/image/JohnLewis/002955092?$rsp-pdp-port-640$"}
        }

        product = Product(item).get_product()

        assert product == {
            "productId": "12345678-prod-0010-1234-abcdefghijkl",
            "brand": "John Lewis & Partners",
            "retailer": "johnlewis.com",
            "details": "Baby Sleeveless Organic GOTS Cotton Bodysuits, Pack of 5, White",
            "price": "9.00",
            "priceCheckedDate": "2020-08-27 16:00:00",
            "productUrl": "https://www.johnlewis.com/john-lewis-partners-baby-sleeveless-organic-gots-cotton-bodysuits-pack-of-5-white/p3182352",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/002955092?$rsp-pdp-port-640$"
        }, "Product object not correct."

    def test_get_details_with_search_hidden_flag(self):
        item = {
            "productId": {"S": "12345678-prod-0010-1234-abcdefghijkl"},
            "brand": {"S": "John Lewis & Partners"},
            "retailer": {"S": "johnlewis.com"},
            "details": {"S": "Baby Sleeveless Organic GOTS Cotton Bodysuits, Pack of 5, White"},
            "price": {"S": "9.00"},
            "priceCheckedDate": {"S": "2020-08-27 16:00:00"},
            "productUrl": {"S": "https://www.johnlewis.com/john-lewis-partners-baby-sleeveless-organic-gots-cotton-bodysuits-pack-of-5-white/p3182352"},
            "imageUrl": {"S": "https://johnlewis.scene7.com/is/image/JohnLewis/002955092?$rsp-pdp-port-640$"},
            "searchHidden": {"BOOL": True}
        }

        product = Product(item).get_product()

        assert product == {
            "productId": "12345678-prod-0010-1234-abcdefghijkl",
            "brand": "John Lewis & Partners",
            "retailer": "johnlewis.com",
            "details": "Baby Sleeveless Organic GOTS Cotton Bodysuits, Pack of 5, White",
            "price": "9.00",
            "priceCheckedDate": "2020-08-27 16:00:00",
            "productUrl": "https://www.johnlewis.com/john-lewis-partners-baby-sleeveless-organic-gots-cotton-bodysuits-pack-of-5-white/p3182352",
            "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/002955092?$rsp-pdp-port-640$",
            "searchHidden": True
        }, "Product object not correct."
