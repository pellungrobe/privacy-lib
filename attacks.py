from itertools import combinations
from numpy import array, ones
from abc import ABCMeta, abstractmethod
from data_structures import *


class Attack:
    """
    Abstract class for a generic attack. Defines a series of functions common to all attacks.
    """
    __metaclass__ = ABCMeta

    def __init__(self, k):
        """
        Generic initializer for an attack.

        Parameters
        ----------
        k: int
            parameter that defines the background knowledge configuration. It represents the quantity of information
            that the adversary has. So, for example, if k = 2, the adversary will, ipothetically, know any combination
            of the visits of a users of length 2.
        """
        self.k = k

    def all_risks(self, dataset):
        """
        Computes privacy risk for all individuals in the dataset. Calls the risk function on all individuals.

        Parameters
        ----------
        dataset: numpy.array[IndividualRecord]
            the dataset on which to calculate the risk.

        Returns
        -------
        risk: dict{int : float}
            a dictionary with the identifier of each individual paired with her risk.
        """
        risks = {}
        for individual_record in dataset:
            risks[individual_record.id] = self.risk(dataset, individual_record)
        return risks

    def __reidentification_prob( self, dataset, instance, individual_id):
        """
        Computes the probability of reidentification of a background knowledge instance. The probability of
        reidentification is defined as the ratio between the number of records belonging to the user, and the number of
        records matching the background knowledge instance. The matching is determined calling the matching function.

        Parameters
        ----------
        dataset: numpy.array[IndividualRecord]
            the dataset against which to make the matching operations.
        instance: numpy.array[(x,y,i)]
            the background knowledge instance on which to execute the computation.
        individual_id: int
            the identifier of the individual owning te instance.
        Returns
        -------
        reid_prob: float
            the probability of reidentification of the background knowledge instance
        """
        support = 0.0
        num_records = 0.0
        for individual_record in dataset:
            if self.has_matching(individual_record, instance):
                support += 1
            if individual_record.id == individual_id:
                num_records += 1
        reid_prob = num_records / support
        return reid_prob

    def risk(self, dataset, individual_record):
        """
        Computes the risk of reidentification of an individual with respect to a dataset.

        Parameters
        ----------
        dataset: numpy.array[IndividualRecord]
            the dataset against which to compute the privacy risk.
        individual_record: IndividualRecord
            the individual record of the individual of which to compute the privacy risk.

        Returns
        -------
        risk: float
            the privacy risk of the individual owner of the individual_record.
        """
        number_of_visits = len(individual_record.visits)
        if self.k > number_of_visits:
            instances = combinations(individual_record.visits, len(individual_record.visits))
        else:
            instances = combinations(individual_record.visits, self.k)
        risk = 0
        for instance in instances:
            arr = array(list(instance), dtype=Trajectory.data_type)
            prob = self.__reidentification_prob(dataset, arr, individual_record.id)
            if prob > risk:
                risk = prob
        return risk

    @abstractmethod
    def has_matching(self, individual_record, instance):
        """
        Parameters
        ----------
        individual_record: IndividualRecord
            the record against which to do the matching.
        instance: numpy.array[(x,y,i)]
            the background knowledge instance on which to execute the matching.

        Matches a background knowledge instance and a data structure. Attacks should implement this with the proper
        matching operation unique to each attack.
        """
        pass


class LocationAttack(Attack):
    """
    Location attack on trajectories or vectors. Each instance is considered as a multiset of pure locations, without any other
    information.
    """

    def has_matching(self, individual_record, instance):
        """
        The matching function for the LocationAttack.

        Parameters
        ----------
        individual_record: IndividualRecord
            the record against which to do the matching.
        instance: numpy.array[(x,y,i)]
            the background knowledge instance on which to execute the matching.

        Returns
        -------
        has_match: bool
            True if the instance matches with the record, False otherwise.
        """
        target = len(instance)
        number_of_visits = len(individual_record.visits)
        control = ones(number_of_visits, dtype=bool)
        count = 0
        has_match = True
        for j in range(0, target):
            instance_elem = instance[j]
            for i in range(0, number_of_visits):
                record_elem = individual_record.visits[i]
                samex = instance_elem["x"] == record_elem["x"]
                samey = instance_elem["y"] == record_elem["y"]
                if samex and samey and control[i]:
                    count += 1
                    control[i] = False
                    break
            if count == target:
                break
            if j >= count:
                has_match = False
                break
        return has_match


