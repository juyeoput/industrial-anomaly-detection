from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.utils.prune as prune
import os
import copy
import joblib


from data_split import load_and_split
from autoencoder import (
    load_csv,
    train_autoencoder,
    compute_reconstruction_error,
    set_threshold,
    evaluate_on_faulty,
    evaluate_by_fault,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

MODEL_CACHE_PATH = "trained_autoencoder.pth"
SCALER_CACHE_PATH = "trained_scaler.pkl"

def get_or_train_model(train_df, bottleneck_dim=16, epochs=50):
    """
    Loads a previously trained model + scaler if a cache exists
    """
    from autoencoder import Autoencoder, SENSOR_COLS, DEVICE

    if os.path.exists(MODEL_CACHE_PATH) and os.path.exists(SCALER_CACHE_PATH):
        print(f"Loading cached model from {MODEL_CACHE_PATH}")
        model = Autoencoder(input_dim=len(SENSOR_COLS), bottleneck_dim=bottleneck_dim).to(DEVICE)
        model.load_state_dict(torch.load(MODEL_CACHE_PATH, map_location=DEVICE))
        scaler = joblib.load(SCALER_CACHE_PATH)
        return model, scaler

    print("No cached model found, training from scratch")
    model, scaler = train_autoencoder(train_df, bottleneck_dim=bottleneck_dim, epochs=epochs)
    torch.save(model.state_dict(), MODEL_CACHE_PATH)
    joblib.dump(scaler, SCALER_CACHE_PATH)
    return model, scaler

def count_nonzero_params(model):
    total = 0
    nonzero = 0
    for param in model.parameters():
        total += param.numel()
        nonzero += torch.count_nonzero(param).item()
    return total, nonzero


def apply_pruning(model, amount=0.3):
    for module in model.modules():
        if isinstance(module, nn.Linear):
            prune.l1_unstructured(module, name="weight", amount=amount)
    return model


def make_pruning_permanent(model):
    for module in model.modules():
        if isinstance(module, nn.Linear):
            prune.remove(module, "weight")
    return model


def apply_dynamic_quantization(model):
    torch.backends.quantized.engine = 'qnnpack'

    quantized_model = torch.quantization.quantize_dynamic(
        model.cpu(), {nn.Linear}, dtype=torch.qint8
    )
    return quantized_model


def get_model_size_mb(model):
    torch.save(model.state_dict(), "_temp_model.pth")
    size_mb = os.path.getsize("_temp_model.pth") / (1024 * 1024)
    os.remove("_temp_model.pth")
    return size_mb

def sweep_pruning_amounts(model, scaler, faultfree_testing_df, faulty_testing_df, amounts):
    """
    check where pruning starts to seriously damage
    the model's ability to reconstruct even normal data.
    """
    results = []

    for amount in amounts:
        # deepcopy so each pruning amount starts from the same original weights,
        # not from an already-pruned model
        model_copy = copy.deepcopy(model)

        model_copy = apply_pruning(model_copy, amount=amount)
        model_copy = make_pruning_permanent(model_copy)

        normal_df = faultfree_testing_df[faultfree_testing_df['faultNumber'] == 0]
        normal_errors = compute_reconstruction_error(model_copy, scaler, normal_df)

        threshold = set_threshold(model_copy, scaler, faultfree_testing_df, target_fpr=0.05)
        eval_results = evaluate_on_faulty(model_copy, scaler, threshold, faulty_testing_df)

        total, nonzero = count_nonzero_params(model_copy)

        results.append({
            'amount': amount,
            'normal_error_mean': normal_errors.mean(),
            'normal_error_std': normal_errors.std(),
            'threshold': threshold,
            'precision': eval_results['precision'],
            'recall': eval_results['recall'],
            'f1': eval_results['f1'],
            'nonzero_params': nonzero,
        })

    return results


def print_sweep_results(results):
    print(f"\n{'Amount':<10}{'NormalErr':<12}{'Threshold':<12}{'Precision':<12}{'Recall':<12}{'F1':<10}{'Nonzero'}")
    for r in results:
        print(
            f"{r['amount']:<10.2f}"
            f"{r['normal_error_mean']:<12.4f}"
            f"{r['threshold']:<12.4f}"
            f"{r['precision']:<12.4f}"
            f"{r['recall']:<12.4f}"
            f"{r['f1']:<10.4f}"
            f"{r['nonzero_params']}"
        )


def run_pruning_sweep():
    print("1. Load data & retrain baseline Autoencoder")
    train_df, val_df = load_and_split("TEP_FaultFree_Training.csv")
    model, scaler = get_or_train_model(train_df, bottleneck_dim=16, epochs=50)

    faultfree_testing_df = load_csv("TEP_FaultFree_Testing.csv")
    faulty_testing_df = load_csv("TEP_Faulty_Testing.csv")

    print("\n=== Pruning Amount Sweep ===")
    sweep_results = sweep_pruning_amounts(
        model, scaler, faultfree_testing_df, faulty_testing_df,
        amounts=[0.1, 0.2, 0.3, 0.4, 0.5, 0.7]
    )
    print_sweep_results(sweep_results)


def run_final_pipeline():
    print("1. Load data & retrain baseline Autoencoder")
    train_df, val_df = load_and_split("TEP_FaultFree_Training.csv")
    model, scaler = get_or_train_model(train_df, bottleneck_dim=16, epochs=50)

    faultfree_testing_df = load_csv("TEP_FaultFree_Testing.csv")
    faulty_testing_df = load_csv("TEP_Faulty_Testing.csv")

    print("\n2. Baseline (original) evaluation")
    threshold_orig = set_threshold(model, scaler, faultfree_testing_df, target_fpr=0.05)
    results_orig = evaluate_on_faulty(model, scaler, threshold_orig, faulty_testing_df)

    total_orig, nonzero_orig = count_nonzero_params(model)
    size_orig = get_model_size_mb(model)
    print(
        f"Params (total/nonzero): {total_orig}/{nonzero_orig}, Model size: {size_orig:.4f} MB"
    )

    print("\n3. Apply Pruning (15%)")
    model_pruned = apply_pruning(model, amount=0.15)
    model_pruned = make_pruning_permanent(model_pruned)

    threshold_pruned = set_threshold(
        model_pruned, scaler, faultfree_testing_df, target_fpr=0.05
    )
    results_pruned = evaluate_on_faulty(
        model_pruned, scaler, threshold_pruned, faulty_testing_df
    )
    # fixed-threshold comparison: what happens if not recalibrate
    # and reuse the original model's threshold on the pruned model
    results_pruned_fixed = evaluate_on_faulty(
        model_pruned, scaler, threshold_orig, faulty_testing_df
    )
    total_pruned, nonzero_pruned = count_nonzero_params(model_pruned)
    size_pruned = get_model_size_mb(model_pruned)
    print(
        f"Params (total/nonzero): {total_pruned}/{nonzero_pruned}, Model size: {size_pruned:.4f} MB"
    )

    print("\n4. Apply Dynamic Quantization (on pruned model)")
    model_quantized = apply_dynamic_quantization(model_pruned)

    threshold_quant = set_threshold(
        model_quantized, scaler, faultfree_testing_df, target_fpr=0.05
    )
    results_quant = evaluate_on_faulty(
        model_quantized, scaler, threshold_quant, faulty_testing_df
    )
    # fixed-threshold comparison: same idea, for the pruned+quantized model
    results_quant_fixed = evaluate_on_faulty(
        model_quantized, scaler, threshold_orig, faulty_testing_df
    )
    size_quant = get_model_size_mb(model_quantized)
    print(f"Model size: {size_quant:.4f} MB")

    print("\n5. Summary comparison (recalibrated threshold per stage)")
    print(f"{'Version':<25}{'Size (MB)':<12}{'Precision':<12}{'Recall':<12}{'F1'}")
    print(
        f"{'Original':<25}{size_orig:<12.4f}{results_orig['precision']:<12.4f}{results_orig['recall']:<12.4f}{results_orig['f1']:.4f}"
    )
    print(
        f"{'Pruned (15%)':<25}{size_pruned:<12.4f}{results_pruned['precision']:<12.4f}{results_pruned['recall']:<12.4f}{results_pruned['f1']:.4f}"
    )
    print(
        f"{'Pruned+Quantized':<25}{size_quant:<12.4f}{results_quant['precision']:<12.4f}{results_quant['recall']:<12.4f}{results_quant['f1']:.4f}"
    )

    print("\n6. Summary comparison (FIXED original threshold, no recalibration)")
    print(f"{'Version':<25}{'Precision':<12}{'Recall':<12}{'F1'}")
    print(
        f"{'Pruned (15%)':<25}{results_pruned_fixed['precision']:<12.4f}{results_pruned_fixed['recall']:<12.4f}{results_pruned_fixed['f1']:.4f}"
    )
    print(
        f"{'Pruned+Quantized':<25}{results_quant_fixed['precision']:<12.4f}{results_quant_fixed['recall']:<12.4f}{results_quant_fixed['f1']:.4f}"
    )
    
    print("\n7. Confusion matrices (to check actual FP/FN counts under fixed threshold)")
    print("Pruned (15%) - fixed threshold:")
    print(results_pruned_fixed['confusion_matrix'])
    print("Pruned+Quantized - fixed threshold:")
    print(results_quant_fixed['confusion_matrix'])

    print("\nFor comparison — Pruned (15%) - recalibrated threshold:")
    print(results_pruned['confusion_matrix'])
    print("Pruned+Quantized - recalibrated threshold:")
    print(results_quant['confusion_matrix'])

if __name__ == "__main__":
    # run_pruning_sweep()
    run_final_pipeline()