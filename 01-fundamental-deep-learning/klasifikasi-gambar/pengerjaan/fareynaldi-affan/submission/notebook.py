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

dataset_path = kagglehub.dataset_download("mostafaabla/garbage-classification")
SRC_DIR = os.path.join(dataset_path, "garbage_classification")

print("Lokasi dataset :", dataset_path)
print("Isi (kelas)    :", sorted(os.listdir(SRC_DIR)))

# Hitung jumlah gambar per kelas + total (untuk EDA & bukti kriteria)
class_counts = {}
for cls in sorted(os.listdir(SRC_DIR)):
    cls_dir = os.path.join(SRC_DIR, cls)
    if os.path.isdir(cls_dir):
        class_counts[cls] = len(os.listdir(cls_dir))

TOTAL = sum(class_counts.values())
NUM_CLASSES_RAW = len(class_counts)
imbalance = max(class_counts.values()) / min(class_counts.values())

print(f"Total gambar  : {TOTAL}")
print(f"Jumlah kelas  : {NUM_CLASSES_RAW}")
print(f"Imbalance     : {imbalance:.1f} : 1  (terbanyak/tersedikit)")
for cls, n in sorted(class_counts.items(), key=lambda x: -x[1]):
    print(f"  {cls:14s} {n}")

counts_sorted = dict(sorted(class_counts.items(), key=lambda x: -x[1]))

plt.figure(figsize=(11, 5))
bars = plt.bar(counts_sorted.keys(), counts_sorted.values(), color="mediumseagreen")
plt.bar_label(bars, fontsize=8)
plt.title("Distribusi Jumlah Gambar per Kelas (Garbage Classification)")
plt.ylabel("Jumlah gambar")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

all_files = []
for cls in os.listdir(SRC_DIR):
    cls_path = os.path.join(SRC_DIR, cls)
    all_files += [os.path.join(cls_path, f) for f in os.listdir(cls_path)]

sample_files = random.sample(all_files, 3000)
sizes = []
for fp in sample_files:
    with Image.open(fp) as im:
        sizes.append(im.size)  # (lebar, tinggi)

widths = [s[0] for s in sizes]
heights = [s[1] for s in sizes]
unique_sizes = set(sizes)
size_freq = Counter(sizes)

print(f"Jumlah ukuran (lebar x tinggi) UNIK dari 3.000 sampel : {len(unique_sizes)}")
print(f"Rentang lebar  : {min(widths)} - {max(widths)} px")
print(f"Rentang tinggi : {min(heights)} - {max(heights)} px")
print("Contoh 10 ukuran berbeda:", list(unique_sizes)[:10])

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].scatter(widths, heights, alpha=0.25, s=12, c="teal")
axes[0].set_xlabel("Lebar (px)")
axes[0].set_ylabel("Tinggi (px)")
axes[0].set_title(f"Sebaran Resolusi — {len(unique_sizes)} ukuran unik dari 3.000 sampel")

top12 = size_freq.most_common(12)
labels = [f"{w}x{h}" for (w, h), _ in top12]
axes[1].barh(labels[::-1], [n for _, n in top12][::-1], color="coral")
axes[1].set_xlabel("Jumlah gambar")
axes[1].set_title("12 Ukuran Tersering (sisanya sangat beragam)")

fig.suptitle("Bukti: Resolusi Gambar Asli TIDAK Seragam", fontsize=13)
plt.tight_layout()
plt.show()

fig, axes = plt.subplots(6, 6, figsize=(14, 14))
classes_sorted = sorted(os.listdir(SRC_DIR))

