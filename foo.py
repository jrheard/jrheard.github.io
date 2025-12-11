from uuid import UUID


class SaveMixin:
    def set_save_data(self, data):
        self._data = data

    def save_to_database(self):
        DATABASE.write(self.id, self._data)


class User(SaveMixin):
    id: UUID
