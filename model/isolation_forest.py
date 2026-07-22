from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
from data_split import load_and_split

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# will use several sensors later
SENSOR_COLS = [f"xmeas_{i}" for i in range(1, 42)] + [f"xmv_{i}" for i in range(1, 12)]


def load_csv(filename):
    return pd.read_csv(DATA_DIR / filename)


# train data
def train_isolation_forest(train_df, random_state=42):
    # only sensors
    X_train = train_df[SENSOR_COLS]
    model = IsolationForest(
        n_estimators=200,
        contamination='auto',
        random_state=random_state,
        n_jobs=-1
    )
    model.fit(X_train)
    return model

# validation data
def check_on_validation(model, val_df):
    X_val = val_df[SENSOR_COLS]
    scores = model.score_samples(X_val)
    print(f"Validation score -> mean: {scores.mean():.4f}, std: {scores.std():.4f}")
    return scores

# set threshold based on the FaultFree test data
def set_threshold(model, faultfree_testing_df, target_fpr=0.05):
    normal_df = faultfree_testing_df[faultfree_testing_df['faultNumber'] == 0]
    X_normal = normal_df[SENSOR_COLS]

    scores = model.score_samples(X_normal)
    threshold = np.percentile(scores, target_fpr * 100)
    predicted_anomaly = scores < threshold
    actual_fpr = predicted_anomaly.mean()
    print(f"Target FPR: {target_fpr}, Actual FPR: {actual_fpr:.4f}")
    return threshold

# evaluate with real faulty test data
def evaluate_on_faulty(model, threshold, faulty_testing_df, sample_cutoff=160):
    df = faulty_testing_df.copy()

    # Right answers
    df['true_label'] = (df['sample'] >= sample_cutoff).astype(int)

    X = df[SENSOR_COLS]
    scores = model.score_samples(X)

    # Answers to be tested
    df['predicted_label'] = (scores < threshold).astype(int)

    precision = precision_score(df['true_label'], df['predicted_label'])
    recall = recall_score(df['true_label'], df['predicted_label'])
    f1 = f1_score(df['true_label'], df['predicted_label'])
    cm = confusion_matrix(df['true_label'], df['predicted_label'])

    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1: {f1:.4f}")
    print("Confusion Matrix:\n", cm)

    return {'precision': precision, 'recall': recall, 'f1': f1, 'confusion_matrix': cm}

# need to know if the model missed in specific faults or overall
def evaluate_by_fault(model, threshold, faulty_testing_df, sample_cutoff=160, late_start=None):
    df = faulty_testing_df.copy()
    df['true_label'] = (df['sample'] >= sample_cutoff).astype(int)

    X = df[SENSOR_COLS]
    scores = model.score_samples(X)
    df['predicted_label'] = (scores < threshold).astype(int)

    anomaly_only = df[df['true_label'] == 1]

    if late_start is not None:
        anomaly_only = anomaly_only[anomaly_only['sample'] >= late_start]

    label = f"Recall (sample>={late_start})" if late_start else "Recall (full)"
    print(f"{'Fault':<8}{label:<20}{'Caught':<12}{'Missed'}")
    for fault_num in sorted(anomaly_only['faultNumber'].unique()):
        subset = anomaly_only[anomaly_only['faultNumber'] == fault_num]
        caught = subset['predicted_label'].sum()
        total = len(subset)
        recall = caught / total
        print(f"{fault_num:<8}{recall:<10.4f}{caught:<12}{total - caught}")

# need to check if the current threshold is appropriate
def inspect_score_distribution(model, threshold, faulty_testing_df, fault_numbers, sample_cutoff=160):
    df = faulty_testing_df.copy()
    df['true_label'] = (df['sample'] >= sample_cutoff).astype(int)
    X = df[SENSOR_COLS]
    df['score'] = model.score_samples(X)

    normal_scores = df[df['true_label'] == 0]['score']
    print(f"Normal scores      -> mean: {normal_scores.mean():.4f}, median: {normal_scores.median():.4f}")
    print(f"Current threshold  -> {threshold:.4f}")
    print()

    for fault_num in fault_numbers:
        fault_scores = df[(df['faultNumber'] == fault_num) & (df['true_label'] == 1)]['score']
        pct_below = (fault_scores < threshold).mean()
        print(f"Fault {fault_num}: mean={fault_scores.mean():.4f}, median={fault_scores.median():.4f}, "
              f"% caught at current threshold={pct_below:.4f}")

if __name__ == "__main__":
    print("1. Load & split (FaultFree Training)")
    train_df, val_df = load_and_split('TEP_FaultFree_Training.csv')

    print("\n2. Train Isolation Forest - train split only")
    model = train_isolation_forest(train_df)

    print("\n3. Sanity check on validation split")
    check_on_validation(model, val_df)

    print("\n4. Set threshold (FaultFree Testing)")
    faultfree_testing_df = load_csv("TEP_FaultFree_Testing.csv")
    threshold = set_threshold(model, faultfree_testing_df, target_fpr=0.05)

    print("\n5. Final evaluation (Faulty Testing)")
    faulty_testing_df = load_csv("TEP_Faulty_Testing.csv")
    results = evaluate_on_faulty(model, threshold, faulty_testing_df)

    print("\n6. Recall by fault number (full anomaly window)")
    evaluate_by_fault(model, threshold, faulty_testing_df)

    print("\n7. Recall by fault number (late window only)")
    evaluate_by_fault(model, threshold, faulty_testing_df, late_start=300)

    # the lowest recalls(4,11,14) VS the highest recalls(1,8)
    print("\n8. Score distribution check (threshold sensitivity)")
    inspect_score_distribution(model, threshold, faulty_testing_df, fault_numbers=[4, 11, 14, 1, 8])