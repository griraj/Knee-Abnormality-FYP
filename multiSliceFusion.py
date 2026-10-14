# Generated from: multiSliceFusion.ipynb
# Converted at: 2026-10-13T18:59:48.442Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

from pathlib import Path

root = Path("/kaggle/input")
print("Input exists:", root.exists())

for dataset in sorted(root.iterdir()):
    print(f"\n{dataset.name}/")
    if dataset.is_dir():
        for item in sorted(dataset.iterdir())[:30]:
            if item.is_file():
                print(f"  {item.name} ({item.stat().st_size / 1e6:.1f} MB)")
            else:
                print(f"  {item.name}/")

from pathlib import Path
from collections import Counter

data_root = Path("/kaggle/input/competitions/rsna-knee-abnormality-detection")
print("Competition folder exists:", data_root.exists())

if data_root.exists():
    for item in sorted(data_root.iterdir()):
        if item.is_file():
            print(f"FILE: {item.name} ({item.stat().st_size / 1e6:.1f} MB)")
        elif item.is_dir():
            children = list(item.iterdir())
            extensions = Counter(
                child.suffix.lower() or "<no extension>"
                for child in children if child.is_file()
            )
            print(
                f"FOLDER: {item.name}/ — "
                f"{len(children):,} immediate entries; "
                f"file extensions: {dict(extensions)}"
            )

from pathlib import Path
from collections import Counter
import pandas as pd

root = Path("/kaggle/input/competitions/rsna-knee-abnormality-detection")

# Show CSV columns and basic metadata only—not row contents.
for csv_path in sorted(root.glob("*.csv")):
    frame = pd.read_csv(csv_path, nrows=1000)
    print(f"\n{csv_path.name}: {len(frame):,}+ rows sampled")
    print("Columns:", list(frame.columns))
    print("Dtypes:", {col: str(dtype) for col, dtype in frame.dtypes.items()})

# Show folder structure and file types, but not individual series filenames.
for folder_name in ("test_series", "train_series"):
    folder = root / folder_name
    print(f"\n{folder_name}: exists={folder.exists()}")
    if folder.is_dir():
        entries = list(folder.iterdir())
        print(f"  Immediate entries: {len(entries):,}")
        print("  Entry types:", dict(Counter(
            "folder" if p.is_dir() else (p.suffix.lower() or "no extension")
            for p in entries
        )))
        for subfolder in [p for p in entries if p.is_dir()][:5]:
            subentries = list(subfolder.iterdir())
            print(
                f"  Nested folder: {len(subentries):,} entries; "
                f"types={dict(Counter('folder' if p.is_dir() else (p.suffix.lower() or 'no extension') for p in subentries))}"
            )

from pathlib import Path
from collections import Counter
import os
import pandas as pd

root = Path("/kaggle/input/competitions/rsna-knee-abnormality-detection")
targets = [
    "ACL", "MCL", "Medial Meniscus", "Lateral Meniscus",
    "Medial OA", "Lateral OA", "PF OA", "Effusion",
    "Synovitis", "Baker's", "Contusion", "Fracture",
]

# Full training-label summary; deliberately exclude the report column.
train = pd.read_csv(root / "train.csv", usecols=lambda c: c != "Report")
print("Training studies:", len(train))
print("Duplicate training study IDs:", train["StudyInstanceUID"].duplicated().sum())
print("\nLabels: positive count and missing count")
for col in targets:
    values = pd.to_numeric(train[col], errors="coerce")
    print(f"{col}: positives={int((values == 1).sum())}, missing={int(values.isna().sum())}")

# Series/plane metadata summary.
for split in ("train", "test"):
    series = pd.read_csv(root / f"{split}_series.csv")
    study_count = series["StudyInstanceUID"].nunique()
    print(f"\n{split} series rows: {len(series):,}; studies: {study_count:,}")
    print("Plane counts:", series["Anatomical_Plane"].value_counts(dropna=False).to_dict())
    print("Studies represented in the study list:", len(pd.read_csv(root / f"{split}.csv")))

# Walk the image folders and summarize file layout without showing IDs/filenames.
for split in ("train", "test"):
    folder = root / f"{split}_series"
    extensions = Counter()
    file_depths = Counter()
    safe_examples = []
    total_files = 0

    for current, _, filenames in os.walk(folder):
        for filename in filenames:
            total_files += 1
            suffix = Path(filename).suffix.lower() or "<no extension>"
            extensions[suffix] += 1
            depth = len(Path(current).relative_to(folder).parts) + 1
            file_depths[depth] += 1
            if len(safe_examples) < 3:
                safe_examples.append("/".join(
                    ["<folder>"] * depth + [f"<file>{suffix}"]
                ))

    print(f"\n{split}_series image files: {total_files:,}")
    print("File extensions:", dict(extensions))
    print("File path depths:", dict(sorted(file_depths.items())))
    print("Example path shapes (IDs hidden):", safe_examples)

