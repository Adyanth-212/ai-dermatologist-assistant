import os
import json
import tensorflow as tf
from keras.src.legacy.preprocessing.image import ImageDataGenerator
from keras.applications import MobileNetV2
from keras.models import Model
from keras.layers import Dense, GlobalAveragePooling2D, Dropout
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, TensorBoard
from keras import regularizers
import sys
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================
# GPU CONFIGURATION
# ==========================
print("=" * 70)
print("🔍 GPU Detection")
print("=" * 70)

# Check TensorFlow version
print(f"TensorFlow version: {tf.__version__}")

# List all physical devices
gpus = tf.config.list_physical_devices('GPU')
print(f"\n🖥️  GPUs detected: {len(gpus)}")

if gpus:
    for i, gpu in enumerate(gpus):
        print(f"  ✅ GPU {i}: {gpu}")
    
    try:
        # Enable memory growth to prevent TensorFlow from allocating all GPU memory at once
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        
        # Set the visible devices (use all available GPUs)
        tf.config.set_visible_devices(gpus, 'GPU')
        
        # Optional: Set to use only first GPU if you have multiple
        # tf.config.set_visible_devices([gpus[0]], 'GPU')
        
        logical_gpus = tf.config.list_logical_devices('GPU')
        print(f"\n✅ {len(gpus)} Physical GPU(s), {len(logical_gpus)} Logical GPU(s)")
        print("🚀 Training will use GPU acceleration!")
        
    except RuntimeError as e:
        print(f"⚠️  GPU configuration error: {e}")
else:
    print("❌ No GPU detected! Training will use CPU (this will be VERY slow)")
    print("💡 Make sure:")
    print("   - NVIDIA GPU drivers are installed")
    print("   - CUDA toolkit is installed")
    print("   - cuDNN is installed")
    print("   - tensorflow-gpu or tensorflow>=2.0 is installed")

print("=" * 70)
print()

# ==========================
# CONFIGURATION
# ==========================
# Use the preprocessed split dataset instead
DATASET_DIR = "/mnt/c/Users/ashma/ai-dermatologist-assistant/ml/split_dataset"
TRAIN_DIR = os.path.join(DATASET_DIR, "train")
VAL_DIR = os.path.join(DATASET_DIR, "val")
TEST_DIR = os.path.join(DATASET_DIR, "test")
CLASS_WEIGHTS_PATH = "/mnt/c/Users/ashma/ai-dermatologist-assistant/ml/preprocessed_data/class_weights.json"
IMG_SIZE = (224, 224)  # EfficientNetB0 standard size
BATCH_SIZE = 32  # Can use larger batch with B0
EPOCHS_INITIAL = 20
EPOCHS_FINETUNE = 25
LEARNING_RATE = 1e-4  # Good starting point for EfficientNet
SEED = 42

# Validate directories exist
if not os.path.exists(TRAIN_DIR):
    print(f"❌ ERROR: Training directory not found: {TRAIN_DIR}")
    print("💡 Please run the preprocessing script first: ml/image_pre_process.py")
    sys.exit(1)

if not os.path.exists(VAL_DIR):
    print(f"❌ ERROR: Validation directory not found: {VAL_DIR}")
    print("💡 Please run the preprocessing script first: ml/image_pre_process.py")
    sys.exit(1)

# Load class weights
class_weights = None
if os.path.exists(CLASS_WEIGHTS_PATH):
    with open(CLASS_WEIGHTS_PATH, 'r') as f:
        class_weights = json.load(f)
        # Convert string keys to integers
        class_weights = {int(k): v for k, v in class_weights.items()}
    print(f"✅ Loaded class weights from {CLASS_WEIGHTS_PATH}")
    print(f"   Class weights: {class_weights}")
else:
    print(f"⚠️  Class weights file not found at {CLASS_WEIGHTS_PATH}")
    print("   Training will proceed without class balancing")


# ==========================
# DATA AUGMENTATION / GENERATORS
# ==========================
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,        # Increased from 15
    width_shift_range=0.15,   # Increased from 0.1
    height_shift_range=0.15,  # Increased from 0.1
    horizontal_flip=True,
    vertical_flip=True,       # Added - medical images can be flipped
    zoom_range=0.15,          # Added zoom
    brightness_range=[0.7, 1.3],  # Wider range
    shear_range=0.1,          # Added shear transformation
    fill_mode='nearest'
)

