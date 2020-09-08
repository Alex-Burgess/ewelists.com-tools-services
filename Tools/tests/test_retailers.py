from tools import retailers, logger

log = logger.setup_test_logger()


class TestGetRetailer:
    def test_jl_retailer(self):
        retailer = retailers.get("https://www.johnlewis.com/lego-creator-10271-fiat-500/p5023360")
        assert retailer == "johnlewis.com", "retailer was not as expected."

    def test_amazon_retailer(self):
        retailer = retailers.get("https://www.amazon.co.uk/East-Coast-Clara-Dresser-White/dp/B001WAK4VM/ref=as_li_ss_il?ie=UTF8&linkCode=li3&tag=ewelists-21&linkId=fc437977b70d0f8c33f61e798569caa5&language=en_GB")
        assert retailer == "amazon.co.uk", "retailer was not as expected."

    def test_amazon_short_link(self):
        retailer = retailers.get("https://amzn.to/32Q7cVR")
        assert retailer == "amazon.co.uk", "retailer was not as expected."
