class Item:
    def __init__(self, id: int, name: str, url: str, set_id: int):
        self.id = id
        self.name = name
        self.url = url
        self.set_id = set_id

    def __eq__(self, other):
        return isinstance(other, Item) and self.id == other.id and self.name == other.name and self.url == other.url and self.set_id == other.set_id

    def __hash__(self):
        return hash((self.id, self.name, self.url, self.set_id))