# Validation data should only be rescaled, no augmentation
val_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True,
    seed=SEED
)

val_generator = val_datagen.flow_from_directory(
    VAL_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False,
    seed=SEED
)

num_classes = len(train_generator.class_indices)
print("✅ Classes detected:", train_generator.class_indices)
print(f"📊 Training samples: {train_generator.samples}")
print(f"📊 Validation samples: {val_generator.samples}")
print(f"📊 Number of classes: {num_classes}")

# ==========================
# CALLBACKS
# ==========================
callbacks = [
    ModelCheckpoint(
        filepath=os.path.join("models", "best_model.h5"),
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    ),
    EarlyStopping(
        monitor='val_loss',
        patience=10,  # Increased patience for EfficientNet
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-8,
        verbose=1
    ),
    TensorBoard(
        log_dir='logs',
        histogram_freq=1,
        write_graph=True,
        update_freq='epoch'
    )
]

# ==========================
# MODEL DEFINITION
# ==========================
# Load MobileNetV2 backbone (lightweight, efficient, and stable for medical images)
print("\n🏗️  Building MobileNetV2 model...")
base_model = MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3),
    alpha=1.0  # Width multiplier
)
base_model.trainable = False  # freeze base layers initially

# Add custom classification head
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(256, activation='relu', kernel_regularizer=regularizers.l2(0.01))(x)
x = Dropout(0.4)(x)
x = Dense(128, activation='relu', kernel_regularizer=regularizers.l2(0.01))(x)
x = Dropout(0.3)(x)
predictions = Dense(num_classes, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)

