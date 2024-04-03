class MlEngTest:
    def __init__(self, image):
        self.image = self.load_image(image=image)

    @staticmethod
    def load_image(image):
        return 0

    def execute_task(self):
        pass


class PageInfo(MlEngTest):
    pass


class Rooms(MlEngTest):
    pass


class Walls(MlEngTest):
    pass


class Tables(MlEngTest):
    pass


tasks_types = {"walls": Walls,
               "rooms": Rooms,
               "tables": Tables,
               "page_info": PageInfo}
