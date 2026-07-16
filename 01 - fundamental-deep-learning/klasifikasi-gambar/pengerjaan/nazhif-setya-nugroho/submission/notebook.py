import os
import random
import shutil
from collections import Counter

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.keras.utils.set_random_seed(SEED)

sns.set_style("whitegrid")

print("TensorFlow :", tf.__version__)
print("GPU        :", tf.config.list_physical_devices("GPU"))

# [notebook magic] %pip install -q kagglehub

import kagglehub

dataset_path = kagglehub.dataset_download("alessiocorrado99/animals10")
SRC_DIR = os.path.join(dataset_path, "raw-img")

print("Lokasi dataset :", dataset_path)
print("Isi            :", sorted(os.listdir(SRC_DIR)))

# Kamus nama kelas: Italia -> Inggris
TRANSLATE = {
    "cane": "dog", "cavallo": "horse", "elefante": "elephant",
    "farfalla": "butterfly", "gallina": "chicken", "gatto": "cat",
    "mucca": "cow", "pecora": "sheep", "ragno": "spider",
    "scoiattolo": "squirrel",
}

class_counts = {}
for folder_it in sorted(os.listdir(SRC_DIR)):
    n_files = len(os.listdir(os.path.join(SRC_DIR, folder_it)))
    class_counts[TRANSLATE[folder_it]] = n_files

total_images = sum(class_counts.values())
print(f"Total gambar : {total_images}")
print(f"Jumlah kelas : {len(class_counts)}")
for name, n in sorted(class_counts.items(), key=lambda x: -x[1]):
    print(f"  {name:10s} {n:6d}")

counts_sorted = dict(sorted(class_counts.items(), key=lambda x: -x[1]))

plt.figure(figsize=(10, 5))
bars = plt.bar(counts_sorted.keys(), counts_sorted.values(),
               color=sns.color_palette("viridis", len(counts_sorted)))
for bar, value in zip(bars, counts_sorted.values()):
    plt.text(bar.get_x() + bar.get_width() / 2, value + 40, str(value),
             ha="center", fontsize=9)
plt.title(f"Distribusi Jumlah Gambar per Kelas (total {total_images})")
plt.ylabel("Jumlah gambar")
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()

all_files = []
for folder_it in os.listdir(SRC_DIR):
    folder_path = os.path.join(SRC_DIR, folder_it)
    all_files += [os.path.join(folder_path, f) for f in os.listdir(folder_path)]

sample_files = random.sample(all_files, 2000)
sizes = []
for fp in sample_files:
    with Image.open(fp) as im:
        sizes.append(im.size)  # (lebar, tinggi)

widths = [s[0] for s in sizes]
heights = [s[1] for s in sizes]
unique_sizes = set(sizes)
size_freq = Counter(sizes)

print(f"Jumlah ukuran (lebar x tinggi) UNIK dari 2.000 sampel : {len(unique_sizes)}")
print(f"Rentang lebar  : {min(widths)} - {max(widths)} px")
print(f"Rentang tinggi : {min(heights)} - {max(heights)} px")
print("Contoh 10 ukuran berbeda:", list(unique_sizes)[:10])

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].scatter(widths, heights, alpha=0.25, s=12, c="teal")
axes[0].set_xlabel("Lebar (px)")
axes[0].set_ylabel("Tinggi (px)")
axes[0].set_title(f"Sebaran Resolusi — {len(unique_sizes)} ukuran unik dari 2.000 sampel")

top12 = size_freq.most_common(12)
labels = [f"{w}x{h}" for (w, h), _ in top12]
axes[1].barh(labels[::-1], [n for _, n in top12][::-1], color="coral")
axes[1].set_xlabel("Jumlah gambar")
axes[1].set_title("12 Ukuran Tersering (sisanya sangat beragam)")

fig.suptitle("Bukti: Resolusi Gambar Asli TIDAK Seragam", fontsize=13)
plt.tight_layout()
plt.show()