class LocationSequenceAttack(Attack):
    """
    Location sequence attack on trajectories or vectors. Each instance is considered as a sequence of pure locations and the order
    in which they appear is also considered.
    """

    def has_matching(self, individual_record, instance):
        """
        The matching function for the LocationSequenceAttack.

        Parameters
        ----------
        individual_record: IndividualRecord
            the record against which to do the matching.
        instance: numpy.array[(x,y,i)]
            the background knowledge instance on which to execute the matching.

        Returns
        -------
        has_match: bool
            True if the instance matches with the record, False otherwise.
        """
        target = len(instance)
        number_of_visits = len(individual_record.visits)
        count = 0
        has_match = True
        for i in range(0, number_of_visits):
            record_elem = individual_record.visits[i]
            instance_elem = instance[count]
            samex = instance_elem["x"] == record_elem["x"]
            samey = instance_elem["y"] == record_elem["y"]
            if samex and samey:
                count += 1
            if count == target:
                break
            if (number_of_visits - i) < (target - count):
                has_match = False
                break
        return has_match


class VisitAttack(Attack):
    """
    Visit attack on trajectories. Each instance is considered as a sequence of locations with timestamps, hence the
    order of the visits is implicitly considered. Also, the precision with which considering the timestamp can also
    be specified.
    """
    precision_levels = ["Year", "Month", "Day", "Hour", "Minute", "Second"]

    def __init__(self, k, precision):
        """
        Initializer for the VisitAttack. Call the generic Attack initializer but adds precision, to allow to specify
        the precision with which to consider the timestamps of the visits during the matching. This essentially
        modulates the power of the attack.

        Parameters
        ----------
        k: int
            parameter that defines the background knowledge configuration. It represents the quantity of information
            that the adversary has. So, for example, if k = 2, the adversary will, ipothetically, know any combination
            of the visits of a users of length 2.
        precision: str
            can be either: "Year", "Month", "Day", "Hour", "Minute" or "Second". The timestamps of the visits will be
            matched depending on the precision specified. So, for instance, if precision is "Day", the timestamps of the
            visits will be matched up to the day, neglecting hour, minute and second.
        """
        super().__init__(k)
        if precision not in VisitAttack.precision_levels:
            raise ValueError
        self.precision = precision

    def __extract_precision(self, i):
        """
        Private function for cutting the time of a visit to the required precision.

        Parameters
        ----------
        i: int
            the time to be cut

        Returns
        -------
        num: int
            the time cut to the required precision.
        """
        num_string = str(i)
        num = i
        if (self.precision == "Year"):
            num = int(num_string[:4])
        elif (self.precision == "Month"):
            num = int(num_string[:6])
        elif (self.precision == "Day"):
            num = int(num_string[:8])
        elif (self.precision == "Hour"):
            num = int(num_string[:10])
        elif (self.precision == "Minute"):
            num = int(num_string[:12])
        elif (self.precision == "Second"):
            num = int(num_string[:14])
        return num

    def has_matching(self, individual_record, instance):
        """
        The matching function for the LocationSequenceAttack.

        Parameters
        ----------
        individual_record: IndividualRecord
            the record against which to do the matching. It is considered a Trajectory.
        instance: numpy.array[(x,y,i)]
            the background knowledge instance on which to execute the matching.

        Returns
        -------
        has_match: bool
            True if the instance matches with the record, False otherwise.
        """
        target = len(instance)
        number_of_visits = len(individual_record.visits)
        count = 0
        has_match = True
        for i in range(0, number_of_visits):
            record_elem = individual_record.visits[i]
            instance_elem = instance[count]
            samex = instance_elem["x"] == record_elem["x"]
            samey = instance_elem["y"] == record_elem["y"]
            t_diff = self.__extract_precision(instance_elem["time"]) - self.__extract_precision(record_elem["time"])
            samet = t_diff == 0
            if samex and samey and samet:
                count += 1
            else:
                too_early = t_diff < 0
                if too_early:
                    has_match = False
                    break
            if count == target:
                break
            if (number_of_visits - i) < (target - count):
                has_match = False
                break
        return has_match


