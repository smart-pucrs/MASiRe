import json
import pathlib


class Checker:
    """Class that handles all the verifications on the configuration file.

    Note that no function raises any kind of Error, the treatment of any possible error is responsible by the caller."""

    def __init__(self, config_file):
        self.config = pathlib.Path(__file__).parents[2] / config_file

    def run_all_tests(self):
        """Run all the tests on the configuration file and returns the error ir any.

        :return tuple: The code on the first position (1|0) and the error message if the code is 0 else just 'Ok.'"""

        test = self.test_json_load()
        if not test[0]:
            return test

        test = self.test_main_keys()
        if not test[0]:
            return test

        test = self.test_map_key()
        if not test[0]:
            return test

        test = self.test_social_assets_key()
        if not test[0]:
            return test

        test = self.test_agents_key()
        if not test[0]:
            return test

        test = self.test_actions_key()
        if not test[0]:
            return test

        test = self.test_generate_key()
        if not test[0]:
            return test

        return 1, 'Ok.'

    def test_json_load(self):
        """Test if the file can be loaded.

        :returns int: Status where 1 is Ok and 0 is Not ok.
        :returns str: Appropriate message for the user understand his error."""

        try:
            with open(self.config, 'r') as config:
                json.load(config)
            return 1, 'Load: Ok.'
        except json.JSONDecodeError:
            return 0, 'Error loading the file.'

    def test_main_keys(self):
        """Test if the main keys of the configuration file are present.

        :returns int: Status where 1 is Ok and 0 is Not ok.
        :returns str: Appropriate message for the user understand his error."""

        keys = ['map', 'agents', 'socialAssets', 'actions', 'generate']

        config = json.load(open(self.config, 'r'))
        for key in keys:
            if key not in config:
                return 0, f'General: {key} is missing.'

        for key in config:
            if key not in keys:
                return 0, f'General: Key {key} not in the allowed list of keys.'

            if not isinstance(config[key], dict):
                return 0, f'General: Key {key} is not a dict.'

        return 1, 'General: Ok.'

    def test_map_key(self):
        """Test the keys and objects inside the map obj.

        :returns int: Status where 1 is Ok and 0 is Not ok.
        :returns str: Appropriate message for the user understand his error."""

        keys = ['id', 'steps', 'maps', 'minLon', 'maxLon', 'minLat', 'maxLat', 'centerLat', 'centerLon', 'proximity',
                'randomSeed']

        map = json.load(open(self.config, 'r'))['map']
        for key in keys:
            if key not in list(map.keys()):
                return 0, f'Map: {key} is missing.'

        for key in map:
            if key not in keys:
                return 0, f'Map: Key {key} is not in the list of allowed keys.'

        if not isinstance(map['id'], str) and not isinstance(map['id'], int):
            return 0, 'Map: ID is not a valid type.'

        if not isinstance(map['steps'], int):
            return 0, 'Map: Steps is not a valid type.'

        if map['steps'] <= 0:
            return 0, 'Map: Steps can not be zero or negative.'

        if not isinstance(map['maps'], list):
            return 0, 'Map: Maps is not a valid type.'

        if not map['maps']:
            return 0, 'Map: Maps is empty.'

        for key in ['minLat', 'minLon', 'maxLat', 'maxLon']:
            if not isinstance(map[key], float) and not isinstance(map[key], int):
                return 0, f'Map: Key {key} is not a valid type.'

        if map['minLon'] > map['maxLon']:
            return 0, f'Map: MinLon can not be bigger than MaxLon.'

        if map['minLat'] > map['maxLat']:
            return 0, f'Map: MinLat can not be bigger than MaxLat.'

        if not isinstance(map['centerLat'], float) and not isinstance(map['centerLat'], int):
            return 0, 'Map: CenterLat is not a valid type.'

        if map['minLat'] > map['centerLat'] or map['centerLat'] > map['maxLat']:
            return 0, 'Map: CenterLat can not be over the limits of minLat or maxLat.'

        if not isinstance(map['centerLon'], float) and not isinstance(map['centerLon'], int):
            return 0, 'Map: CenterLon is not a valid type.'

        if map['minLon'] > map['centerLon'] or map['centerLon'] > map['maxLon']:
            return 0, 'Map: CenterLon can not be over the limits of minLat or maxLat.'

        if not isinstance(map['proximity'], int):
            return 0, 'Map: Proximity is not a valid type.'

        if not isinstance(map['randomSeed'], str) and not isinstance(map['randomSeed'], int):
            return 0, 'Map: RandomSeed is not a valid type.'

        if map['proximity'] <= 0:
            return 0, 'Map: Proximity can not be zero or negative.'

        return 1, 'Map: Ok.'

    def test_social_assets_key(self):
        """Test the keys and sub keys inside the socialAssets obj.

        :returns int: Status where 1 is Ok and 0 is Not ok.
        :returns str: Appropriate message for the user understand his error."""

        sub_keys = ['abilities', 'resources', 'minSize', 'maxSize', 'amount', 'speed', 'physicalCapacity', 'virtualCapacity']

        social_assets = json.load(open(self.config, 'r'))['socialAssets']

        for key in social_assets:
            if not isinstance(social_assets[key], dict):
                return 0, f'SocialAssets: {str(key).title()} is not a valid type.'

            for sub_key in sub_keys:
                if sub_key not in social_assets[key]:
                    return 0, f'SocialAssets: Sub key {sub_key} from {str(key).title()} is missing.'

            for sub_key in social_assets[key]:
                if sub_key not in sub_keys:
                    return 0, f'SocialAssets: Sub key {sub_key} ' \
                        f'from {str(key).title()} is not int the list of allowed sub keys.'

            if not isinstance(social_assets[key]['abilities'], list):
                return 0, f'SocialAssets: Sub key Abilities from {str(key).title()} is not a valid type.'

            if not isinstance(social_assets[key]['resources'], list):
                return 0, f'SocialAssets: Sub key Resources from {str(key).title()} is not a valid type.'

            if not isinstance(social_assets[key]['minSize'], int):
                return 0, f'SocialAssets: Sub key MinSize from {str(key).title()} is not a valid type.'

            if not isinstance(social_assets[key]['maxSize'], int):
                return 0, f'SocialAssets: Sub key MaxSize from {str(key).title()} is not a valid type.'

            if social_assets[key]['minSize'] > social_assets[key]['maxSize']:
                return 0, f'SocialAssets: Sub key MinSize from {str(key).title()} ' \
                    f'can not be bigger than sub key MaxSize from {str(key).title()}.'

            if social_assets[key]['minSize'] <= 0:
                return 0, f'SocialAssets: Sub key MinSize from {str(key).title()} can not be zero or negative.'

            if not isinstance(social_assets[key]['amount'], int):
                return 0, f'SocialAssets: Sub key Amount from {str(key).title()} is not a valid type.'

            if not isinstance(social_assets[key]['speed'], int):
                return 0, f'SocialAssets: Sub key Speed from {str(key).title()} is not a valid type.'

            if not isinstance(social_assets[key]['physicalCapacity'], int):
                return 0, f'SocialAssets: Sub key PhysicalCapacity from {str(key).title()} is not a valid type.'

            if not isinstance(social_assets[key]['virtualCapacity'], int):
                return 0, f'SocialAssets: Sub key VirtualCapacity from {str(key).title()} is not a valid type.'

        return 1, 'SocialAssets: Ok.'

    def test_agents_key(self):
        """Test the keys and sub keys inside the agents obj.

        :returns int: Status where 1 is Ok and 0 is Not ok.
        :returns str: Appropriate message for the user understand his error."""

        keys = ['drone', 'car', 'boat']
        sub_keys = ['abilities', 'resources', 'size', 'amount', 'speed', 'physicalCapacity', 'virtualCapacity', 'battery']

        agents = json.load(open(self.config, 'r'))['agents']

        for key in keys:
            if key not in agents:
                return 0, f'Agents: {key} is missing.'

        for key in agents:
            if key not in keys:
                return 0, f'Agents: Key {key} not in the list of allowed keys.'

            if not isinstance(agents[key], dict):
                return 0, f'Agents: {str(key).title()} is not a valid type.'

            for sub_key in sub_keys:
                if sub_key not in agents[key]:
                    return 0, f'Agents: Sub key {sub_key} from {str(key).title()} is missing.'

            for sub_key in agents[key]:
                if sub_key not in sub_keys:
                    return 0, f'Agents: Sub key {sub_key} from {str(key).title()} is not int the list of allowed sub keys.'

            if not isinstance(agents[key]['abilities'], list):
                return 0, f'Agents: Sub key Abilities from {str(key).title()} is not a valid type.'

            if not isinstance(agents[key]['resources'], list):
                return 0, f'Agents: Sub key Resources from {str(key).title()} is not a valid type.'

            if not isinstance(agents[key]['size'], int):
                return 0, f'Agents: Sub key Size from {str(key).title()} is not a valid type.'

            if not isinstance(agents[key]['amount'], int):
                return 0, f'Agents: Sub key Amount from {str(key).title()} is not a valid type.'

            if not isinstance(agents[key]['speed'], int):
                return 0, f'Agents: Sub key Speed from {str(key).title()} is not a valid type.'

            if not isinstance(agents[key]['physicalCapacity'], int):
                return 0, f'Agents: Sub key PhysicalCapacity from {str(key).title()} is not a valid type.'

            if not isinstance(agents[key]['virtualCapacity'], int):
                return 0, f'Agents: Sub key VirtualCapacity from {str(key).title()} is not a valid type.'

            if not isinstance(agents[key]['battery'], int):
                return 0, f'Agents: Sub key Battery from {str(key).title()} is not a valid type.'

        return 1, 'Agents: Ok.'

    def test_actions_key(self):
        keys = ['pass', 'move', 'charge', 'rescueVictim', 'collectWater', 'takePhoto', 'analyzePhoto', 'searchSocialAsset',
                'deliverPhysical', 'deliverVirtual', 'carry', 'getCarried', 'receivePhysical', 'receiveVirtual']

        sub_keys = ['abilities', 'resources']

        actions = json.load(open(self.config, 'r'))['actions']
        for key in keys:
            if key not in actions:
                return 0, f'Actions: {key} is missing.'

        for key in actions:
            if key not in keys:
                return 0, f'Actions: Key {key} is not in the list of allowed keys.'

            if not isinstance(actions[key], dict):
                return 0, f'Actions: Key {key} is not a valid type.'

            for sub_key in sub_keys:
                if sub_key not in actions[key]:
                    return 0, f'Actions: Sub key {sub_key} from {str(key).title()} is missing.'

                if not isinstance(actions[key][sub_key], list):
                    return 0, f'Actions: Sub key {sub_key} from {str(key).title()} is not a valid type.'

        return 1, 'Actions: Ok.'

    def test_generate_key(self):
        """Test the keys and objects inside the generate obj.

        :returns int: Status where 1 is Ok and 0 is Not ok.
        :returns str: Appropriate message for the user understand his error."""

        keys = ['flood', 'photo', 'victim', 'waterSample']

        generate = json.load(open(self.config, 'r'))['generate']

        for key in keys:
            if key not in generate:
                return 0, f'Generate: {key} is missing.'

        for key in generate:
            if key not in keys:
                return 0, f'Generate: Key {key} is not in the list of allowed keys.'

        if not isinstance(generate['flood'], dict):
            return 0, 'Generate: Flood is not a valid type.'

        test = self._test_flood_keys(generate['flood'])
        if not test[0]:
            return test

        if not isinstance(generate['photo'], dict):
            return 0, 'Generate: Photo is not a valid type.'

        test = self._test_photo_keys(generate['photo'])
        if not test[0]:
            return test

        if not isinstance(generate['victim'], dict):
            return 0, 'Generate: Victim is not a valid type.'

        test = self._test_victim_keys(generate['victim'])
        if not test[0]:
            return test

        if not isinstance(generate['waterSample'], dict):
            return 0, 'Generate: WaterSample is not a valid type.'

        test = self._test_water_sample_keys(generate['waterSample'])
        if not test[0]:
            return test

        return 1, 'Generate: Ok.'

    @staticmethod
    def _test_flood_keys(flood):
        """Test the keys and objects inside the flood obj that is inside the generate obj.

        :returns int: Status where 1 is Ok and 0 is Not ok.
        :returns str: Appropriate message for the user understand his error."""

        keys = ['probability', 'minPeriod', 'maxPeriod', 'circle']
        sub_keys = ['minRadius', 'maxRadius']

        for key in keys:
            if key not in flood:
                return 0, f'Generate: Key {key} from Flood is missing.'

        for key in flood:
            if key not in keys:
                return 0, f'Generate: Key {key} from Flood is not in the list of allowed keys.'

        if not isinstance(flood['probability'], int) and not isinstance(flood['probability'], float):
            return 0, 'Generate: Probability from Flood is not a valid type.'

        if not isinstance(flood['minPeriod'], int):
            return 0, 'Generate: MinPeriod from Flood is not a valid type.'

        if not isinstance(flood['maxPeriod'], int):
            return 0, 'Generate: MaxPeriod from Flood is not a valid type.'

        if flood['minPeriod'] > flood['maxPeriod']:
            return 0, 'Generate: MinPeriod from Flood can not be bigger than MaxPeriod from Flood.'

        if flood['minPeriod'] <= 0:
            return 0, 'Generate: MinPeriod from Flood can not be zero or negative.'

        if not isinstance(flood['circle'], dict):
            return 0, 'Generate: Circle from Flood is not a valid type.'

        for sub_key in sub_keys:
            if sub_key not in flood['circle']:
                return 0, f'Generate: Key {sub_key} from Flood is missing.'

        for sub_key in flood['circle']:
            if sub_key not in sub_keys:
                return 0, f'Generate: Key {sub_key} from Flood is not in the list of allowed subKeys.'

        if not isinstance(flood['circle']['minRadius'], float):
            return 0, 'Generate: MinRadius from Flood is not a valid type.'

        if not isinstance(flood['circle']['maxRadius'], float):
            return 0, 'Generate: MaxRadius from Flood is not a valid type.'

        if flood['circle']['minRadius'] > flood['circle']['maxRadius']:
            return 0, 'Generate: MinRadius from Flood can not be bigger than MaxRadius from Flood.'

        if flood['circle']['minRadius'] <= 0:
            return 0, 'Generate: MinRadius from Flood can not be zero or negative.'

        return 1, 'Generate: Ok from Flood.'

    @staticmethod
    def _test_photo_keys(photo):
        """Test the keys and objects inside the photo obj that is inside the generate obj.

        :returns int: Status where 1 is Ok and 0 is Not ok.
        :returns str: Appropriate message for the user understand his error."""

        keys = ['minSize', 'maxSize', 'minAmount', 'maxAmount', 'victimProbability']

        for key in keys:
            if key not in photo:
                return 0, f'Generate: Key {key} from Photo is missing.'

        for key in photo:
            if not isinstance(photo[key], int):
                return 0, f'Generate: Key {key} from Photo is not a valid type.'

            if key not in keys:
                return 0, f'Generate: Key {key} from Photo is not in the list of allowed keys.'

        if photo['minAmount'] > photo['maxAmount']:
            return 0, f'Generate: MinAmount from Photo can not be bigger than MaxAmount from Photo.'

        if photo['minAmount'] < 0:
            return 0, 'Generate: MinAmount can not be negative.'

        if photo['minSize'] > photo['maxSize']:
            return 0, f'Generate: MinSize from Photo can not be bigger than MaxSize from Photo.'

        if photo['minSize'] <= 0:
            return 0, 'Generate: MinSize can not be zero or negative.'

        return 1, 'Generate: Ok from Photo.'

    @staticmethod
    def _test_victim_keys(victim):
        """Test the keys and objects inside the victim obj that is inside the generate obj.

        :returns int: Status where 1 is Ok and 0 is Not ok.
        :returns str: Appropriate message for the user understand his error."""

        keys = ['minSize', 'maxSize', 'minAmount', 'maxAmount', 'minLifetime', 'maxLifetime']

        for key in keys:
            if key not in victim:
                return 0, f'Generate: Key {key} from Victim is missing.'

        for key in victim:
            if not isinstance(victim[key], int):
                return 0, f'Generate: Key {key} from Victim is not a valid type.'

            if key not in keys:
                return 0, f'Generate: Key {key} from Victim is not in the list of allowed keys.'

        if victim['minAmount'] > victim['maxAmount']:
            return 0, 'Generate: MinAmount from Victim can not be bigger than MaxAmount from Victim.'

        if victim['minAmount'] < 0:
            return 0, 'Generate: MinAmount from Victim can not be negative.'

        if victim['minSize'] > victim['maxSize']:
            return 0, 'Generate: MinSize from Victim can not be bigger than MaxSize from Victim.'

        if victim['minSize'] <= 0:
            return 0, 'Generate: MinSize from Victim can not be zero or negative.'

        if victim['minLifetime'] > victim['maxLifetime']:
            return 0, 'Generate: MinLifetime from Victim can not be bigger than MaxLifetime from Victim.'

        if victim['minLifetime'] <= 0:
            return 0, 'Generate: MinLifetime from Victim can not be zero or negative.'

        return 1, 'Generate: Ok from Victim.'

    @staticmethod
    def _test_water_sample_keys(water_sample):
        """Test the keys and objects inside the water sample obj that is inside the generate obj.

        :returns int: Status where 1 is Ok and 0 is Not ok.
        :returns str: Appropriate message for the user understand his error."""

        keys = ['minSize', 'maxSize', 'minAmount', 'maxAmount']

        for key in keys:
            if key not in water_sample:
                return 0, f'Generate: Key {key} from WaterSample is missing.'

        for key in water_sample:
            if not isinstance(water_sample[key], int):
                return 0, f'Generate: Key {key} from WaterSample is not a valid type.'

            if key not in keys:
                return 0, f'Generate: Key {key} from WaterSample not in the list of allowed keys.'

        if water_sample['minAmount'] > water_sample['maxAmount']:
            return 0, 'Generate: MinAmount from WaterSample can not be bigger than MaxAmount from WaterSample.'

        if water_sample['minAmount'] < 0:
            return 0, 'Generate: MinAmount from WaterSample can not be negative.'

        if water_sample['minSize'] > water_sample['maxSize']:
            return 0, 'Generate: MinSize from WaterSample can not be bigger than MaxSize from WaterSample.'

        if water_sample['minSize'] <= 0:
            return 0, 'Generate: MinSize from WaterSample can not be zero or negative.'

        return 1, 'Generate: Ok from WaterSample.'
