

class Post:
    def __init__(self, postId, itemId, price, duration, post_quanity, stack):
        self.postId = postId
        self.itemId = itemId
        self.price = price
        self.duration = duration
        self.post_quanity = post_quanity
        self.stack = stack


    def toString(self):
        string = (
            '\nPOST ID: ' + str(self.postId) +
            '\nITEM ID: ' + str(self.itemId) +
            '\nPRICE: ' + str(self.price) +
            '\nDURATION: ' + str(self.duration) +
            '\nQUANTITY: ' + str(self.quantity))
        return string

    def __eq__(self, other):
        return self.postId == other.postId