from pathlib import Path
import pandas as pd

root = Path("/kaggle/input/competitions/rsna-knee-abnormality-detection")
targets = [
    "ACL", "MCL", "Medial Meniscus", "Lateral Meniscus",
    "Medial OA", "Lateral OA", "PF OA", "Effusion",
    "Synovitis", "Baker's", "Contusion", "Fracture",
]

# Count observed labels without showing study IDs or report text.
train = pd.read_csv(root / "train.csv", usecols=lambda c: c != "Report")
observed = train[targets].notna()

print("Studies with at least one observed label:", int(observed.any(axis=1).sum()))
print("Studies with all 12 labels observed:", int(observed.all(axis=1).sum()))
print("Observed values per target:")
for col in targets:
    print(f"  {col}: {int(observed[col].sum())}")

# Show the folder depth and file type for a few image files; hide folder names.
train_dir = root / "train_series"
examples = []
for study_dir in sorted(train_dir.iterdir()):
    if not study_dir.is_dir():
        continue
    for series_dir in sorted(study_dir.iterdir()):
        if not series_dir.is_dir():
            continue
        for image_path in series_dir.rglob("*"):
            if image_path.is_file():
                examples.append(image_path)
                break
        if examples:
            break
    if len(examples) >= 3:
        break

print("\nExample image-file layouts (folder names hidden):")
for path in examples:
    relative = path.relative_to(train_dir)
    print(f"  {len(relative.parts)} path components; extension={path.suffix or '<none>'}")

if examples:
    try:
        import pydicom

        ds = pydicom.dcmread(examples[0], stop_before_pixels=True)
        print("\nFirst image header (safe fields only):")
        for name in (
            "Modality", "Rows", "Columns",
            "PixelSpacing", "SliceThickness", "ImageOrientationPatient",
        ):
            print(f"  {name}: {getattr(ds, name, None)}")
    except ImportError:
        print("\npydicom isn't available in this notebook session yet.")



from pathlib import Path
import pandas as pd

root = Path("/kaggle/input/competitions/rsna-knee-abnormality-detection")
train_dir = root / "train_series"

targets = [
    "ACL", "MCL", "Medial Meniscus", "Lateral Meniscus",
    "Medial OA", "Lateral OA", "PF OA", "Effusion",
    "Synovitis", "Baker's", "Contusion", "Fracture",
]

labels = pd.read_csv(root / "train.csv", usecols=lambda c: c != "Report")
labeled_ids = set(
    labels.loc[labels[targets].notna().all(axis=1), "StudyInstanceUID"]
)

series = pd.read_csv(root / "train_series.csv")
series = series[series["StudyInstanceUID"].isin(labeled_ids)].copy()

# The observed layout is study-folder / series-folder / DICOM-file.
# Match folder names internally; do not print the IDs.
rows = []
missing_series_folders = 0

for study_id in labeled_ids:
    study_folder = train_dir / study_id
    if not study_folder.is_dir():
        continue

    for series_folder in study_folder.iterdir():
        if not series_folder.is_dir():
            continue

        dicom_count = sum(
            1 for path in series_folder.iterdir()
            if path.is_file() and path.suffix.lower() == ".dcm"
        )
        if dicom_count:
            rows.append({
                "StudyInstanceUID": study_id,
                "SeriesInstanceUID": series_folder.name,
                "dicom_slices": dicom_count,
            })

paths = pd.DataFrame(rows)
if paths.empty:
    raise RuntimeError("No DICOM series folders found for the labeled studies.")

series_map = series.merge(
    paths,
    on=["StudyInstanceUID", "SeriesInstanceUID"],
    how="left",
    validate="one_to_one",
)
missing_series_folders = int(series_map["dicom_slices"].isna().sum())

print("Expert-labeled studies:", len(labeled_ids))
print("Series metadata rows for those studies:", len(series_map))
print("Series with matching DICOM folders:", int(series_map["dicom_slices"].notna().sum()))
print("Series missing a DICOM folder:", missing_series_folders)
print("\nSeries counts by plane:")
print(series_map.groupby("Anatomical_Plane").size().to_string())
print("\nDICOM slice-count summary by plane:")
print(series_map.groupby("Anatomical_Plane")["dicom_slices"].describe().round(1).to_string())
print("\nFluid-sensitive series by plane:")
print(
    series_map.groupby("Anatomical_Plane")["Fluid_Sensitive"]
    .agg(["count", "sum"])
    .to_string()
)

from pathlib import Path
import pandas as pd

root = Path("/kaggle/input/competitions/rsna-knee-abnormality-detection")
train_dir = root / "train_series"
targets = [
    "ACL", "MCL", "Medial Meniscus", "Lateral Meniscus",
    "Medial OA", "Lateral OA", "PF OA", "Effusion",
    "Synovitis", "Baker's", "Contusion", "Fracture",
]
planes = ["Sagittal", "Coronal", "Axial"]

