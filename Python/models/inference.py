import numpy as np
import pandas as pd
from tensorflow import keras
from tensorflow.keras.models import model_from_json
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve, auc
from matplotlib import pyplot as plt
import seaborn as sns
from Python.models.training import max_pool_mse

MODEL_PATH = './Python/models/results/'
DATA_PATH = './Python/data/h5xydata/'
MODEL_NAME = 'spc_dnn_rd_20'
#LOSS = keras.losses.mse
LOSS = max_pool_mse

def find_threshold(model, x_train):
  reconstructions = model.predict(x_train)
  # provides losses of individual instances
  reconstruction_errors = LOSS(reconstructions, x_train)
  # threshold for anomaly scores
  threshold = np.mean(reconstruction_errors.numpy()) \
      + np.std(reconstruction_errors.numpy())
  return threshold

def get_predictions(model, x_test_scaled, threshold):
  predictions = model.predict(x_test_scaled)
  #print("PRED SHAPE:-----------------", predictions.shape)
  # provides losses of individual instances
  errors = LOSS(predictions, x_test_scaled)
  #print("ERROR SHAPE:-----------------", errors.shape)
  # 0 = anomaly, 1 = normal
  anomaly_mask = pd.Series(errors) > threshold
  preds = anomaly_mask.map(lambda x: 1.0 if x == True else 0.0)
  return preds

def cm_plot(y_pred, y_test):
    LABELS = ["Normal", "Anomaly"]
    conf_matrix = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(12, 12))
    sns.heatmap(conf_matrix, xticklabels=LABELS, yticklabels=LABELS, annot=True, fmt="d")
    plt.title("Confusion matrix")
    plt.ylabel('True class')
    plt.xlabel('Predicted class')
    plt.savefig(MODEL_PATH+MODEL_NAME+'_cm_plot.png')
    plt.show()


def recon_error_plot(error_df):
    # Error for BKG class
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharex=True, sharey=True, dpi=150)
    fig.tight_layout(pad=5.0)

    normal_error_df = error_df[(error_df['true_class']== 0)]
    _ = axes[0].hist(normal_error_df.reconstruction_mse.values, bins=10)

    axes[0].title.set_text("Reconstruction Error: Background data")
    axes[0].set_xlabel("Reconstruction Error")
    axes[0].set_ylabel("Data (binning = 10)")

    # Error for electron class
    ad_error_df = error_df[error_df['true_class'] == 1]
    _ = axes[1].hist(ad_error_df.reconstruction_mse.values, bins=10)

    axes[1].title.set_text("Reconstruction Error: Anolmalous Data")
    axes[1].set_ylabel("Data (binning = 10)")
    axes[1].set_xlabel("Reconstruction Error (MSE)")

    plt.savefig(MODEL_PATH+MODEL_NAME+'_recon_error.png')
    plt.show()

def ploting_curves(y_test, y_pred):

    fprs, tprs, _ = roc_curve(y_test, y_pred)
    precisions, recalls, _ = precision_recall_curve(y_test, y_pred)
    roc_auc_val = auc(fprs, tprs) # area-under-curve for ROC
    pr_auc_val = auc(recalls, precisions) # area-under-curve for PR-curve

    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharex=True, sharey=True, dpi=150)
    fig.tight_layout(pad=5.0)

    # nice palette from seaborn
    pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)

    # plot pr-curve
    axes[0].plot(
        recalls,
        precisions,
        marker="",
        label=MODEL_NAME+" PR AUC = {:.3f}".format(pr_auc_val),
        color=pal[5],
        linewidth=1,
    )

    # plot no-skill model line
    axes[0].plot(
        np.array([0, 1]),
        np.array([0.073, 0.073]),
        marker="",
        linestyle="--",
        label="No skill model",
        color="orange",
        linewidth=1,
    )

    axes[0].legend()
    axes[0].title.set_text("Precision-Recall Curve")
    axes[0].set_xlabel("Recall")
    axes[0].set_ylabel("Precision")

    # plot ROC curve
    axes[1].plot(
        fprs, 
        tprs, 
        marker="", 
        label=MODEL_NAME+" ROC AUC = {:.3f}".format(roc_auc_val), 
        color=pal[5], 
        linewidth=1,
    )

    # plot no-skill line
    axes[1].plot(
        np.array([0, 1]),
        np.array([0, 1]),
        marker="",
        linestyle="--",
        label="No skill",
        color="orange",
        linewidth=1,
    )

    axes[1].legend()
    axes[1].title.set_text("ROC Curve")
    axes[1].set_xlabel("False Positive Rate")
    axes[1].set_ylabel("True Positive Rate")

    for ax in axes.flatten():
        ax.yaxis.set_tick_params(labelleft=True, which="major")
        ax.grid(False)

    plt.savefig(MODEL_PATH+MODEL_NAME+'_curves.png')
    plt.show()

def class_thresh_error(error_df, threshold):
    """Recon error vs data points index: giving info on the threshold 
    and reconstruction error for different classes"""
    
    groups = error_df.groupby('true_class')
    fig, ax = plt.subplots()
    for name, group in groups:
        ax.plot(group.index, group.reconstruction_mse, marker='o', ms=3.5, linestyle='',
                label= "Anomaly Data" if name == 1 else "Normal")
    ax.hlines(threshold, ax.get_xlim()[0], ax.get_xlim()[1], colors="r", zorder=100, label='Threshold')
    ax.legend()
    plt.title("Reconstruction error for different classes")
    plt.ylabel("Reconstruction error")
    plt.xlabel("Data point index")
    plt.savefig(MODEL_PATH+MODEL_NAME+'_class_error.png')
    plt.show()

if __name__=='__main__':
    x_train = np.load(DATA_PATH+'x_train.npy')
    x_test = np.load(DATA_PATH+'x_test.npy')
    y_test = np.load(DATA_PATH+'y_test.npy')

    # load json and create model
    model_json = open(MODEL_PATH+MODEL_NAME+'.json', 'r')
    model_arch = model_json.read()
    model_json.close()
    model = model_from_json(model_arch)
    # load weights into new model
    model.load_weights(MODEL_PATH+'weights_%s.h5' % MODEL_NAME)
    print("Loaded model from disk")

    predictions = model.predict(x_test)
    mse = keras.losses.mse(predictions, x_test)
    msle = keras.losses.msle(predictions, x_test)
    error_df = pd.DataFrame({'reconstruction_mse': mse,
                            'reconstruction_msle': msle,
                            'true_class': y_test})
    print(error_df.describe())
    recon_error_plot(error_df)

    # Plotting ROC and PR curves
    ploting_curves(error_df.true_class, error_df.reconstruction_msle)

    threshold = find_threshold(model, x_train)
    print(f"Threshold: {threshold}")
    class_thresh_error(error_df, threshold)

    predictions = get_predictions(model, x_test, threshold)
    cm_plot(predictions, y_test)
    print(accuracy_score(predictions, y_test))
    print(classification_report(predictions, y_test))
