import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
import pandas as pd
import matplotlib
import glob


def get_areas(name):
    for elem in name.split('_'):
        if 'areas' in elem:
            n_areas = int(elem[-1])
            return n_areas


def get_data(directory, algorithm):
    files = glob.glob(directory)
    df = pd.DataFrame(columns=['Test accuracy', 'Areas', 'Algorithm'])
    for f in files:
        area = get_areas(f)
        acc = pd.read_csv(f).iloc[0].mean()
        df = df._append({'Test accuracy': acc, 'Areas': area, 'Algorithm': algorithm}, ignore_index=True)
    return df


if __name__ == '__main__':

    output_directory = 'charts/test'
    Path(output_directory).mkdir(parents=True, exist_ok=True)

    matplotlib.rcParams.update({'axes.titlesize': 12})
    matplotlib.rcParams.update({'axes.labelsize': 10})

    data_baseline = get_data('data-test-baseline/*.csv', 'Baseline')

    data_self_fl = {}

    for th in [20.0, 40.0, 80.0]:
        d = get_data(f'data-test/*lossThreshold-{th}.csv', 'Self-FL')
        data_self_fl[th] = d

    for th in data_self_fl.keys():
        data_comparison = pd.concat([data_baseline, data_self_fl[th]])
        sns.color_palette('colorblind', as_cmap=True)
        sns.set_palette('colorblind')
        ax = sns.boxplot(data=data_comparison, x='Areas', y='Test accuracy', hue='Algorithm')
        sns.move_legend(ax, 'lower left')
        plt.title(f'Test accuracy when loss threshold {th}')
        plt.ylim(0, 1)
        ax.yaxis.grid(True)
        plt.savefig(f'{output_directory}/test-accuracy-comparison-threshold-{th}.png', dpi=500)
        plt.close()