
class MedicationActionPotential:
    """
    This class holds the action for a given medication concept (discussed, etc). They are pulled
    from the MedicationActionNames class (essentially string constants)
    """
    name:str
    probability:float

    def __eq__(self, other):
        return (self.name == other.name and self.probability == other.probability)

    def __lt__(self, other):
        return self.probability<other.probability

    def __str__(self):
        probabilityString = "{:.2%}".format(self.probability)
        return str(f'{self.name} {probabilityString}')

    def __init__(self, medName:str, actionProbability:float):
        self.name = medName
        self.probability=actionProbability
