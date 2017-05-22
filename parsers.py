from data_structures import *

def __read_trajectory_datetime(line):
    itemlist = line.split(",")
    trj = Trajectory(itemlist[0])
    for i in range(1, len(itemlist), 3):
        trj.add_visit(float(itemlist[i]), float(itemlist[i + 1]), int(itemlist[i + 2]))
    return trj


def __read_trajectory_date_and_time(line):
    itemlist = line.split(",")
    trj = Trajectory(itemlist[0])
    for i in range(1, len(itemlist), 4):
        trj.add_visit(float(itemlist[i]), float(itemlist[i + 1]), int(itemlist[i + 2] + itemlist[i + 3]))
    return trj


def __find_record_by_id(records, id_value):
    matching_rec = None
    for record in records:
        if record.id == id_value:
            matching_rec = record
            break
    return matching_rec


def read_trajectory_dataset_csv(filename):
    """
    Reads a Trajectory dataset from a .csv file. The requested format for each row is:
    
    userid,latitude,longitude,timestamp
    
    Each row is thus composed of: the identifier of the individual, latitude of the location, longitude of the location,
    timestamp of the visit.
    
    The trajectory of an individual is thus divided across multiple rows.
    
    Parameters
    ----------
    filename: str
        The name of the file from which to read the trajectories.
    
    Returns
    -------
    trafectories: Trajectory[]
        A list of trajectories read from the file.
    """
    trajectories = []
    with open(filename) as f:
        for line in f:
            itemlist = line.split(",")
            individual_id = int(itemlist[0])
            tr = __find_record_by_id(trajectories, individual_id)
            if tr is None:
                tr = Trajectory(individual_id)
                trajectories.append(tr)
            tr.add_visit(float(itemlist[1]), float(itemlist[2]), int(itemlist[3]))
    return trajectories


def read_trajectory_dataset_datetime(filename):
    """
    Reads a Trajectory dataset from a textfile. The requested format for each row is:

    userid,latitude 1,longitude 1,timestamp 1, ... , latitude n,longitude n,timestamp n
    
    Each row thus decribes the complete trajectory of an individual. Timestamps are single numbers.

    Parameters
    ----------
    filename: str
        The name of the file from which to read the trajectories.
        
    Returns
    -------
    trafectories: Trajectory[]
        A list of trajectories read from the file.
    """
    trajectories = []
    with open(filename) as f:
        for line in f:
            trajectories.append(__read_trajectory_datetime(line))
    return trajectories


def read_trajectory_dataset_date_and_time(filename):
    """
    Reads a Trajectory dataset from a textfile. The requested format for each row is:

    userid,latitude 1,longitude 1,date 1,time 1, ... , latitude n,longitude n,date n,time n

    Each row thus decribes the complete trajectory of an individual. Timestamps are divided in two numbers, one representing
    the date and the other representing the time of the day.

    Parameters
    ----------
    filename: str
        The name of the file from which to read the trajectories.
    
    Returns
    -------
    trafectories: Trajectory[]
        A list of trajectories read from the file.
    """
    trajectories = []
    with open(filename) as f:
        for line in f:
            trajectories.append(__read_trajectory_date_and_time(line))
    return trajectories


def write_trajectory_dataset(trajectories, filename):
    """
    Writes a Trajectory dataset to a textfile. The format for each row is:

    userid,latitude 1,longitude 1,timestamp 1, ... , latitude n,longitude n,timestamp n

    Each row thus decribes the complete trajectory of an individual. Timestamps are single numbers.

    Parameters
    ----------
    filename: str
        The name of the file to which to write the dataset.
    trafectories: Trajectory[]
        A list of trajectories to write.
    """
    with open(filename, "w+") as f:
        for tr in trajectories:
            f.write(str(tr))


def __read_frequency_vector(line):
    itemlist = line.split(",")
    fv = FrequencyVector(itemlist[0])
    for i in range(1, len(itemlist), 3):
        fv.add_visit(float(itemlist[i]), float(itemlist[i + 1]), int(itemlist[i + 2]))
    return fv


def read_frequency_vector_dataset(filename):
    """
    Reads a Frequency Vector dataset from a text file. The requested format for each row is:

    userid,latitude 1,longitude 1,frequency 1, ... ,latitude n,longitude n,frequency n

    Each row is thus represents the complete frequency vector of an individual

    Parameters
    ----------
    filename: str
        The name of the file from which to read the frequency vectors.

    Returns
    -------
    frequency_vectors: FrequencyVector[]
        A list of frequency vectors read from the file.
    """
    frequency_vectors = []
    with open(filename) as f:
        for line in f:
            frequency_vectors.append(__read_frequency_vector(line))
    return frequency_vectors


