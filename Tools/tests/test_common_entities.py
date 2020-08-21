from tools.common_entities import Notfound
from tools import logger

log = logger.setup_test_logger()


class TestProduct:
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
