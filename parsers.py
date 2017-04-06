from data_structures import *

def parse_trajectory_datetime(line):
    itemlist = line.split(",")
    trj = Trajectory(itemlist[0])
    for i in range(1,len(itemlist),3):
        trj.add_visit(float(itemlist[i]), float(itemlist[i+1]), int(itemlist[i+2]))
    return trj

def parse_trajectory_date_and_time(line):
    itemlist = line.split(",")
    trj = Trajectory(itemlist[0])
    for i in range(1,len(itemlist),4):
        trj.add_visit(float(itemlist[i]), float(itemlist[i+1]), int(itemlist[i+2] + itemlist[i+3]))
    return trj

def parse_trajectory_dataset_datetime(filename):
    trajectories = []
    with open(filename) as f:
        for line in f:
            trajectories.append(parse_trajectory_datetime(line))
    return trajectories

def parse_trajectory_dataset_date_and_time(filename):
    trajectories = []
    with open(filename) as f:
        for line in f:
            trajectories.append(parse_trajectory_date_and_time(line))
    return trajectories