class FrequencyAttack(Attack):
    """
    Frequency attack on frequency vectors. Each instance is considered as a sequence of locations and their frequency of
    visit is also considered. It is also possible to specify a tolerance level.
    """

    def __init__(self, k, tolerance):
        """
        Initializer for the FrequencyAttack. Call the generic Attack initializer but adds tolerance, to allow to specify
        the precision with which to consider the frequency of the visits during the matching. This essentially
        modulates the power of the attack.

        Parameters
        ----------
        k: int
            parameter that defines the background knowledge configuration. It represents the quantity of information
            that the adversary has. So, for example, if k = 2, the adversary will, ipothetically, know any combination
            of the visits of a users of length 2.
        tolerance: float
            can be any number between 0 and 1. The tolerance is used as a percentage: each visit in the instance
            will match if there is a visit in the individual record with the same location and that has a frequency
            of at least the frequency of the visit in the instance times the tolerance. For instance, if the tolerance
            is 0.9, and the frequency of the visit in the instance is 10, it will match a visit in the individual record
            if it has the same location and at least frequency of 9.
        """
        super().__init__(k)
        if tolerance < 0 or tolerance > 1:
            raise ValueError
        self.tolerance = tolerance

    def has_matching(self, individual_record, instance):
        """
        The matching function for the LocationSequenceAttack.

        Parameters
        ----------
        individual_record: IndividualRecord
            the record against which to do the matching. It is considered a FrequencyVector.
        instance: numpy.array[(x,y,i)]
            the background knowledge instance on which to execute the matching.

        Returns
        -------
        has_match: bool
            True if the instance matches with the record, False otherwise.
        """
        target = len(instance)
        number_of_visits = len(individual_record.visits)
        count = 0
        has_match = True
        for i in range(0, number_of_visits):
            record_elem = individual_record.visits[i]
            instance_elem = instance[count]
            samex = instance_elem["x"] == record_elem["x"]
            samey = instance_elem["y"] == record_elem["y"]
            f_diff = record_elem["freq"] - instance_elem["freq"] * self.tolerance
            samef = f_diff >= 0
            if samex and samey and samef:
                count += 1
            else:
                too_few_f = f_diff < 0
                if too_few_f:
                    has_match = False
                    break
            if count == target:
                break
            if (number_of_visits - i) < (target - count):
                has_match = False
                break
        return has_match

    class ProbabilityAttack(Attack):
        """
        Probability attack on probability vectors. Each instance is considered as a sequence of locations and their
        probability of visit is also considered. It is also possible to specify a tolerance level.
        """

        def __init__(self, k, tolerance):
            """
            Initializer for the ProbabilityAttack. Call the generic Attack initializer but adds tolerance, to allow to specify
            the precision with which to consider the probability of the visits during the matching. This essentially
            modulates the power of the attack.

            Parameters
            ----------
            k: int
                parameter that defines the background knowledge configuration. It represents the quantity of information
                that the adversary has. So, for example, if k = 2, the adversary will, ipothetically, know any combination
                of the visits of a users of length 2.
            tolerance: float
                can be any number between 0 and 1. The tolerance is used in the following way: each visit in the instance
                will match if there is a visit in the individual record with the same location and that has a probability
                that falls in the range of the probability of visit of the instance +/- the tolerance. For instance, if
                the tolerance is 0.1, and the probability of the visit in the instance is 0.85, it will match a visit in
                the individual record if it has the same location and a probability in the range [0.75,0.95]
            """
            super().__init__(k)
            if tolerance < 0 or tolerance > 1:
                raise ValueError
            self.tolerance = tolerance

        def has_matching(self, individual_record, instance):
            """
            The matching function for the LocationSequenceAttack.

            Parameters
            ----------
            individual_record: IndividualRecord
                the record against which to do the matching. It is considered a ProbabilityVector.
            instance: numpy.array[(x,y,i)]
                the background knowledge instance on which to execute the matching.

            Returns
            -------
            has_match: bool
                True if the instance matches with the record, False otherwise.
            """
            target = len(instance)
            number_of_visits = len(individual_record.visits)
            count = 0
            has_match = True
            for i in range(0, number_of_visits):
                record_elem = individual_record.visits[i]
                instance_elem = instance[count]
                samex = instance_elem["x"] == record_elem["x"]
                samey = instance_elem["y"] == record_elem["y"]
                p_diff_min = record_elem["prob"] - instance_elem["prob"] - self.tolerance
                p_diff_max = record_elem["prob"] - instance_elem["prob"] + self.tolerance
                samep = p_diff_min >= 0 and p_diff_max <= 0
                if samex and samey and samep:
                    count += 1
                else:
                    too_few_p = p_diff_min < 0
                    if too_few_p:
                        has_match = False
                        break
                if count == target:
                    break
                if (number_of_visits - i) < (target - count):
                    has_match = False
                    break
            return has_match


