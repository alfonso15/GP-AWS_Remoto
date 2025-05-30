from djchoices import DjangoChoices, ChoiceItem


class ModelChoices(DjangoChoices):

    @classmethod
    def options(cls):
        return cls._fields.values()
