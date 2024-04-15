import copy
import torch
from torch import nn
import torch.nn.functional as F


class CNNMnist(nn.Module):

    def __init__(self):
        super(CNNMnist, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(320, 50)
        self.fc2 = nn.Linear(50, 10)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.conv2(x)), 2))
        x = x.view(-1, x.shape[1]*x.shape[2]*x.shape[3])
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)


def average_weights(models):
    ''' Averages the weights

    Args:
        models (list): a list of state_dict

    Returns:
        state_dict: the average state_dict
    ''' 
    w_avg = copy.deepcopy(models[0])
    for key in w_avg.keys():
        for i in range(1, len(models)):
            w_avg[key] += models[i][key]
        w_avg[key] = torch.div(w_avg[key], len(models))
    return w_avg


def discrepancy(weightsA, weightsB):
    ''' Computes the discrepancy between two models

    Args:
        weightsA (state_dict): the dict containing the weights of the first model
        weightsB (state_dict): the dict containing the weights of the second model

    Returns:
        double: the discrepancy between the two models
    '''
    keys = weightsA.keys()
    S_t = len(keys)
    d = 0
    for key in keys:
        w_a = weightsA[key]
        w_b = weightsB[key]
        norm = torch.norm(torch.sub(w_a, w_b))
        d += norm
    return d / S_t