# Only use studies with all 12 expert labels; never convert missing labels to 0.
labels = pd.read_csv(root / "train.csv", usecols=lambda col: col != "Report")
labels = labels.loc[labels[targets].notna().all(axis=1)].copy()

series = pd.read_csv(root / "train_series.csv")
series = series[series["StudyInstanceUID"].isin(labels["StudyInstanceUID"])].copy()

# Count DICOM slices in each series folder and verify the folder mapping.
folder_rows = []
for row in series[["StudyInstanceUID", "SeriesInstanceUID"]].itertuples(index=False):
    series_folder = train_dir / row.StudyInstanceUID / row.SeriesInstanceUID
    if not series_folder.is_dir():
        continue
    slice_count = sum(
        1 for path in series_folder.iterdir()
        if path.is_file() and path.suffix.lower() == ".dcm"
    )
    if slice_count:
        folder_rows.append({
            "StudyInstanceUID": row.StudyInstanceUID,
            "SeriesInstanceUID": row.SeriesInstanceUID,
            "dicom_slices": slice_count,
            "series_path": str(series_folder),
        })

folder_index = pd.DataFrame(folder_rows)
series = series.merge(
    folder_index,
    on=["StudyInstanceUID", "SeriesInstanceUID"],
    how="inner",
    validate="one_to_one",
)

# Prefer fluid-sensitive series; within that choice, prefer the most slices.
series["Fluid_Sensitive"] = pd.to_numeric(
    series["Fluid_Sensitive"], errors="coerce"
).fillna(0)
series = series.sort_values(
    ["StudyInstanceUID", "Anatomical_Plane", "Fluid_Sensitive",
     "dicom_slices", "SeriesInstanceUID"],
    ascending=[True, True, False, False, True],
)
selected = series.drop_duplicates(
    ["StudyInstanceUID", "Anatomical_Plane"], keep="first"
)

# Build one row per expert-labeled study, with separate fields for each plane.
manifest = labels[["StudyInstanceUID", *targets]].copy()
for plane in planes:
    plane_rows = selected[selected["Anatomical_Plane"] == plane][
        ["StudyInstanceUID", "SeriesInstanceUID", "series_path",
         "dicom_slices", "Fluid_Sensitive"]
    ].rename(columns={
        "SeriesInstanceUID": f"{plane}_SeriesInstanceUID",
        "series_path": f"{plane}_Path",
        "dicom_slices": f"{plane}_Slices",
        "Fluid_Sensitive": f"{plane}_FluidSensitive",
    })
    manifest = manifest.merge(
        plane_rows, on="StudyInstanceUID", how="left", validate="one_to_one"
    )

manifest_path = Path("/kaggle/working/rsna_labeled_manifest.csv")
manifest.to_csv(manifest_path, index=False)

print("Expert-labeled studies:", len(manifest))
print("Manifest saved:", manifest_path)
for plane in planes:
    print(f"{plane} series available:", int(manifest[f"{plane}_Path"].notna().sum()))

print("\nPositive labels among the 58 expert-labeled studies:")
for target in targets:
    print(f"{target}: {int((manifest[target] == 1).sum())}")

print("\nSlice-count summary for selected series:")
print(manifest[[f"{plane}_Slices" for plane in planes]].describe().round(1))

from pathlib import Path
import numpy as np
import pandas as pd
import pydicom
import matplotlib.pyplot as plt

manifest = pd.read_csv("/kaggle/working/rsna_labeled_manifest.csv")
sample = manifest.iloc[0]

planes = ["Sagittal", "Coronal", "Axial"]
fig, axes = plt.subplots(1, 3, figsize=(12, 4))