# ==========================
# COMPILE MODEL
# ==========================
model.compile(
    optimizer=Adam(learning_rate=LEARNING_RATE),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# ==========================
# TRAIN MODEL
# ==========================
print("\n🚀 Starting initial training (frozen base)...")
history = model.fit(
    train_generator,
    epochs=EPOCHS_INITIAL,
    validation_data=val_generator,
    callbacks=callbacks,
    class_weight=class_weights  # Use class weights for balanced training
)

# ==========================
# FINE-TUNE (optional)
# ==========================
print("\n🔥 Starting fine-tuning (unfreezing top layers)...")
# Unfreeze some of the base model layers for fine-tuning
base_model.trainable = True
# Fine-tune more layers for EfficientNet (unfreeze last 40 blocks)
for layer in base_model.layers[:-40]:
    layer.trainable = False

# Recompile with lower learning rate
model.compile(
    optimizer=Adam(learning_rate=1e-5),  # Lower learning rate for fine-tuning
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Update callbacks for fine-tuning
finetune_callbacks = [
    ModelCheckpoint(
        filepath=os.path.join("models", "finetuned_model.h5"),
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    ),
    EarlyStopping(
        monitor='val_loss',
        patience=12,  # More patience for fine-tuning
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-9,
        verbose=1
    ),
    TensorBoard(
        log_dir='logs/finetune',
        histogram_freq=1,
        write_graph=True,
        update_freq='epoch'
    )
]

# Reset generators to ensure fresh epoch
train_generator.reset()
val_generator.reset()

history_finetune = model.fit(
    train_generator,
    epochs=EPOCHS_FINETUNE,
    validation_data=val_generator,
    callbacks=finetune_callbacks,
    class_weight=class_weights  # Continue using class weights
)

# ==========================
# SAVE MODEL
# ==========================
MODEL_PATH = os.path.join("models", "general_skin_model.h5")
os.makedirs("models", exist_ok=True)
model.save(MODEL_PATH)
print(f"\n✅ Final model saved at {MODEL_PATH}")

# Save training history
import pickle
history_path = os.path.join("models", "training_history.pkl")
with open(history_path, 'wb') as f:
    pickle.dump({
        'initial_training': history.history,
        'fine_tuning': history_finetune.history
    }, f)
print(f"✅ Training history saved at {history_path}")

# ==========================
# EVALUATE ON TEST SET
# ==========================
if os.path.exists(TEST_DIR):
    print("\n" + "="*70)
    print("📊 EVALUATING ON TEST SET")
    print("="*70)
    
    test_datagen = ImageDataGenerator(rescale=1./255)
    test_generator = test_datagen.flow_from_directory(
        TEST_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    
    # Get predictions
    test_loss, test_accuracy = model.evaluate(test_generator)
    print(f"\n✅ Test Loss: {test_loss:.4f}")
    print(f"✅ Test Accuracy: {test_accuracy:.4f}")
    
    # Get detailed predictions for classification report
    test_generator.reset()
    y_pred = model.predict(test_generator, verbose=1)
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_true = test_generator.classes
    
    # Get class names
    class_names = list(test_generator.class_indices.keys())
    
    print("\n📋 Classification Report:")
    print("="*70)
    print(classification_report(y_true, y_pred_classes, target_names=class_names))
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred_classes)
    print("\n🔢 Confusion Matrix:")
    print(cm)
    
    # Per-class accuracy
    print("\n📊 Per-Class Accuracy:")
    print("="*70)
    for i, class_name in enumerate(class_names):
        class_accuracy = cm[i, i] / cm[i].sum() if cm[i].sum() > 0 else 0
        print(f"{class_name}: {class_accuracy:.4f} ({cm[i, i]}/{cm[i].sum()})")
else:
    print(f"\n⚠️  Test directory not found at {TEST_DIR}")
    print("   Skipping test set evaluation")

# Print final metrics
print("\n" + "="*70)
print("📊 TRAINING COMPLETE!")
print("="*70)
print(f"Initial Training - Best Val Accuracy: {max(history.history['val_accuracy']):.4f}")
print(f"Fine-tuning - Best Val Accuracy: {max(history_finetune.history['val_accuracy']):.4f}")
if os.path.exists(TEST_DIR):
    print(f"Test Set Accuracy: {test_accuracy:.4f}")
print("="*70)

# ==========================
# PLOT TRAINING HISTORY
# ==========================
print("\n📈 Generating training visualizations...")
os.makedirs("visualizations", exist_ok=True)

# Set style
plt.style.use('default')
sns.set_palette("husl")

# Combine histories
initial_epochs = len(history.history['accuracy'])
finetune_epochs = len(history_finetune.history['accuracy'])
total_epochs = initial_epochs + finetune_epochs

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('EfficientNetB3 Training History - Skin Disease Classification', fontsize=16, fontweight='bold')

# Plot 1: Training & Validation Accuracy
ax1 = axes[0, 0]
epochs_range = range(1, total_epochs + 1)
train_acc = history.history['accuracy'] + history_finetune.history['accuracy']
val_acc = history.history['val_accuracy'] + history_finetune.history['val_accuracy']

ax1.plot(epochs_range, train_acc, 'b-', label='Training Accuracy', linewidth=2)
ax1.plot(epochs_range, val_acc, 'r-', label='Validation Accuracy', linewidth=2)
ax1.axvline(x=initial_epochs, color='gray', linestyle='--', linewidth=1.5, label='Fine-tuning starts')
ax1.set_xlabel('Epoch', fontsize=12)
ax1.set_ylabel('Accuracy', fontsize=12)
ax1.set_title('Model Accuracy over Time', fontsize=14, fontweight='bold')
ax1.legend(loc='lower right', fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_ylim([0, 1])

# Plot 2: Training & Validation Loss
ax2 = axes[0, 1]
train_loss = history.history['loss'] + history_finetune.history['loss']
val_loss = history.history['val_loss'] + history_finetune.history['val_loss']

ax2.plot(epochs_range, train_loss, 'b-', label='Training Loss', linewidth=2)
ax2.plot(epochs_range, val_loss, 'r-', label='Validation Loss', linewidth=2)
ax2.axvline(x=initial_epochs, color='gray', linestyle='--', linewidth=1.5, label='Fine-tuning starts')
ax2.set_xlabel('Epoch', fontsize=12)
ax2.set_ylabel('Loss', fontsize=12)
ax2.set_title('Model Loss over Time', fontsize=14, fontweight='bold')
ax2.legend(loc='upper right', fontsize=10)
ax2.grid(True, alpha=0.3)

# Plot 3: Accuracy Comparison (Train vs Val)
ax3 = axes[1, 0]
x_pos = np.arange(2)
final_train_acc = train_acc[-1]
final_val_acc = val_acc[-1]
accuracies = [final_train_acc, final_val_acc]
colors = ['#3498db', '#e74c3c']

bars = ax3.bar(x_pos, accuracies, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
ax3.set_ylabel('Accuracy', fontsize=12)
ax3.set_title('Final Accuracy Comparison', fontsize=14, fontweight='bold')
ax3.set_xticks(x_pos)
ax3.set_xticklabels(['Training', 'Validation'], fontsize=11)
ax3.set_ylim([0, 1])
ax3.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for i, (bar, acc) in enumerate(zip(bars, accuracies)):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
             f'{acc:.4f}',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

# Plot 4: Learning Rate Schedule (if available in history)
ax4 = axes[1, 1]
if 'lr' in history.history and 'lr' in history_finetune.history:
    lr_values = history.history['lr'] + history_finetune.history['lr']
    ax4.plot(epochs_range, lr_values, 'g-', linewidth=2)
    ax4.axvline(x=initial_epochs, color='gray', linestyle='--', linewidth=1.5, label='Fine-tuning starts')
    ax4.set_xlabel('Epoch', fontsize=12)
    ax4.set_ylabel('Learning Rate', fontsize=12)
    ax4.set_title('Learning Rate Schedule', fontsize=14, fontweight='bold')
    ax4.set_yscale('log')
    ax4.grid(True, alpha=0.3)
    ax4.legend(fontsize=10)
else:
    # If LR not tracked, show epoch-wise improvement
    epoch_improvement = [val_acc[i] - val_acc[i-1] if i > 0 else 0 for i in range(len(val_acc))]
    ax4.plot(epochs_range, epoch_improvement, 'm-', linewidth=2)
    ax4.axvline(x=initial_epochs, color='gray', linestyle='--', linewidth=1.5, label='Fine-tuning starts')
    ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax4.set_xlabel('Epoch', fontsize=12)
    ax4.set_ylabel('Val Accuracy Improvement', fontsize=12)
    ax4.set_title('Epoch-wise Validation Accuracy Change', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend(fontsize=10)

plt.tight_layout()
plot_path = os.path.join("visualizations", "training_history.png")
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
print(f"✅ Training history plot saved at {plot_path}")
plt.close()

# ==========================
# PLOT CONFUSION MATRIX (if test evaluation was performed)
# ==========================
if os.path.exists(TEST_DIR):
    print("📊 Generating confusion matrix visualization...")
    
    plt.figure(figsize=(14, 12))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names,
                cbar_kws={'label': 'Count'}, linewidths=0.5, linecolor='gray')
    plt.title('Confusion Matrix - Test Set Predictions\nEfficientNetB3 Model', 
              fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('True Label', fontsize=13, fontweight='bold')
    plt.xlabel('Predicted Label', fontsize=13, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(rotation=0, fontsize=9)
    
    cm_path = os.path.join("visualizations", "confusion_matrix.png")
    plt.tight_layout()
    plt.savefig(cm_path, dpi=300, bbox_inches='tight')
    print(f"✅ Confusion matrix saved at {cm_path}")
    plt.close()
    
    # Per-class accuracy bar chart
    plt.figure(figsize=(14, 8))
    per_class_acc = [cm[i, i] / cm[i].sum() if cm[i].sum() > 0 else 0 for i in range(len(class_names))]
    
    colors_gradient = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(class_names)))
    bars = plt.bar(range(len(class_names)), per_class_acc, color=colors_gradient, 
                   edgecolor='black', linewidth=1.2, alpha=0.8)
    
    plt.xlabel('Disease Class', fontsize=13, fontweight='bold')
    plt.ylabel('Accuracy', fontsize=13, fontweight='bold')
    plt.title('Per-Class Test Accuracy - EfficientNetB3 Model', fontsize=16, fontweight='bold', pad=20)
    plt.xticks(range(len(class_names)), class_names, rotation=45, ha='right', fontsize=10)
    plt.ylim([0, 1])
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for i, (bar, acc) in enumerate(zip(bars, per_class_acc)):
        plt.text(bar.get_x() + bar.get_width()/2., acc + 0.02,
                f'{acc:.3f}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Add average line
    avg_acc = np.mean(per_class_acc)
    plt.axhline(y=avg_acc, color='red', linestyle='--', linewidth=2, 
                label=f'Average: {avg_acc:.3f}')
    plt.legend(fontsize=11)
    
    plt.tight_layout()
    acc_path = os.path.join("visualizations", "per_class_accuracy.png")
    plt.savefig(acc_path, dpi=300, bbox_inches='tight')
    print(f"✅ Per-class accuracy plot saved at {acc_path}")
    plt.close()

print("\n🎉 All visualizations generated successfully!")
print("="*70)
