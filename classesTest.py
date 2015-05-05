class SlowCooker(object):
    foods = []
    def __init__(self, foods):
        self.foods = foods

class Dehydrator(object):
    foods = []
    def __init__(self, foods):
        self.foods = foods

class Foods(object):
    def __init__(self, name):
        self.name = name

class Jerky(Foods):
    temperature = 160
    cooktime = 240
    device = "dehydrator"

class Pineapple(Foods):
    temperature = 135
    cooktime = 480
    device = "dehydrator"

class BBQ(Foods):
    temperature = "low"
    cooktime = 480
    device = "slow cooker"

class TomatoSauce(Foods):
    temperature = "low"
    cooktime = 480
    device = "slow cooker"

class Dessert(Foods):
    temperature = "high"
    cooktime = 120
    device = "slow cooker"

dehydrate_food = [Jerky("Original Beef"), Pineapple("Rings")]
dehydrate_jobs = Dehydrator(dehydrate_food)
slowcook_food = [TomatoSauce("Meatballs"), BBQ("Pork Butt"), Dessert("Cherry Lava Cake")]
slowcook_jobs = SlowCooker(slowcook_food)

for foods in dehydrate_jobs.foods:
    print foods.name

for foods in slowcook_jobs.foods:
    print foods.name