class ProportionAttack(Attack):
    """
    Proportion attack on frequency vectors. Each instance is considered as a sequence of locations and the proportion
    between the frequency of visit is also considered. It is also possible to specify a tolerance level.
    """

    def __init__(self, k, tolerance):
        """
        Initializer for the ProportionAttack. Call the generic Attack initializer but adds tolerance, to allow to specify
        the precision with which to consider the proportion of frequency of the visits during the matching.
        This essentially modulates the power of the attack.

        Parameters
        ----------
        k: int
            parameter that defines the background knowledge configuration. It represents the quantity of information
            that the adversary has. So, for example, if k = 2, the adversary will, ipothetically, know any combination
            of the visits of a users of length 2.
        tolerance: float
            can be any number between 0 and 1. The tolerance is used in the following way: a pair of visits in the instance
            will match if there is a pair of visit in the individual record that has the same locations and has the same
            proportions between the frequencies of the visits as in the instance +/- the tolerance. For instance, 
            if the tolerance is 0.2, and the proportion between two visits in the istance is 0.4, it will match
            in the individual record if there are two visits with the same locations that have a proportion between
            their frequencies that lies between 0.2 and 0.6.
        """
        super().__init__(k)
        if tolerance < 0 or tolerance > 1:
            raise ValueError
        self.tolerance = tolerance

    def __match_proportions(self, matched_elements, instance):
        """
        Private function for the matching of frequencies proportions between two collections of elements: 
        FrequencyVector and instance. Should not be used directly.
        
        Parameters
        ----------
        
        matched_elements: FrequencyVector
            contains the elements that matched in terms of locations.
        instance: numpy.array[(x,y,i)]
            the background knowledge instance on which to execute the matching.
        
        Returns
        -------
        has_match: bool
            True if the two collections have the same frequencies proportions, False otherwise.
        """
        has_match = True
        most_frequent_instance = instance[0]
        most_frequent_matched = matched_elements.visits[0]
        number_of_visits = len(matched_elements.visits)
        for i in range(1, number_of_visits):
            prop_matched = matched_elements.visits[i]["freq"] / most_frequent_matched["freq"]
            prop_instance = instance[i]["freq"] / most_frequent_instance["freq"]
            p_diff_min = prop_matched - prop_instance - self.tolerance
            p_diff_max = prop_matched - prop_instance + self.tolerance
            samep = p_diff_min >= 0 and p_diff_max <= 0
            if not samep:
                has_match = False
                break
        return has_match

    def has_matching(self, individual_record, instance):
        """
        The matching function for the LocationSequenceAttack.

        Parameters
        ----------
        individual_record: IndividualRecord
            the record against which to do the matching. It is considered a FrequencyVector.
        instance: numpy.array[(x,y,i)]
            the background knowledge instance on which to execute the matching.

        Returns
        -------
        has_match: bool
            True if the instance matches with the record, False otherwise.
        """
        target = len(instance)
        number_of_visits = len(individual_record.visits)
        count = 0
        has_match = True
        matched_elements = FrequencyVector(individual_record.id)
        for i in range(0, number_of_visits):
            record_elem = individual_record.visits[i]
            instance_elem = instance[count]
            samex = instance_elem["x"] == record_elem["x"]
            samey = instance_elem["y"] == record_elem["y"]
            if samex and samey:
                count += 1
                matched_elements.add_visit(record_elem["x"], record_elem["y"], record_elem["freq"])
            if count == target:
                break
            if (number_of_visits - i) < (target - count):
                has_match = False
                break
        if (has_match):
            has_match = self.__match_proportions(matched_elements, instance)
        return has_match

