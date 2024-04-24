import copy
import torch
from torch import nn
from torchvision import datasets, transforms
import torch.nn.functional as F
import numpy as np
from torch.utils.data import DataLoader, Dataset, random_split

dataset_download_path = "../../build/dataset"

class CNNMnist(nn.Module):

    def __init__(self):
        super(CNNMnist, self).__init__()
        self.conv1 = nn.Conv2d(1, 5, kernel_size=5)
        self.conv2 = nn.Conv2d(5, 10, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(160, 20)
        self.fc2 = nn.Linear(20, 10)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.conv2(x)), 2))
        x = x.view(-1, x.shape[1] * x.shape[2] * x.shape[3])
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)

class DatasetSplit(Dataset):
    """An abstract Dataset class wrapped around Pytorch Dataset class.
    """

    def __init__(self, dataset, idxs):
        self.dataset = dataset
        self.idxs = [int(i) for i in idxs]

    def __len__(self):
        return len(self.idxs)

    def __getitem__(self, item):
        image, label = self.dataset[self.idxs[item]]
        return torch.tensor(image), torch.tensor(label)

def average_weights(models, weigths):
    """ Averages the weights

    Args:
        models (list): a list of state_dict

    Returns:
        state_dict: the average state_dict
    """
    w_avg = copy.deepcopy(models[0])

    for key in w_avg.keys():
        w_avg[key] = torch.mul(w_avg[key], 0.0)
    sum_weights = sum(weigths)
    for key in w_avg.keys():
        for i in range(0, len(models)):
            w_avg[key] += models[i][key] * weigths[i]
        w_avg[key] = torch.div(w_avg[key], sum_weights)
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
        ## compute euclidean distance between w_a and w_b
        norm = torch.dist(w_a, w_b, p=2)

        #norm = torch.sub(w_a, w_b)
        d += norm
    return d / S_t


def get_dataset(indexes):

    apply_transform = transforms.ToTensor()

    train_dataset = datasets.MNIST(dataset_download_path,
                                   train=True,
                                   download=False,
                                   transform=apply_transform)

    dataset = DatasetSplit(train_dataset, indexes)

    return dataset


def dataset_to_nodes_partitioning(areas: int, random_seed: int, shuffling: bool = False, data_fraction = 1.0):
    np.random.seed(random_seed)  # set seed from Alchemist to make the partitioning deterministic
    apply_transform = transforms.ToTensor()

    train_dataset = datasets.MNIST(dataset_download_path, train=True, download=True, transform=apply_transform)

    # nodes_per_area = int(nodes_count / areas)
    dataset_labels_count = len(train_dataset.classes)
    # split_nodes_per_area = np.array_split(np.arange(nodes_count), areas)
    split_classes_per_area = np.array_split(np.arange(dataset_labels_count), areas)
    print(f"split_classes_per_area: {split_classes_per_area}")
    index_mapping = {}  # area_id -> list((record_id, label))

    for index, classes in enumerate(split_classes_per_area):
        records_per_class = [(index, lab) for index, (_, lab) in enumerate(train_dataset) if lab in classes]
        # intra-class shuffling
        if shuffling:
            np.random.shuffle(records_per_class)
        bound = int(len(records_per_class) * data_fraction)
        split_classes_per_area[index] = records_per_class[:bound]
        index_mapping[index] = split_classes_per_area[index]

    return index_mapping

result = dataset_to_nodes_partitioning(2, 42, True, 0.2)
print(len(result[0]))
def init_cnn(seed):
    torch.manual_seed(seed)
    model = CNNMnist()
    torch.save(model.state_dict(), f'networks/initial_model_seed_{seed}')

def cnn_loader(seed):
    model = CNNMnist()
    model.load_state_dict(torch.load(f'networks/initial_model_seed_{seed}'))
    return model

def local_training(model, epochs, data, batch_size, seed):
    torch.manual_seed(seed)
    criterion = nn.NLLLoss()
    model.train()
    epoch_loss = []
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
    data_loader = DataLoader(data, batch_size=batch_size, shuffle=True)
    for _ in range(epochs):
        batch_loss = []
        for batch_index, (images, labels) in enumerate(data_loader):
            model.zero_grad()
            log_probs = model(images)
            loss = criterion(log_probs, labels)
            loss.backward()
            optimizer.step()
            batch_loss.append(loss.item())
        mean_epoch_loss = sum(batch_loss) / len(batch_loss)
        epoch_loss.append(mean_epoch_loss)
    return model.state_dict(), sum(epoch_loss) / len(epoch_loss)

def evaluate(model, data, batch_size, seed):
    torch.manual_seed(seed)
    criterion = nn.NLLLoss()
    model.eval()
    loss, total, correct = 0.0, 0.0, 0.0
    data_loader = DataLoader(data, batch_size=batch_size, shuffle=False)
    for batch_index, (images, labels) in enumerate(data_loader):
        outputs = model(images)
        batch_loss = criterion(outputs, labels)
        loss += batch_loss.item()

        _, pred_labels = torch.max(outputs, 1)
        pred_labels = pred_labels.view(-1)
        correct += torch.sum(torch.eq(pred_labels, labels)).item()
        total += len(labels)

    accuracy = correct / total
    return accuracy, loss
    
def train_val_split(data, seed):
    torch.manual_seed(seed)
    train_size = int(len(data) * 0.8)
    validation_size = len(data) - train_size
    train_set, val_set = random_split(data, [train_size, validation_size])
    return train_set, val_set