for plane, ax in zip(planes, axes):
    series_dir = Path(sample[f"{plane}_Path"])
    dicom_files = list(series_dir.glob("*.dcm"))

    if not dicom_files:
        raise FileNotFoundError(f"No DICOM files found for the {plane} series.")

    # Sort by DICOM InstanceNumber when available.
    ordered = []
    for path in dicom_files:
        ds = pydicom.dcmread(path, stop_before_pixels=True)
        instance_number = getattr(ds, "InstanceNumber", None)
        sort_key = int(instance_number) if instance_number is not None else path.name
        ordered.append((sort_key, path))
    ordered.sort(key=lambda item: item[0])

    # Read only the middle slice's pixels.
    middle_path = ordered[len(ordered) // 2][1]
    ds = pydicom.dcmread(middle_path)
    image = ds.pixel_array.astype(np.float32)

    if getattr(ds, "PhotometricInterpretation", "") == "MONOCHROME1":
        image = image.max() - image

    low, high = np.percentile(image, [1, 99])
    if high <= low:
        raise ValueError(f"The {plane} slice has no usable intensity range.")

    display_image = np.clip((image - low) / (high - low), 0, 1)

    print(
        f"{plane}: slices={len(dicom_files)}, "
        f"shape={image.shape}, dtype={ds.pixel_array.dtype}, "
        f"intensity_min={image.min():.1f}, intensity_max={image.max():.1f}"
    )

    ax.imshow(display_image, cmap="gray")
    ax.set_title(plane)
    ax.axis("off")

plt.tight_layout()
plt.show()

from pathlib import Path
import numpy as np
import pandas as pd
import pydicom
from PIL import Image

root = Path("/kaggle/input/competitions/rsna-knee-abnormality-detection")
manifest = pd.read_csv("/kaggle/working/rsna_labeled_manifest.csv")

targets = [
    "ACL", "MCL", "Medial Meniscus", "Lateral Meniscus",
    "Medial OA", "Lateral OA", "PF OA", "Effusion",
    "Synovitis", "Baker's", "Contusion", "Fracture",
]
planes = ["Sagittal", "Coronal", "Axial"]
image_size = 224

# Verify all included studies have the full set of expert labels.
if manifest[targets].isna().any().any():
    raise ValueError("Manifest contains missing labels; do not replace them with zero.")

images = np.zeros(
    (len(manifest), len(planes), image_size, image_size),
    dtype=np.float32,
)
labels = manifest[targets].to_numpy(dtype=np.float32)

for study_index, row in enumerate(manifest.itertuples(index=False)):
    for plane_index, plane in enumerate(planes):
        series_dir = Path(getattr(row, f"{plane}_Path"))
        dicom_paths = list(series_dir.glob("*.dcm"))
        if not dicom_paths:
            raise FileNotFoundError(f"No DICOM slices found for the {plane} series.")

        # Choose the middle slice by DICOM InstanceNumber.
        slices = []
        for path in dicom_paths:
            header = pydicom.dcmread(path, stop_before_pixels=True)
            instance_number = getattr(header, "InstanceNumber", None)
            if instance_number is None:
                raise ValueError(f"Missing InstanceNumber in a {plane} series slice.")
            slices.append((int(instance_number), path))

        slices.sort(key=lambda entry: entry[0])
        middle_path = slices[len(slices) // 2][1]
        ds = pydicom.dcmread(middle_path)

        pixels = ds.pixel_array.astype(np.float32)
        pixels = pixels * float(getattr(ds, "RescaleSlope", 1.0))
        pixels += float(getattr(ds, "RescaleIntercept", 0.0))

        if getattr(ds, "PhotometricInterpretation", "") == "MONOCHROME1":
            pixels = pixels.max() - pixels

        low, high = np.percentile(pixels, [1, 99])
        if not np.isfinite(low) or not np.isfinite(high) or high <= low:
            raise ValueError(f"Invalid intensity range for the {plane} slice.")

        normalized = np.clip((pixels - low) / (high - low), 0, 1)
        resized = Image.fromarray((normalized * 255).astype(np.uint8)).resize(
            (image_size, image_size),
            resample=Image.Resampling.BILINEAR,
        )
        images[study_index, plane_index] = np.asarray(resized, dtype=np.float32) / 255.0

    if (study_index + 1) % 10 == 0 or study_index + 1 == len(manifest):
        print(f"Processed studies: {study_index + 1}/{len(manifest)}")

cache_path = Path("/kaggle/working/rsna_expert_pilot_224.npz")
np.savez_compressed(cache_path, images=images, labels=labels)

# Verify the saved cache and its numeric ranges.
with np.load(cache_path) as cache:
    saved_images = cache["images"]
    saved_labels = cache["labels"]
    print("\nCache:", cache_path)
    print("Images shape:", saved_images.shape)
    print("Labels shape:", saved_labels.shape)
    print("Image range:", float(saved_images.min()), "to", float(saved_images.max()))
    print("All image values finite:", bool(np.isfinite(saved_images).all()))
    print("All labels finite:", bool(np.isfinite(saved_labels).all()))

import numpy as np
import pandas as pd
from pathlib import Path

manifest = pd.read_csv("/kaggle/working/rsna_labeled_manifest.csv")
targets = [
    "ACL", "MCL", "Medial Meniscus", "Lateral Meniscus",
    "Medial OA", "Lateral OA", "PF OA", "Effusion",
    "Synovitis", "Baker's", "Contusion", "Fracture",
]

if manifest[targets].isna().any().any():
    raise ValueError("Missing labels found; do not replace them with zero.")

y = manifest[targets].to_numpy(dtype=np.int8)
n_studies = len(y)
n_val = int(round(n_studies * 0.2))
rng = np.random.default_rng(42)

# Search for a deterministic split where both sets contain positives and
# negatives for every target, preferring validation counts near 20% of each.
best = None
best_score = float("inf")

for _ in range(20_000):
    val_idx = rng.choice(n_studies, size=n_val, replace=False)
    train_mask = np.ones(n_studies, dtype=bool)
    train_mask[val_idx] = False

    train_pos = y[train_mask].sum(axis=0)
    val_pos = y[val_idx].sum(axis=0)

    if np.any(train_pos == 0) or np.any(train_pos == train_mask.sum()):
        continue
    if np.any(val_pos == 0) or np.any(val_pos == n_val):
        continue

    expected_val_pos = y.sum(axis=0) * (n_val / n_studies)
    score = float(np.abs(val_pos - expected_val_pos).sum())

    if score < best_score:
        best = (train_mask, val_idx)
        best_score = score

if best is None:
    raise RuntimeError(
        "Could not find a split with both classes for every label in both sets. "
        "Use grouped cross-validation or revise the validation strategy."
    )

train_mask, val_idx = best
split = np.full(n_studies, "train", dtype=object)
split[val_idx] = "validation"

split_path = Path("/kaggle/working/rsna_expert_split.csv")
pd.DataFrame({
    "StudyInstanceUID": manifest["StudyInstanceUID"],
    "split": split,
}).to_csv(split_path, index=False)

print(f"Train studies: {int(train_mask.sum())}")
print(f"Validation studies: {len(val_idx)}")
print(f"Split saved: {split_path}")
print("\nPositive / negative counts by split:")
for i, target in enumerate(targets):
    train_pos = int(y[train_mask, i].sum())
    val_pos = int(y[val_idx, i].sum())
    print(
        f"{target}: train {train_pos}/{int(train_mask.sum()) - train_pos} "
        f"positive/negative; validation {val_pos}/{len(val_idx) - val_pos}"
    )

import random
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import average_precision_score, roc_auc_score

# Reproducibility for this pilot run.
seed = 42
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(seed)

targets = [
    "ACL", "MCL", "Medial Meniscus", "Lateral Meniscus",
    "Medial OA", "Lateral OA", "PF OA", "Effusion",
    "Synovitis", "Baker's", "Contusion", "Fracture",
]

manifest = pd.read_csv("/kaggle/working/rsna_labeled_manifest.csv")
split_df = pd.read_csv("/kaggle/working/rsna_expert_split.csv")

with np.load("/kaggle/working/rsna_expert_pilot_224.npz") as cache:
    images = cache["images"].astype(np.float32)
    labels = cache["labels"].astype(np.float32)

# Ensure cached images, labels, manifest, and split use the same study order.
if len(manifest) != len(images) or len(manifest) != len(labels):
    raise ValueError("Cache and manifest row counts do not match.")
if not np.array_equal(
    manifest["StudyInstanceUID"].to_numpy(),
    split_df["StudyInstanceUID"].to_numpy(),
):
    raise ValueError("Manifest and split study order differs; align by study ID first.")
if labels.shape[1] != len(targets) or not np.isfinite(labels).all():
    raise ValueError("Labels have an unexpected shape or contain non-finite values.")

train_mask = split_df["split"].eq("train").to_numpy()
val_mask = split_df["split"].eq("validation").to_numpy()
if train_mask.sum() == 0 or val_mask.sum() == 0:
    raise ValueError("The train/validation split is empty.")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Device:", device)
print("Train studies:", int(train_mask.sum()))
print("Validation studies:", int(val_mask.sum()))

x_train = torch.from_numpy(images[train_mask])
y_train = torch.from_numpy(labels[train_mask])
x_val = torch.from_numpy(images[val_mask]).to(device)
y_val = torch.from_numpy(labels[val_mask]).to(device)

# Class weighting uses training labels only; cap weights to limit instability
# from the very small number of expert-labeled studies.
positive = y_train.sum(dim=0)
negative = len(y_train) - positive
if torch.any(positive == 0) or torch.any(negative == 0):
    raise ValueError("A training label has only one class; cannot train this baseline.")
pos_weight = (negative / positive).clamp(min=1.0, max=5.0).to(device)

train_loader = DataLoader(
    TensorDataset(x_train, y_train),
    batch_size=8,
    shuffle=True,
    generator=torch.Generator().manual_seed(seed),
)

class SmallMultiPlaneCNN(nn.Module):
    def __init__(self, number_of_labels: int):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1, bias=False),
            nn.GroupNorm(4, 16),
            nn.SiLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(16, 32, kernel_size=3, padding=1, bias=False),
            nn.GroupNorm(4, 32),
            nn.SiLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, kernel_size=3, padding=1, bias=False),
            nn.GroupNorm(8, 64),
            nn.SiLU(),
            nn.MaxPool2d(2),

            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Dropout(0.3),
            nn.Linear(64, number_of_labels),
        )

    def forward(self, x):
        return self.features(x)

