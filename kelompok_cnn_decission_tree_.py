# -*- coding: utf-8 -*-
"""Kelompok_CNN-Decission Tree .ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12C8QDQzTF6-hXsReRNMT8qbl1yZch9bE

# UAS Machine Learning
Anggota Kelompok :


1. 432022611037/Muhammad Daffa Nurahman
2. 4329226110/Muhammad Ariel Naafi
3. 4320226110/Muhammad Amrico Putra
4.4320226110/Muhammad Alif Makasau

# Import file dataset dari Google Drive
"""

from google.colab import drive

drive.mount('/content/gdrive')

"""# Path Folder

"""

!ls "/content/gdrive/My Drive/Colab Notebooks/ML/rockpaperscissors"

"""## Import Library"""

import numpy as np
import os
from glob import glob
import cv2
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from random import randint


from tensorflow import keras
import tensorflow as tf
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten, Input, Dropout
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.preprocessing.image import img_to_array


from PIL import Image
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay, classification_report, accuracy_score
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import OneHotEncoder

"""## Membaca Dataset"""

train_dir = '../content/gdrive/MyDrive/Colab Notebooks/ML/rockpaperscissors/rps-cv-images'
test_dir = '../content/gdrive/MyDrive/Colab Notebooks/ML/tes-set'
classes = os.listdir(train_dir)
print(classes)

"""# Melihat Jumlah Dataset yang dimiliki"""

# Definisi direktori dataset
build_dir = '../content/gdrive/MyDrive/Colab Notebooks/ML/rockpaperscissors/rps-cv-images'
rock_dir = os.path.join(build_dir, 'rock')
paper_dir = os.path.join(build_dir, 'paper')
scissors_dir = os.path.join(build_dir, 'scissors')

# Membuat DataFrame untuk menampilkan jumlah gambar
class_counts = [len(os.listdir(rock_dir)),
                len(os.listdir(paper_dir)),
                len(os.listdir(scissors_dir))]
class_names = ['Rock', 'Paper', 'Scissors']
class_df = pd.DataFrame(data=class_counts, index=class_names, columns=['Total Image'])
print(class_df)

"""# Melihat Jumlah Data Testing yang dimiliki

"""

# Definisi direktori dataset
build_dir = '../content/gdrive/MyDrive/Colab Notebooks/ML/tes-set'
rock_dir = os.path.join(build_dir, 'rock')
paper_dir = os.path.join(build_dir, 'paper')
scissors_dir = os.path.join(build_dir, 'scissors')

# Membuat DataFrame untuk menampilkan jumlah gambar
class_counts = [len(os.listdir(rock_dir)),
                len(os.listdir(paper_dir)),
                len(os.listdir(scissors_dir))]
class_names = ['Rock', 'Paper', 'Scissors']
class_df = pd.DataFrame(data=class_counts, index=class_names, columns=['Total Image'])
print(class_df)

# Inisiasi dataset untuk Training dan Validation dengan resize gambar
X_train_val = []
y_train_val = []
class_names = sorted(os.listdir(train_dir))  # Urutkan daftar direktori

for i, cls in enumerate(class_names):
    for img in os.listdir(os.path.join(train_dir, cls)):
        image = cv2.imread(os.path.join(train_dir, cls, img), cv2.IMREAD_GRAYSCALE)
        image = cv2.resize(image, (64, 64))  # Pastikan ukuran gambar sesuai
        X_train_val.append(image)
        y_train_val.append(i)

# Inisiasi dataset untuk Test dengan resize gambar
X_test = []
y_test = []

# Verify the 'test_dir' path exists
if os.path.exists(test_dir):
    for i, cls in enumerate(class_names):  # Gunakan class_names yang sama
        for img in os.listdir(os.path.join(test_dir, cls)):
            image = cv2.imread(os.path.join(test_dir, cls, img), cv2.IMREAD_GRAYSCALE)
            image = cv2.resize(image, (64, 64))  # Pastikan ukuran gambar sesuai
            X_test.append(image)
            y_test.append(i)
else:
    print(f"Error: The directory '{test_dir}' does not exist.")

X_train_val = np.array(X_train_val)
X_test = np.array(X_test)
y_train_val = np.array(y_train_val)
y_test = np.array(y_test)

X_train_val = X_train_val.reshape(-1, 64, 64, 1)
X_test = X_test.reshape(-1, 64, 64, 1)

print(f'Ada {X_train_val.shape[0]} jumlah sample di training set')
print(f'Ada {X_test.shape[0]} jumlah sample di test set')

"""## Mengambil beberapa sampel dari data training"""

