from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_and_split(filename, test_size=0.2, random_state=42):
    df = pd.read_csv(DATA_DIR / filename)

    runs = df['simulationRun'].unique()
    train_runs, val_runs = train_test_split(runs, test_size=test_size, random_state=random_state)

    train_df = df[df['simulationRun'].isin(train_runs)]
    val_df = df[df['simulationRun'].isin(val_runs)]

    return train_df, val_df

if __name__ == "__main__":
    train_df, val_df = load_and_split('TEP_FaultFree_Training.csv')

    print("Train shape is:", train_df.shape)
    print("Val shape:", val_df.shape)

    print("Train runs:", train_df['simulationRun'].nunique())
    print("Val runs:", val_df['simulationRun'].nunique())