model = SmallMultiPlaneCNN(len(targets)).to(device)
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)

best_val_loss = float("inf")
best_state = None
patience = 4
epochs_without_improvement = 0
max_epochs = 15

for epoch in range(1, max_epochs + 1):
    model.train()
    train_loss_sum = 0.0
    train_count = 0

    for batch_x, batch_y in train_loader:
        batch_x = batch_x.to(device)
        batch_y = batch_y.to(device)

        optimizer.zero_grad(set_to_none=True)
        logits = model(batch_x)
        loss = criterion(logits, batch_y)
        loss.backward()
        optimizer.step()

        train_loss_sum += loss.item() * len(batch_x)
        train_count += len(batch_x)

    model.eval()
    with torch.no_grad():
        val_logits = model(x_val)
        val_loss = criterion(val_logits, y_val).item()

    train_loss = train_loss_sum / train_count
    print(
        f"Epoch {epoch:02d}: "
        f"train_loss={train_loss:.4f}, val_loss={val_loss:.4f}"
    )

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        best_state = {
            key: value.detach().cpu().clone()
            for key, value in model.state_dict().items()
        }
        epochs_without_improvement = 0
    else:
        epochs_without_improvement += 1
        if epochs_without_improvement >= patience:
            print("Early stopping: validation loss did not improve.")
            break

