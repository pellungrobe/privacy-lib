from abc import ABCMeta, abstractmethod
from numpy import array, searchsorted, insert


class IndividualRecord:
    """
    Abstract class for a generic mobility individual record

    Attributes
    ----------
    data_type:
        the type of the visits that  will compose a mobility individual record.
        Should be overwritten by implementing classes, if needed.
    """
    __metaclass__ = ABCMeta

    data_type = [("x", float), ("y", float), ("i", float)]

    def __init__(self, individual_id):
        """
        Generic initializer for a record.

        Parameters
        ----------
        individual_id: int
            the identifier of the individual whose this record belongs to.
        """
        self.visits = array([], dtype=self.data_type)
        self.id = individual_id

    @abstractmethod
    def add_visit(self, x, y, i):
        """
        Adding a visit to a record.
        This should be instantiated by classes inheriting Mobility Record.
        """
        pass


class Trajectory(IndividualRecord):
    """
    Class for trajectory records. Each visit of a trajectory is a triple of two geographical coordinatesrepresenting the
    location and a timestamp. The timestamp is managed as an integer, with precision up to the second.

    Attributes
    ----------
    data_type:
        the type of the visits that  will compose a trajectory.
    """

    data_type = [("x", float), ("y", float), ("time", "int")]

    def add_visit(self, x, y, i):
        """
        Adds a visit to the trajectory. The visits are kept in order of timestamp, from least recent to most recent.

        Parameters
        ----------
        x: float
            first geographical coordinate (typically latitude).
        y: float
            second geographical coordinate (typically longitude).
        i: int
            timestamp of the visit, as an integer.

        Returns
        -------
        self: Trajectory
            modified with the added visit
        """
        elem = (x, y, i)
        target = array(elem, dtype=self.data_type)
        index = searchsorted(self.visits["time"], target["time"])
        self.visits = insert(self.visits, index, elem)
        return self

    def __repr__(self):
        repr = str(self.id)
        for v in self.visits:
            repr += "," + str(v["x"]) + "," + str(v["y"]) + "," + str(v["time"])
        return repr


class FrequencyVector(IndividualRecord):
    """
    Class for frequency vector records. Each visit of a frequency vector is a triple of two geographical coordinates
    representing the location and an integer representing how many times the individual visited the location.

    Attributes
    ----------
    data_type:
        the type of the visits that  will compose a trajectory.
    """
    data_type = [("x", float), ("y", float), ("freq", int)]

    def add_visit(self, x, y, i):
        """
        Adds a visit to the FrequencyVector. The visits are kept in order of frequency, from most frequent to
        least frequent.

        Parameters
        ----------
        x: float
            first geographical coordinate (typically latitude).
        y: float
            second geographical coordinate (typically longitude).
        i: int
            frequency of the visit.

        Returns
        -------
        self: FrequencyVector
            modified with the added visit
        """
        elem = (x, y, i)
        target = array(elem, dtype=self.data_type)
        index = self.visits.size - searchsorted(self.visits["freq"][::-1], target["freq"], side="right")
        self.visits = insert(self.visits, index, elem)
        return self

    def __repr__(self):
        repr = str(self.id)
        for v in self.visits:
            repr += "," + str(v["x"]) + "," + str(v["y"]) + "," + str(v["freq"])
        return repr


class ProbabilityVector(IndividualRecord):
    """
    Class for probability vector records. Each visit of a probability vector is a triple of two geographical coordinates
    representing the location and a float representing the probability with which the individual visited the location.

    Attributes
    ----------
    data_type:
        the type of the visits that  will compose a trajectory.
    """
    data_type = [("x", float), ("y", float), ("prob", float)]

    def add_visit(self, x, y, i):
        """
        Adds a visit to the ProbabilityVector. The visits are kept in order of probability, from most frequent to
        least frequent.

        Parameters
        ----------
        x: float
            first geographical coordinate (typically latitude).
        y: float
            second geographical coordinate (typically longitude).
        i: int
            probability of the visit.

        Returns
        -------
        self: ProbabilityVector
            modified with the added visit
        """
        elem = (x, y, i)
        target = array(elem, dtype=self.data_type)
        index = self.visits.size - searchsorted(self.visits["prob"][::-1], target["prob"], side="right")
        self.visits = insert(self.visits, index, elem)

    def __repr__(self):
        repr = str(self.id)
        for v in self.visits:
            repr += "," + str(v["x"]) + "," + str(v["y"]) + "," + str(v["prob"])
        return repr
