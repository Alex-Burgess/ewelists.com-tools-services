class Notfound:

    def __init__(self, item):
        self.productId = item.get('productId').get('S')
        self.createdBy = item.get('createdBy').get('S')
        self.brand = item.get('brand').get('S')
        self.details = item.get('details').get('S')
        self.productUrl = item.get('productUrl').get('S')

    def __repr__(self):
        return "Product<{} -- {} -- {} -- {} -- {}>".format(self.productId, self.brand, self.details, self.productUrl, self.createdBy)

    def get_product(self):
        product = {
            'productId': self.productId,
            'createdBy': self.createdBy,
            'brand': self.brand,
            'details': self.details,
            'productUrl': self.productUrl
        }

        return product
