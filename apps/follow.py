
class followers():
    """
    Handle lights following another light
    A light can only follow one light, but many lights can follow the same
    """
    def __init__(self):
        self.f = []

    def add_follower(self, light, light_to_follow):
        for l in self.f:
            if l["name"] is not light_to_follow:
                if light in l["followers"]:
                    return False

        found = False
        for l in self.f:
            if l["name"] == light_to_follow:
                found = True
                l["followers"].append(light)
        if not found:
            a = {"name": light_to_follow, "followers": [light]}
            self.f.append(a)
        return True


    def get_followers(self, light):
        for l in self.f:
            if l["name"] == light:
                return l["followers"]

        return None

    def remove_follower(self, light, following_light):
        for l in self.f:
            if l["name"] == following_light:
                if light in l["followers"]:
                    l["followers"].remove(light)
                    return True
                else:
                    return False
