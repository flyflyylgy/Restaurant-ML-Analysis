import scrapy

class TaobaoItem(scrapy.Item):
    title = scrapy.Field()       # 商品标题
    price = scrapy.Field()      # 商品价格
    sales = scrapy.Field()      # 销量
    shop = scrapy.Field()       # 店铺名称
    link = scrapy.Field()       # 商品链接
    image = scrapy.Field()      # 商品图片