fig, axes = plt.subplots(5,5,figsize=(14,14))
for i in range(25):
    idx = randint(0,X_train_val.shape[0]-1)
    img = X_train_val[idx]
    label = y_train_val[idx]
    axes[i//5][i%5].imshow(img,cmap='gray')
    axes[i//5][i%5].title.set_text(classes[label])

"""# Preprocessing Model

## Memisahkan data training dan validasi
"""

X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, stratify=y_train_val, test_size=0.15)

"""## Membuat generator data untuk augmentasi dan normalisasi


"""

train_datagen = ImageDataGenerator(width_shift_range=0.1, height_shift_range=0.1, rescale=1.0/255)
train_generator = train_datagen.flow(X_train, y_train, shuffle=True)

"""## Normalisasi set validasi dan set uji  

"""

X_val = X_val/255.0
X_test= X_test/255.0

"""# Modelling Data

## Membuat Model CNN
"""

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, InputLayer

model = Sequential([
    InputLayer(input_shape=(64, 64, 1)),
    Conv2D(32, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dense(64, activation='relu'),
    Dense(10, activation='softmax')
])

earlystop = EarlyStopping(patience=8, restore_best_weights=True, min_delta=1e-3)
model.compile(loss='sparse_categorical_crossentropy',optimizer='adam',metrics=['accuracy'])

history = model.fit(train_generator, epochs=30, validation_data=(X_val, y_val))

# Now that 'model' has been trained, you can extract features
# Assume cnn_model is your pre-trained CNN model
# Remove the last layer (softmax layer) to use CNN as a feature extractor
feature_extractor = Model(inputs=model.input, outputs=model.layers[-2].output)

# Extract features using CNN
train_features = feature_extractor.predict(X_train)
test_features = feature_extractor.predict(X_test)

# Reshape features if necessary (e.g., flatten)
train_features = train_features.reshape(train_features.shape[0], -1)
test_features = test_features.reshape(test_features.shape[0], -1)

# Train Decision Tree with extracted features
decision_tree = DecisionTreeClassifier()
decision_tree.fit(train_features, y_train)

# Evaluate Decision Tree
y_pred = decision_tree.predict(test_features)
accuracy = accuracy_score(y_test, y_pred)

print(f"Accuracy: {accuracy * 100:.2f}%")

# Evaluasi model dan plot confusion matrix
y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)

cm = confusion_matrix(y_test, y_pred_classes)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['paper', 'rock', 'scissors'], yticklabels=['paper', 'rock', 'scissors'])
plt.xlabel('Predicted label')
plt.ylabel('True label')
plt.title('Confusion Matrix')
plt.show()

plt.figure(figsize=(12, 4))

# Plot Loss
plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training and Validation Loss')
plt.legend()

# Plot Akurasi
plt.subplot(1, 2, 2)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.title('Training and Validation Accuracy')
plt.legend()

plt.show()

fig, axes = plt.subplots(5,5,figsize=(16,16))
for i in range(25):
    idx = randint(0,X_test.shape[0]-1)
    img = X_test[idx]
    label = classes[np.argmax(model.predict(np.array([img])))]
    axes[i//5][i%5].imshow(img,cmap='gray')
    axes[i//5][i%5].title.set_text(label)

"""## Mencoba memasukkan gambar baru"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import img_to_array

# Fungsi untuk memuat dan memproses gambar baru
def load_and_preprocess_image(image_path):
    # Muat gambar dalam grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Resize gambar ke ukuran yang sesuai (misalnya, 64x64)
    image = cv2.resize(image, (64, 64))

    # Konversi gambar ke array numpy
    image = img_to_array(image)

    # Normalisasi gambar (nilai piksel berada di antara 0 dan 1)
    image = image / 255.0

    # Ubah dimensi gambar agar sesuai dengan input model (1, 64, 64, 1)
    image = np.expand_dims(image, axis=0)

    return image

# Fungsi untuk memprediksi gambar baru dan menampilkan probabilitas untuk setiap kelas
def predict_image(model, image_path, classes):
    # Muat dan preprocess gambar baru
    image = load_and_preprocess_image(image_path)

    # Buat prediksi menggunakan model
    prediction = model.predict(image)[0]

    # Tampilkan gambar
    plt.imshow(cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB))
    plt.title("Predicted Probabilities")
    plt.axis('off')
    plt.show()

    # Tampilkan probabilitas untuk setiap kelas
    for i, cls in enumerate(classes):
        print(f"{cls}: {prediction[i] * 100:.2f}%")

    # Ambil kelas dengan probabilitas tertinggi
    predicted_class = classes[np.argmax(prediction)]

    return predicted_class

# Path ke gambar baru
#image_path = '../content/gdrive/MyDrive/Colab Notebooks/ML/Gambar Baru/Batu/img6.jpg'
image_path = '../content/gdrive/MyDrive/Colab Notebooks/ML/Gambar Baru/Gunting/img7.jpg'
#image_path = '../content/gdrive/MyDrive/Colab Notebooks/ML/Gambar Baru/Kertas/img8.jpg'

# Kelas (label) yang mungkin
classes = ['paper', 'rock', 'scissors']

# Prediksi gambar baru
predicted_class = predict_image(model=model, image_path=image_path, classes=classes)
print(f"Predicted class: {predicted_class}")