if best_state is None:
    raise RuntimeError("Training did not produce a valid model checkpoint.")

model.load_state_dict(best_state)
model.eval()
with torch.no_grad():
    probabilities = torch.sigmoid(model(x_val)).cpu().numpy()

results = []
for index, target in enumerate(targets):
    truth = labels[val_mask, index]
    results.append({
        "label": target,
        "positive_validation_cases": int(truth.sum()),
        "roc_auc": roc_auc_score(truth, probabilities[:, index]),
        "average_precision": average_precision_score(truth, probabilities[:, index]),
    })

results_df = pd.DataFrame(results)
print("\nPreliminary validation metrics:")
print(results_df.to_string(index=False, float_format=lambda value: f"{value:.3f}"))
print(
    "\nMacro ROC AUC:",
    f"{results_df['roc_auc'].mean():.3f}",
    "| Macro average precision:",
    f"{results_df['average_precision'].mean():.3f}",
)

checkpoint_path = Path("/kaggle/working/rsna_pilot_cnn.pt")
torch.save(model.state_dict(), checkpoint_path)
print("\nPilot checkpoint saved:", checkpoint_path)
print("Reminder: these 12-study validation metrics are highly uncertain.")

from pathlib import Path

import numpy as np
import pandas as pd
import pydicom
from PIL import Image

root = Path("/kaggle/input/competitions/rsna-knee-abnormality-detection")
train_dir = root / "train_series"

targets = [
    "ACL", "MCL", "Medial Meniscus", "Lateral Meniscus",
    "Medial OA", "Lateral OA", "PF OA", "Effusion",
    "Synovitis", "Baker's", "Contusion", "Fracture",
]
planes = ["Sagittal", "Coronal", "Axial"]
slices_per_plane = 8
image_size = 224

# Rebuild labels and manifest from persistent competition inputs.
labels = pd.read_csv(root / "train.csv", usecols=lambda col: col != "Report")
labels = labels.loc[labels[targets].notna().all(axis=1)].copy()
if labels.empty:
    raise ValueError("No fully labeled expert studies found in train.csv.")

series = pd.read_csv(root / "train_series.csv")
series = series[series["StudyInstanceUID"].isin(labels["StudyInstanceUID"])].copy()

folder_rows = []
for _, row in series.iterrows():
    series_dir = train_dir / str(row["StudyInstanceUID"]) / str(row["SeriesInstanceUID"])
    if not series_dir.is_dir():
        continue

    dicom_count = sum(
        1 for path in series_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".dcm"
    )
    if dicom_count:
        folder_rows.append({
            "StudyInstanceUID": row["StudyInstanceUID"],
            "SeriesInstanceUID": row["SeriesInstanceUID"],
            "series_path": str(series_dir),
            "dicom_slices": dicom_count,
        })

folder_index = pd.DataFrame(folder_rows)
if folder_index.empty:
    raise FileNotFoundError("No DICOM series folders matched train_series.csv.")

series = series.merge(
    folder_index,
    on=["StudyInstanceUID", "SeriesInstanceUID"],
    how="inner",
    validate="one_to_one",
)

# Prefer fluid-sensitive series, then the series with the most slices.
series["Fluid_Sensitive"] = pd.to_numeric(
    series["Fluid_Sensitive"], errors="coerce"
).fillna(0)

manifest = labels[["StudyInstanceUID", *targets]].copy()
for plane in planes:
    candidates = series[series["Anatomical_Plane"] == plane].copy()
    candidates = candidates.sort_values(
        ["StudyInstanceUID", "Fluid_Sensitive", "dicom_slices", "SeriesInstanceUID"],
        ascending=[True, False, False, True],
    ).drop_duplicates("StudyInstanceUID")

    plane_rows = candidates[
        ["StudyInstanceUID", "series_path", "dicom_slices"]
    ].rename(columns={
        "series_path": f"{plane}_Path",
        "dicom_slices": f"{plane}_Slices",
    })

    manifest = manifest.merge(
        plane_rows,
        on="StudyInstanceUID",
        how="left",
        validate="one_to_one",
    )

    missing = int(manifest[f"{plane}_Path"].isna().sum())
    print(f"{plane} series available: {len(manifest) - missing}/{len(manifest)}")
    if missing:
        raise ValueError(f"{missing} labeled studies are missing a {plane} series.")

