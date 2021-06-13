class Serie:

    def __init__(self, serie_id, titles, descriptions, generes, modify_date, seasons):
        self.serie_id = serie_id
        self.titles = titles
        self.descriptions = descriptions
        self.generes = generes
        self.modify_date = modify_date
        self.seasons = seasons

    def setSeasons(self, seasons):
        self.seasons = seasons

class Season:

    def __init__(self, season_number ,descriptions, episodes):
        self.season_number = season_number
        self.descriptions = descriptions
        self.episodes = episodes

class Episode:

    def __init__(self, titles, descriptions, originally_aired, duration):
        self.titles = titles
        self.descriptions = descriptions
        self.originally_aired = originally_aired
        self.duration = duration