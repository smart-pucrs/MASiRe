import json
class Photo:

    def __init__(self, id: int, size: int, victims: list, location: list):
        """
        [Object <Consumable> that represents a photography,
        resultant of a 'photograph' action over a flood instance.]

        :param size: Amount of virtual space that a photo instance
        costs over the virtual storage of an agent.
        :param victims: List of possible associated victims.
        :param node: Representation of the location where the photo
        instance was taken.
        """

        self.id = id
        self.type: str = 'photo'
        self.size: int = size
        self.victims: list = victims
        self.location: list = location
        self.active: bool = False

    def json(self):
        victims = [victim.json() for victim in self.victims if victim.active]
        copy = self.__dict__.copy()
        copy['victims'] = victims
        del copy['active']
        copy['location'] = {'lat': copy['location'][0], 'lon': copy['location'][1]}
        return copy

    def json_file(self):
        copy = self.__dict__.copy()
        del copy['active']
        del copy['type']
        copy['victims'] = [victim.json_file() for victim in copy['victims']]
        return copy

    ###################### TEMPORARY CODE #########################
    def __repr__(self):
        copy = self.__dict__.copy()
        copy['victims'] = [v.json_file() for v in copy['victims']]
        return json.dumps(copy)