if manifest[targets].isna().any().any():
    raise ValueError("Missing labels found; refusing to treat them as negatives.")

# Cache eight evenly spaced slices per plane for every labeled study.
images = np.zeros(
    (len(manifest), len(planes), slices_per_plane, image_size, image_size),
    dtype=np.uint8,
)
y = manifest[targets].to_numpy(dtype=np.float32)

for study_index, (_, row) in enumerate(manifest.iterrows()):
    for plane_index, plane in enumerate(planes):
        series_dir = Path(row[f"{plane}_Path"])
        dicom_paths = list(series_dir.glob("*.dcm"))
        if not dicom_paths:
            raise FileNotFoundError(f"No DICOM slices found for {plane}.")

        ordered = []
        for path in dicom_paths:
            header = pydicom.dcmread(path, stop_before_pixels=True)
            instance = getattr(header, "InstanceNumber", None)
            if instance is None:
                raise ValueError(f"Missing InstanceNumber in {plane} series.")
            ordered.append((int(instance), path))

        ordered.sort(key=lambda item: (item[0], item[1].name))
        sample_indices = np.linspace(
            0, len(ordered) - 1, slices_per_plane
        ).round().astype(int)

        for slice_index, selected_index in enumerate(sample_indices):
            ds = pydicom.dcmread(ordered[selected_index][1])
            pixels = ds.pixel_array.astype(np.float32)
            pixels = pixels * float(getattr(ds, "RescaleSlope", 1.0))
            pixels += float(getattr(ds, "RescaleIntercept", 0.0))

            if getattr(ds, "PhotometricInterpretation", "") == "MONOCHROME1":
                pixels = pixels.max() - pixels

            low, high = np.percentile(pixels, [1, 99])
            if not np.isfinite(low) or not np.isfinite(high) or high <= low:
                raise ValueError(f"Invalid intensity range in {plane} slice.")

            pixels = np.clip((pixels - low) / (high - low), 0, 1)
            resized = Image.fromarray((pixels * 255).astype(np.uint8)).resize(
                (image_size, image_size),
                resample=Image.Resampling.BILINEAR,
            )
            images[study_index, plane_index, slice_index] = np.asarray(resized)

    if (study_index + 1) % 10 == 0 or study_index + 1 == len(manifest):
        print(f"Processed studies: {study_index + 1}/{len(manifest)}")

# Keep the manifest available for later cells in this same session.
manifest.to_csv("/kaggle/working/rsna_labeled_manifest.csv", index=False)

cache_path = Path("/kaggle/working/rsna_expert_multislice_224.npz")
np.savez_compressed(cache_path, images=images, labels=y)

with np.load(cache_path) as cache:
    print("\nCache:", cache_path)
    print("Images:", cache["images"].shape, cache["images"].dtype)
    print("Labels:", cache["labels"].shape, cache["labels"].dtype)
    print("Image range:", int(cache["images"].min()), "to", int(cache["images"].max()))
    print("All labels finite:", bool(np.isfinite(cache["labels"]).all()))

import random
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.metrics import average_precision_score, roc_auc_score
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

seed = 42
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(seed)

targets = [
    "ACL", "MCL", "Medial Meniscus", "Lateral Meniscus",
    "Medial OA", "Lateral OA", "PF OA", "Effusion",
    "Synovitis", "Baker's", "Contusion", "Fracture",
]

manifest = pd.read_csv("/kaggle/working/rsna_labeled_manifest.csv")
with np.load("/kaggle/working/rsna_expert_multislice_224.npz") as cache:
    images = cache["images"]
    labels = cache["labels"]

if images.shape != (len(manifest), 3, 8, 224, 224):
    raise ValueError(f"Unexpected image-cache shape: {images.shape}")
if labels.shape != (len(manifest), len(targets)):
    raise ValueError(f"Unexpected label-cache shape: {labels.shape}")
if not np.isfinite(labels).all():
    raise ValueError("Labels contain missing or non-finite values.")

# Find a repeatable study-level split with positive and negative examples
# for every label in both partitions.
n_studies = len(labels)
n_val = round(n_studies * 0.2)
rng = np.random.default_rng(seed)
best_split = None
best_score = float("inf")

for _ in range(20_000):
    val_idx = rng.choice(n_studies, size=n_val, replace=False)
    train_mask = np.ones(n_studies, dtype=bool)
    train_mask[val_idx] = False
    y = labels.astype(np.int8)

    train_pos = y[train_mask].sum(axis=0)
    val_pos = y[val_idx].sum(axis=0)
    if np.any(train_pos == 0) or np.any(train_pos == train_mask.sum()):
        continue
    if np.any(val_pos == 0) or np.any(val_pos == n_val):
        continue

    expected = y.sum(axis=0) * (n_val / n_studies)
    score = float(np.abs(val_pos - expected).sum())
    if score < best_score:
        best_split = (train_mask, val_idx)
        best_score = score

