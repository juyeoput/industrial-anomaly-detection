# Industrial Anomaly Detection for Process Monitoring

Machine learning-based anomaly detection on the Tennessee Eastman Process (TEP) dataset.

This project compares an Isolation Forest baseline with an Autoencoder-based approach for detecting industrial process anomalies, then evaluates lightweight model compression using pruning and dynamic quantization.

## Motivation

Industrial process anomalies are not always visible as large changes in a single sensor.

During baseline analysis, several fault types showed relatively small mean shifts but meaningful changes in multivariate sensor relationships. This motivated moving from a classical Isolation Forest baseline to a reconstruction-based Autoencoder that models the joint behavior of multiple process variables.

The project focuses on three questions:

1. How well does a classical anomaly detection baseline identify different fault patterns?
2. Can an Autoencoder improve detection of subtle multivariate anomalies?
3. How much can the trained model be compressed while preserving useful detection performance?

## Dataset

This project uses the Tennessee Eastman Process (TEP) simulation dataset.

Dataset source:

https://www.kaggle.com/datasets/averkij/tennessee-eastman-process-simulation-dataset

Raw dataset files are not included in this repository.

After downloading the dataset, place the required files under:

```text
data/
├── TEP_FaultFree_Training.csv
├── TEP_FaultFree_Testing.csv
├── TEP_Faulty_Training.csv
└── TEP_Faulty_Testing.csv
```

## Project Structure

```text
industrial-anomaly-detection/
├── model/
│   ├── data_split.py
│   ├── isolation_forest.py
│   ├── autoencoder.py
│   └── autoencoder_lightweight.py
│
├── eda/
│   ├── config.py
│   ├── plot_fault.py
│   ├── fault_run_level_validation.py
│   └── fault2_composition.py
│
├── optimization/
│   ├── bottleneck_analysis_document.md
│   └── operation_strategy_document.md
│
├── data/
├── requirements.txt
└── README.md
```

## Method

### 1. Leakage-safe data split

Fault-free training runs are split at the run level rather than randomly splitting individual rows.

This avoids leakage between samples originating from the same simulated process run.

### 2. Isolation Forest baseline

Isolation Forest is used as the initial anomaly detection baseline.

Evaluation includes:

- overall precision, recall, and F1
- per-fault recall
- early vs. late fault-window analysis
- threshold sensitivity analysis

The baseline performed well on faults with clear shifts, but struggled on several faults characterized by subtler multivariate changes.

### 3. Autoencoder anomaly detection

A fully connected Autoencoder is trained only on normal operating data.

Anomalies are detected using reconstruction error:

```text
Normal process behavior
        ↓
   Autoencoder
        ↓
Reconstruction error
        ↓
Threshold-based anomaly decision
```

The anomaly threshold is calibrated using fault-free validation data.

## Results

### Isolation Forest vs. Autoencoder

| Model            | Precision | Recall |     F1 |
| ---------------- | --------: | -----: | -----: |
| Isolation Forest |    0.9955 | 0.4597 | 0.6289 |
| Autoencoder      |    0.9867 | 0.6614 | 0.7919 |

The Autoencoder substantially improved recall while maintaining high precision.

The largest gains appeared in several faults that were difficult for the Isolation Forest baseline.

Examples:

| Fault | Isolation Forest Recall | Autoencoder Recall |
| ----- | ----------------------: | -----------------: |
| 4     |                    0.09 |              0.998 |
| 11    |                    0.12 |               0.78 |
| 14    |                    0.17 |              0.998 |

These results suggest that reconstruction-based modeling can capture multivariate process relationships that are difficult to detect using an isolation-based baseline alone.

## Model Compression

To explore lightweight deployment, the Autoencoder was evaluated under unstructured pruning and dynamic quantization.

A pruning sensitivity sweep was performed before selecting the final pruning ratio.

### Pruning sweep

| Pruning Amount | Recall |     F1 |
| -------------: | -----: | -----: |
|            10% | 0.6611 | 0.7919 |
|            20% | 0.6543 | 0.7872 |
|            30% | 0.6110 | 0.7547 |
|            40% | 0.5708 | 0.7233 |
|            50% | 0.5738 | 0.7271 |
|            70% | 0.5525 | 0.7095 |

Based on this sensitivity analysis, 15% pruning was selected as a compromise between compression and performance stability.

### Final compressed model

| Version            | Model Size | Precision | Recall |     F1 |
| ------------------ | ---------: | --------: | -----: | -----: |
| Original           |  0.0239 MB |    0.9870 | 0.6606 | 0.7915 |
| Pruned 15%         |  0.0239 MB |    0.9876 | 0.6616 | 0.7923 |
| Pruned + Quantized |  0.0136 MB |    0.9694 | 0.7069 | 0.8176 |

Dynamic quantization reduced the stored model size by approximately 43%.

## Threshold Recalibration

An additional experiment reused the original anomaly threshold after compression.

Although the resulting F1 score appeared higher, false positives increased substantially.

This showed that compression changes the reconstruction-error distribution, so the anomaly threshold should be recalibrated after modifying the model.

This experiment also highlighted an important evaluation lesson:

> F1 alone can hide a large increase in false alarms.

For deployment-oriented anomaly detection, false-positive rate should be evaluated together with precision, recall, and F1.

## Team

- **Yoonseo** — Chemical Engineering, University at Buffalo  
  Process-domain analysis, exploratory data analysis, and fault scenario design

- **Juyeop** — Computer Science, University at Buffalo  
  Anomaly detection modeling, Autoencoder development, evaluation, and model compression

- **Hyeonbeom** — Industrial Engineering  
  Bottleneck analysis, KPI analysis, and operational optimization

## Installation

```bash
pip install -r requirements.txt
```

## Notes

- Raw TEP dataset files are not redistributed in this repository.
- Trained model files and preprocessing artifacts are excluded from version control.
- Results reported above were produced from the project experiments and may vary slightly depending on environment and random state.
