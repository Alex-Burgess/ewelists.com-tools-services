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


class Product:

    def __init__(self, item):
        self.productId = item.get('productId').get('S')
        self.brand = item.get('brand').get('S')
        self.retailer = item.get('retailer').get('S')
        self.details = item.get('details').get('S')
        self.price = item.get('price').get('S')
        self.productUrl = item.get('productUrl').get('S')
        self.imageUrl = item.get('imageUrl').get('S')
        if item.get('priceCheckedDate'):
            self.priceCheckedDate = item.get('priceCheckedDate').get('S')
        if item.get('searchHidden'):
            self.searchHidden = item.get('searchHidden').get('BOOL')

    def __repr__(self):
        return "Product<{} -- {} -- {} -- {} -- {}>".format(self.productId, self.brand, self.details, self.productUrl, self.price)

    def get_product(self):
        product = {
            'productId': self.productId,
            'brand': self.brand,
            'retailer': self.retailer,
            'details': self.details,
            'price': self.price,
            'productUrl': self.productUrl,
            'imageUrl': self.imageUrl
        }

        if hasattr(self, 'priceCheckedDate'):
            product['priceCheckedDate'] = self.priceCheckedDate

        if hasattr(self, 'searchHidden'):
            product['searchHidden'] = self.searchHidden

        return product