class HomeWorkAttack(Attack):
    """
    Home and work attack on frequency vectors. Each instance is made of the two most freuent locations and their frequency of
    visit is also considered. It is also possible to specify a tolerance level.
    """

    HomeWorkK = 0

    def __init__(self, tolerance):
        """
        Initializer for the HomeWorkAttack. Call the generic Attack initializer but adds tolerance, to allow to specify
        the precision with which to consider the frequency of the visits during the matching. This essentially
        modulates the power of the attack.

        Parameters
        ----------
        k: int
            parameter that defines the background knowledge configuration. It represents the quantity of information
            that the adversary has. So, for example, if k = 2, the adversary will, ipothetically, know any combination
            of the visits of a users of length 2.
        tolerance: float
            can be any number between 0 and 1. The tolerance is used as a percentage: each visit in the instance
            will match if there is a visit in the individual record with the same location and that has a frequency
            of at least the frequency of the visit in the instance times the tolerance. For instance, if the tolerance
            is 0.9, and the frequency of the visit in the instance is 10, it will match a visit in the individual record
            if it has the same location and at least frequency of 9.
        """
        super().__init__(HomeWorkAttack.HomeWorkK)
        if tolerance < 0 or tolerance > 1:
            raise ValueError
        self.tolerance = tolerance

    def has_matching(self, individual_record, instance):
        """
        The matching function for the LocationSequenceAttack.

        Parameters
        ----------
        individual_record: IndividualRecord
            the record against which to do the matching. It is considered a FrequencyVector.
        instance: numpy.array[(x,y,i)]
            the background knowledge instance on which to execute the matching.

        Returns
        -------
        has_match: bool
            True if the instance matches with the record, False otherwise.
        """
        target = len(instance)
        number_of_visits = len(individual_record.visits)
        count = 0
        has_match = True
        for i in range(0, number_of_visits):
            record_elem = individual_record.visits[i]
            instance_elem = instance[count]
            samex = instance_elem["x"] == record_elem["x"]
            samey = instance_elem["y"] == record_elem["y"]
            f_diff = record_elem["freq"] - instance_elem["freq"] * self.tolerance
            samef = f_diff >= 0
            if samex and samey and samef:
                count += 1
            else:
                too_few_f = f_diff < 0
                if too_few_f:
                    has_match = False
                    break
            if count == target:
                break
            if (number_of_visits - i) < (target - count):
                has_match = False
                break
        return has_match

    def risk(self, dataset, individual_record):
        """
        Computes the risk of reidentification of an individual with respect to a dataset. We have to override the general
        risk calculation procedure because for the Home and Work attack we don't have to compute combinations.

        Parameters
        ----------
        dataset: numpy.array[IndividualRecord]
            the dataset against which to compute the privacy risk.
        individual_record: IndividualRecord
            the individual record of the individual of which to compute the privacy risk.

        Returns
        -------
        risk: float
            the privacy risk of the individual owner of the individual_record.
        """
        number_of_visits = len(individual_record.visits)
        instance = (individual_record.visits[0], individual_record.visits[1])
        risk = 0
        arr = array(list(instance), dtype=Trajectory.data_type)
        prob = self.__reidentification_prob(dataset, arr, individual_record.id)
        if prob > risk:
            risk = prob
        return risk