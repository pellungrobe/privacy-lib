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
    trajectories = []
    with open(filename) as f:
        for line in f:
            trajectories.append(__read_trajectory_datetime(line))
    return trajectories


def read_trajectory_dataset_date_and_time(filename):
    trajectories = []
    with open(filename) as f:
        for line in f:
            trajectories.append(__read_trajectory_date_and_time(line))
    return trajectories


def write_trajectory_dataset(trajectories, filename):
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
    frequency_vectors = []
    with open(filename) as f:
        for line in f:
            frequency_vectors.append(__read_frequency_vector(line))
    return frequency_vectors


def read_frequency_vector_dataset_csv(filename):
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
    return FrequencyVector


def write_frequency_vector_dataset(frequency_vectors, filename):
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
    return FrequencyVector


def read_probability_vector_dataset(filename):
    probability_vectors = []
    with open(filename) as f:
        for line in f:
            probability_vectors.append(__read_probability_vector(line))
    return probability_vectors


def write_probability_vector_dataset(probability_vectors, filename):
    with open(filename, "w+") as f:
        for fv in probability_vectors:
            f.write(str(fv))