fig, axes = plt.subplots(5, 6, figsize=(14, 12))
folders_it = sorted(os.listdir(SRC_DIR))

for i, folder_it in enumerate(folders_it):
    folder_path = os.path.join(SRC_DIR, folder_it)
    picks = random.sample(os.listdir(folder_path), 3)
    for j, fname in enumerate(picks):
        ax = axes[i // 2, (i % 2) * 3 + j]
        with Image.open(os.path.join(folder_path, fname)) as im:
            ax.imshow(im.convert("RGB"))
            title = f"{TRANSLATE[folder_it]}\n{im.size[0]}x{im.size[1]}"
        ax.set_title(title, fontsize=8)
        ax.axis("off")

plt.suptitle("Contoh Gambar per Kelas (judul = kelas & ukuran asli)", fontsize=13)
plt.tight_layout()
plt.show()

BASE_DIR = "dataset"

if os.path.exists(BASE_DIR):
    shutil.rmtree(BASE_DIR)

for folder_it, name_en in TRANSLATE.items():
    files = sorted(os.listdir(os.path.join(SRC_DIR, folder_it)))
    random.shuffle(files)  # seed sudah diset -> hasil selalu sama

    n = len(files)
    n_train = int(n * 0.8)
    n_val = int(n * 0.1)
    splits = {
        "train": files[:n_train],
        "val": files[n_train:n_train + n_val],
        "test": files[n_train + n_val:],
    }
    for split_name, split_files in splits.items():
        dest = os.path.join(BASE_DIR, split_name, name_en)
        os.makedirs(dest, exist_ok=True)
        for fname in split_files:
            shutil.copy2(os.path.join(SRC_DIR, folder_it, fname),
                         os.path.join(dest, fname))

for split_name in ["train", "val", "test"]:
    split_dir = os.path.join(BASE_DIR, split_name)
    n_split = sum(len(os.listdir(os.path.join(split_dir, c)))
                  for c in os.listdir(split_dir))
    print(f"{split_name:5s}: {n_split:6d} gambar")

IMG_SIZE = (224, 224)
BATCH_SIZE = 64

train_ds = tf.keras.utils.image_dataset_from_directory(
    os.path.join(BASE_DIR, "train"), image_size=IMG_SIZE,
    batch_size=BATCH_SIZE, shuffle=True, seed=SEED)
val_ds = tf.keras.utils.image_dataset_from_directory(
    os.path.join(BASE_DIR, "val"), image_size=IMG_SIZE,
    batch_size=BATCH_SIZE, shuffle=False)
test_ds = tf.keras.utils.image_dataset_from_directory(
    os.path.join(BASE_DIR, "test"), image_size=IMG_SIZE,
    batch_size=BATCH_SIZE, shuffle=False)

# Versi train TANPA augmentasi & tanpa shuffle -> untuk mengukur akurasi train yang jujur
train_eval_ds = tf.keras.utils.image_dataset_from_directory(
    os.path.join(BASE_DIR, "train"), image_size=IMG_SIZE,
    batch_size=BATCH_SIZE, shuffle=False)

class_names = train_ds.class_names
NUM_CLASSES = len(class_names)
print("Kelas:", class_names)

data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.15),
], name="augmentasi")


@tf.autograph.experimental.do_not_convert
def apply_augmentation(images, labels):
    return data_augmentation(images, training=True), labels


AUTOTUNE = tf.data.AUTOTUNE
train_aug_ds = (train_ds
                .map(apply_augmentation, num_parallel_calls=AUTOTUNE)
                .prefetch(AUTOTUNE))
val_ds = val_ds.cache().prefetch(AUTOTUNE)
test_ds = test_ds.cache().prefetch(AUTOTUNE)
train_eval_ds = train_eval_ds.prefetch(AUTOTUNE)

# Visualisasi: gambar asli vs hasil augmentasi
sample_batch, _ = next(iter(train_ds))
sample_img = sample_batch[0]

