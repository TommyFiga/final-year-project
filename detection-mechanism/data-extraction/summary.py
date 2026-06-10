import pandas as pd

def show_dataset_statistics(dataset: pd.DataFrame, dataset_name: str) -> None:
    print('Dataset: ', dataset_name)

    print('Instances: ', dataset.shape[0])
    print('Attributes: ', dataset.shape[1] - 1)

    print('Dataset balance:')

    balance = dataset['label'].value_counts()

    for label, count in balance.items():
        percentage = count / len(dataset) * 100
        print(f'{label}: {count} ({percentage:.2f}%)')

    print()