for i, cls in enumerate(classes_sorted):
    cls_path = os.path.join(SRC_DIR, cls)
    picks = random.sample(os.listdir(cls_path), 3)
    for j, fname in enumerate(picks):
        ax = axes[i // 2, (i % 2) * 3 + j]
        with Image.open(os.path.join(cls_path, fname)) as im:
            ax.imshow(im.convert("RGB"))
            ax.set_title(f"{cls}\n{im.size[0]}x{im.size[1]}", fontsize=8)
        ax.axis("off")

plt.suptitle("Contoh Gambar per Kelas (judul = kelas & ukuran asli)", fontsize=13)
plt.tight_layout()
plt.show()

BASE_DIR = "dataset"

if os.path.exists(BASE_DIR):
    shutil.rmtree(BASE_DIR)

for cls in sorted(os.listdir(SRC_DIR)):
    src_cls = os.path.join(SRC_DIR, cls)
    files = sorted(os.listdir(src_cls))
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
        dest = os.path.join(BASE_DIR, split_name, cls)
        os.makedirs(dest, exist_ok=True)
        for fname in split_files:
            shutil.copy2(os.path.join(src_cls, fname), os.path.join(dest, fname))

for split_name in ["train", "val", "test"]:
    split_dir = os.path.join(BASE_DIR, split_name)
    n_split = sum(len(os.listdir(os.path.join(split_dir, c)))
                  for c in os.listdir(split_dir))
    print(f"{split_name:5s}: {n_split:6d} gambar")

IMG_SIZE = (224, 224)
BATCH_SIZE = 32

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
    layers.RandomRotation(0.15),
    layers.RandomZoom(0.2),
    layers.RandomContrast(0.1),
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
    axes[i].imshow(tf.clip_by_value(tf.squeeze(augmented), 0, 255).numpy().astype("uint8"))
    axes[i].set_title(f"Augmentasi #{i}")
    axes[i].axis("off")
plt.suptitle("Augmentasi hanya diterapkan pada train set")
plt.tight_layout()
plt.show()

base_model = keras.applications.EfficientNetV2B0(
    include_top=False, weights="imagenet", input_shape=(224, 224, 3))
base_model.trainable = False  # Fase 1: bekukan seluruh base model

model = keras.Sequential([
    layers.Input(shape=(224, 224, 3)),
    base_model,                                             # ekstraktor fitur (EfficientNetV2B0)
    layers.Conv2D(128, 3, padding="same", activation="relu"),
    layers.BatchNormalization(),
    layers.MaxPooling2D(),
    layers.Conv2D(64, 3, padding="same", activation="relu"),
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.4),
    layers.Dense(128, activation="relu"),
    layers.Dropout(0.3),
    layers.Dense(NUM_CLASSES, activation="softmax"),
], name="garbage_efficientnetv2b0")

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-3),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)
model.summary()

from sklearn.utils.class_weight import compute_class_weight

# Kumpulkan seluruh label train (dari versi tanpa shuffle) untuk hitung bobot kelas
y_train_all = np.concatenate([y.numpy() for _, y in train_eval_ds], axis=0)
weights = compute_class_weight(
    "balanced", classes=np.arange(NUM_CLASSES), y=y_train_all)
class_weight = {i: float(w) for i, w in enumerate(weights)}
print("class_weight:")
for i, w in class_weight.items():
    print(f"  {class_names[i]:14s} {w:.3f}")

callbacks = [
    keras.callbacks.EarlyStopping(
        monitor="val_accuracy", patience=5,
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
    class_weight=class_weight,
    callbacks=callbacks,
)

FINE_TUNE_AT = 150

base_model.trainable = True
# Bekukan layer bawah
for layer in base_model.layers[:FINE_TUNE_AT]:
    layer.trainable = False
# Bekukan SEMUA BatchNormalization (penting untuk EfficientNet)
for layer in base_model.layers:
    if isinstance(layer, layers.BatchNormalization):
        layer.trainable = False

n_trainable = sum(1 for l in base_model.layers if l.trainable)
print(f"Layer base yang dilatih: {n_trainable} / {len(base_model.layers)}")

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
    class_weight=class_weight,
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
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt="d", cmap="Greens",
            xticklabels=class_names, yticklabels=class_names)
plt.title("Confusion Matrix — Test Set")
plt.xlabel("Prediksi")
plt.ylabel("Label Sebenarnya")
plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()

model.export("saved_model")
print(sorted(os.listdir("saved_model")))

converter = tf.lite.TFLiteConverter.from_saved_model("saved_model")
converter.optimizations = [tf.lite.Optimize.DEFAULT]
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
    x = np.expand_dims(np.array(img, dtype=np.float32), axis=0)  # [0,255] -> EfficientNet normalisasi internal
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

with zipfile.ZipFile("garbage_models.zip", "w", zipfile.ZIP_DEFLATED) as zf:
    for folder in ["saved_model", "tflite", "tfjs_model"]:
        for root, _, files in os.walk(folder):
            for f in files:
                fp = os.path.join(root, f)
                zf.write(fp, fp)

print(f"garbage_models.zip: {os.path.getsize('garbage_models.zip') / 1e6:.1f} MB")
print("Unduh dari panel Files di kiri Colab.")