if best_split is None:
    raise RuntimeError("Could not create a valid train/validation split.")

train_mask, val_idx = best_split
split_names = np.full(n_studies, "train", dtype=object)
split_names[val_idx] = "validation"
pd.DataFrame({
    "StudyInstanceUID": manifest["StudyInstanceUID"],
    "split": split_names,
}).to_csv("/kaggle/working/rsna_expert_split.csv", index=False)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Device:", device)
print(f"Train studies: {int(train_mask.sum())}; validation studies: {len(val_idx)}")

x_train = torch.from_numpy(images[train_mask])  # uint8 to reduce memory
y_train = torch.from_numpy(labels[train_mask].astype(np.float32))
x_val = torch.from_numpy(images[val_idx]).to(device)
y_val = torch.from_numpy(labels[val_idx].astype(np.float32)).to(device)

positive = y_train.sum(dim=0)
negative = len(y_train) - positive
if torch.any(positive == 0) or torch.any(negative == 0):
    raise ValueError("A training label has only one class.")
pos_weight = (negative / positive).clamp(1.0, 5.0).to(device)

class MultiPlaneFusionCNN(nn.Module):
    def __init__(self, number_of_labels):
        super().__init__()
        self.slice_encoder = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, stride=2, padding=1, bias=False),
            nn.GroupNorm(4, 16),
            nn.SiLU(),
            nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1, bias=False),
            nn.GroupNorm(4, 32),
            nn.SiLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1, bias=False),
            nn.GroupNorm(8, 64),
            nn.SiLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        )
        self.fusion_head = nn.Sequential(
            nn.Linear(3 * 64, 128),
            nn.SiLU(),
            nn.Dropout(0.3),
            nn.Linear(128, number_of_labels),
        )

    def forward(self, x):
        batch, planes, slices, height, width = x.shape
        x = x.reshape(batch * planes * slices, 1, height, width)
        x = x.float().div(255.0)
        x = F.interpolate(
            x, size=(160, 160), mode="bilinear", align_corners=False
        )
        features = self.slice_encoder(x)
        features = features.reshape(batch, planes, slices, 64)
        plane_features = features.mean(dim=2)
        fused = plane_features.reshape(batch, planes * 64)
        return self.fusion_head(fused)

loader = DataLoader(
    TensorDataset(x_train, y_train),
    batch_size=4,
    shuffle=True,
    generator=torch.Generator().manual_seed(seed),
)
model = MultiPlaneFusionCNN(len(targets)).to(device)
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)

best_val_loss = float("inf")
best_state = None
wait = 0

for epoch in range(1, 13):
    model.train()
    total_loss = 0.0

    for batch_x, batch_y in loader:
        batch_x = batch_x.to(device)
        batch_y = batch_y.to(device)

        optimizer.zero_grad(set_to_none=True)
        loss = criterion(model(batch_x), batch_y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(batch_x)

    model.eval()
    with torch.no_grad():
        val_loss = criterion(model(x_val), y_val).item()

    print(
        f"Epoch {epoch:02d}: "
        f"train_loss={total_loss / len(x_train):.4f}, "
        f"val_loss={val_loss:.4f}"
    )

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        best_state = {
            key: value.detach().cpu().clone()
            for key, value in model.state_dict().items()
        }
        wait = 0
    else:
        wait += 1
        if wait >= 3:
            print("Early stopping.")
            break

if best_state is None:
    raise RuntimeError("Training did not produce a model checkpoint.")

model.load_state_dict(best_state)
model.eval()
with torch.no_grad():
    probabilities = torch.sigmoid(model(x_val)).cpu().numpy()

metrics = []
for index, target in enumerate(targets):
    truth = labels[val_idx, index]
    metrics.append({
        "label": target,
        "validation_positives": int(truth.sum()),
        "roc_auc": roc_auc_score(truth, probabilities[:, index]),
        "average_precision": average_precision_score(truth, probabilities[:, index]),
    })

metrics_df = pd.DataFrame(metrics)
print("\nPreliminary validation metrics:")
print(metrics_df.to_string(index=False, float_format=lambda value: f"{value:.3f}"))
print(f"\nMacro ROC AUC: {metrics_df['roc_auc'].mean():.3f}")

torch.save(model.state_dict(), "/kaggle/working/rsna_multiplane_fusion_pilot.pt")
metrics_df.to_csv("/kaggle/working/rsna_multiplane_pilot_metrics.csv", index=False)
print("Saved pilot checkpoint and metrics under /kaggle/working.")
print("These 12-study validation results are highly uncertain.")