fig, axes = plt.subplots(1, 4, figsize=(13, 3.5))
axes[0].imshow(sample_img.numpy().astype("uint8"))
axes[0].set_title("Asli")
axes[0].axis("off")
for i in range(1, 4):
    augmented = data_augmentation(tf.expand_dims(sample_img, 0), training=True)
    axes[i].imshow(tf.squeeze(augmented).numpy().astype("uint8"))
    axes[i].set_title(f"Augmentasi #{i}")
    axes[i].axis("off")
plt.suptitle("Augmentasi hanya diterapkan pada train set")
plt.tight_layout()
plt.show()

base_model = keras.applications.MobileNetV2(
    include_top=False, weights="imagenet", input_shape=(224, 224, 3))
base_model.trainable = False  # Fase 1: bekukan seluruh base model

model = keras.Sequential([
    layers.Input(shape=(224, 224, 3)),
    layers.Rescaling(1.0 / 127.5, offset=-1),
    base_model,
    layers.Conv2D(256, 3, padding="same", activation="relu"),
    layers.MaxPooling2D(2),
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.3),
    layers.Dense(256, activation="relu"),
    layers.Dropout(0.3),
    layers.Dense(NUM_CLASSES, activation="softmax"),
], name="animals10_mobilenetv2")

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-3),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)
model.summary()

callbacks = [
    keras.callbacks.EarlyStopping(
        monitor="val_accuracy", patience=4,
        restore_best_weights=True, verbose=1),
    keras.callbacks.ModelCheckpoint(
        "best_model.keras", monitor="val_accuracy",
        save_best_only=True, verbose=1),
    keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss", factor=0.5, patience=2,
        min_lr=1e-6, verbose=1),
]

EPOCHS_PHASE1 = 8

history1 = model.fit(
    train_aug_ds,
    validation_data=val_ds,
    epochs=EPOCHS_PHASE1,
    callbacks=callbacks,
)

base_model.trainable = True
for layer in base_model.layers[:100]:
    layer.trainable = False

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-5),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

EPOCHS_PHASE2 = 15
history2 = model.fit(
    train_aug_ds,
    validation_data=val_ds,
    epochs=EPOCHS_PHASE1 + EPOCHS_PHASE2,
    initial_epoch=len(history1.epoch),
    callbacks=callbacks,
)

train_loss, train_acc = model.evaluate(train_eval_ds, verbose=0)
val_loss, val_acc = model.evaluate(val_ds, verbose=0)
test_loss, test_acc = model.evaluate(test_ds, verbose=0)

print(f"{'Set':12s} {'Akurasi':>10s} {'Loss':>10s}")
print(f"{'Train':12s} {train_acc:>9.2%} {train_loss:>10.4f}")
print(f"{'Validation':12s} {val_acc:>9.2%} {val_loss:>10.4f}")
print(f"{'Test':12s} {test_acc:>9.2%} {test_loss:>10.4f}")

if train_acc >= 0.95 and test_acc >= 0.95:
    print("\n>> Target akurasi train & test >= 95% TERCAPAI")
elif train_acc >= 0.85 and test_acc >= 0.85:
    print("\n>> Kriteria minimal 85% tercapai (target 95% belum)")

acc = history1.history["accuracy"] + history2.history["accuracy"]
val_accuracy = history1.history["val_accuracy"] + history2.history["val_accuracy"]
loss = history1.history["loss"] + history2.history["loss"]
val_loss_hist = history1.history["val_loss"] + history2.history["val_loss"]
fine_tune_start = len(history1.history["accuracy"])

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].plot(acc, label="Train")
axes[0].plot(val_accuracy, label="Validation")
axes[0].axvline(fine_tune_start - 0.5, ls="--", c="gray", label="Mulai fine-tuning")
axes[0].axhline(0.95, ls=":", c="red", alpha=0.6, label="Target 95%")
axes[0].set_title("Akurasi Model")
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("Akurasi")
axes[0].legend()

