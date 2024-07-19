# Case_Skins.py

class Skin:
    """
    A class to represent an individual skin.

    Attributes:
    name (str): The name of the skin.
    weapon (str): The weapon associated with the skin.
    prices (list): A list of prices for the skin at different qualities.
    rarity (str): The rarity of the skin.
    """
    def __init__(self):
        self.name = ""
        self.weapon = ""
        self.prices = []
        self.rarity = ""


class Case:
    """
    A class to represent a case containing skins.

    Attributes:
    name (str): The name of the case.
    link (str): The link to data about the skins in the case.
    Skins (list): A list of Skin objects contained in the case.
    byRarity (list): A list of lists, each containing Skin objects of a specific rarity.
    """
    def __init__(self):
        self.name = ""
        self.link = ""
        self.Skins = []
        self.byRarity = []