def read_frequency_vector_dataset_csv(filename):
    """
    Reads a Frequency Vector dataset from a .csv file. The requested format for each row is:

    userid,latitude,longitude,frequency

    Each row is thus composed of: the identifier of the individual, latitude of the location, longitude of the location,
    frequency of the visits to the location.

    The frequency vector of an individual is thus divided across multiple rows.

    Parameters
    ----------
    filename: str
        The name of the file from which to read the frequency vectors.

    Returns
    -------
    frequency_vectors: FrequencyVector[]
        A list of frequency vectors read from the file.
    """
    frequency_vectors = []
    with open(filename) as f:
        for line in f:
            itemlist = line.split(",")
            individual_id = int(itemlist[0])
            fv = __find_record_by_id(frequency_vectors, individual_id)
            if fv is None:
                vf = FrequencyVector(individual_id)
                frequency_vectors.append(fv)
            fv.add_visit(float(itemlist[1]), float(itemlist[2]), int(itemlist[3]))
    return frequency_vectors


def write_frequency_vector_dataset(frequency_vectors, filename):
    """
    Writes a Frequency Vector Dataset to a textfile. The format for each row is:

    userid,latitude 1,longitude 1,frequency 1, ... , latitude n,longitude n,frequency n

    Each row thus decribes the complete vector of an individual.
    
    Parameters
    ----------
    filename: str
        The name of the file to which to write the dataset.
    frequency_vectors: FrequencyVector[]
        A list of frequency vectors to write.
    """
    with open(filename, "w+") as f:
        for fv in frequency_vectors:
            f.write(str(fv))


def __read_probability_vector(line):
    itemlist = line.split(",")
    pv = ProbabilityVector(itemlist[0])
    for i in range(1, len(itemlist), 3):
        pv.add_visit(float(itemlist[i]), float(itemlist[i + 1]), float(itemlist[i + 2]))
    return pv


def read_probability_vector_dataset_csv(filename):
    """
    Reads a Probability Vector dataset from a .csv file. The requested format for each row is:

    userid,latitude,longitude,probability

    Each row is thus composed of: the identifier of the individual, latitude of the location, longitude of the location,
    probability of the visit to the location.

    The probability vector of an individual is thus divided across multiple rows.

    Parameters
    ----------
    filename: str
        The name of the file from which to read the probability vectors.

    Returns
    -------
    probability_vectors: ProbabilityVector[]
        A list of probability vectors read from the file.
    """
    probability_vectors = []
    with open(filename) as f:
        for line in f:
            itemlist = line.split(",")
            individual_id = int(itemlist[0])
            pv = __find_record_by_id(probability_vectors, individual_id)
            if pv is None:
                vf = FrequencyVector(individual_id)
                probability_vectors.append(pv)
            pv.add_visit(float(itemlist[1]), float(itemlist[2]), float(itemlist[3]))
    return probability_vectors


def read_probability_vector_dataset(filename):
    """
    Reads a Probability Vector dataset from a text file. The requested format for each row is:

    userid,latitude 1,longitude 1,probability 1, ... ,latitude n,longitude n,probability n

    Each row is thus represents the complete probability vector of an individual

    Parameters
    ----------
    filename: str
        The name of the file from which to read the probability vectors.

    Returns
    -------
    probability_vectors: ProbabilityVector[]
        A list of probability vectors read from the file.
    """
    probability_vectors = []
    with open(filename) as f:
        for line in f:
            probability_vectors.append(__read_probability_vector(line))
    return probability_vectors


def write_probability_vector_dataset(probability_vectors, filename):
    """
    Writes a Probability Vector Dataset to a textfile. The format for each row is:

    userid,latitude 1,longitude 1,probability 1, ... , latitude n,longitude n,probability n

    Each row thus decribes the complete vector of an individual.

    Parameters
    ----------
    filename: str
        The name of the file to which to write the dataset.
    probability_vectors: ProbabilityVector[]
        A list of probability vectors to write.
    """
    with open(filename, "w+") as f:
        for fv in probability_vectors:
            f.write(str(fv))