axes[1].plot(loss, label="Train")
axes[1].plot(val_loss_hist, label="Validation")
axes[1].axvline(fine_tune_start - 0.5, ls="--", c="gray", label="Mulai fine-tuning")
axes[1].set_title("Loss Model")
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("Loss")
axes[1].legend()

plt.tight_layout()
plt.show()

from sklearn.metrics import classification_report, confusion_matrix

y_true = np.concatenate([y.numpy() for _, y in test_ds], axis=0)
y_pred = np.argmax(model.predict(test_ds, verbose=0), axis=1)

print(classification_report(y_true, y_pred, target_names=class_names, digits=4))

cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(9, 7))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=class_names, yticklabels=class_names)
plt.title("Confusion Matrix — Test Set")
plt.xlabel("Prediksi")
plt.ylabel("Label Sebenarnya")
plt.tight_layout()
plt.show()

model.export("saved_model")
print(sorted(os.listdir("saved_model")))

converter = tf.lite.TFLiteConverter.from_saved_model("saved_model")
tflite_model = converter.convert()

os.makedirs("tflite", exist_ok=True)
with open("tflite/model.tflite", "wb") as f:
    f.write(tflite_model)
with open("tflite/label.txt", "w") as f:
    f.write("\n".join(class_names))

print(f"tflite/model.tflite : {os.path.getsize('tflite/model.tflite') / 1e6:.1f} MB")
print("tflite/label.txt    :", class_names)

# [notebook magic] %pip install -q tensorflowjs

# [notebook magic] !tensorflowjs_converter --input_format=tf_saved_model saved_model tfjs_model

print("Isi tfjs_model/:", sorted(os.listdir("tfjs_model")))

interpreter = tf.lite.Interpreter(model_path="tflite/model.tflite")
interpreter.allocate_tensors()
input_detail = interpreter.get_input_details()[0]
output_detail = interpreter.get_output_details()[0]


def predict_tflite(image_path):
    """Prediksi 1 gambar dengan TF-Lite: return (label, confidence)."""
    with Image.open(image_path) as im:
        img = im.convert("RGB").resize(IMG_SIZE)
    x = np.expand_dims(np.array(img, dtype=np.float32), axis=0)
    interpreter.set_tensor(input_detail["index"], x)
    interpreter.invoke()
    probs = interpreter.get_tensor(output_detail["index"])[0]
    return class_names[int(np.argmax(probs))], float(np.max(probs))


# Ambil 9 gambar acak dari test set
test_files = []
for cls in class_names:
    cls_dir = os.path.join(BASE_DIR, "test", cls)
    test_files += [(os.path.join(cls_dir, f), cls) for f in os.listdir(cls_dir)]
random.shuffle(test_files)
picks = test_files[:9]

fig, axes = plt.subplots(3, 3, figsize=(11, 11))
correct = 0
for ax, (fpath, true_label) in zip(axes.flat, picks):
    pred_label, conf = predict_tflite(fpath)
    ok = pred_label == true_label
    correct += ok
    with Image.open(fpath) as im:
        ax.imshow(im.convert("RGB"))
    ax.set_title(f"Prediksi: {pred_label} ({conf:.0%})\nAsli: {true_label} {'✓' if ok else '✗'}",
                 fontsize=10, color="green" if ok else "red")
    ax.axis("off")
plt.suptitle(f"Inference TF-Lite — {correct}/9 benar", fontsize=14)
plt.tight_layout()
plt.show()

# Kemas semua artefak model jadi 1 zip untuk diunduh dari Colab
import zipfile

with zipfile.ZipFile("animals10_models.zip", "w", zipfile.ZIP_DEFLATED) as zf:
    for folder in ["saved_model", "tflite", "tfjs_model"]:
        for root, _, files in os.walk(folder):
            for f in files:
                fp = os.path.join(root, f)
                zf.write(fp, fp)

print(f"animals10_models.zip: {os.path.getsize('animals10_models.zip') / 1e6:.1f} MB")
print("Unduh dari panel Files di kiri Colab.")
