class Food:
    def __init__(self, name):
        self.name = name
        self.createdate = datetime.now()

class Device:
    def __init__(self, name, temp_gauge):
        self.name = name
        self.temp_gauge = temp_gauge
        self.createdate = datetime.now()

class User:
    def __init__(self, username, fullname, email_address, password)
        self.username = username
        self.fullname = fullname
        self.email_address = email_address
        self.password = password
        self.createdate = datetime.now()

class CookJob:
    def __init__(self, food_id, device_id, user_id, cooktime, starttime):
        self.device = device_id
        self.food = food_id
        self.user = user_id
        self.cooktime = cooktime
        self.starttime = starttime
        self.createdate = datetime.now()
