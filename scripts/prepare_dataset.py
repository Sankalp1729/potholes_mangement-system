"""Validate/extract a downloaded YOLOv8 dataset into the project dataset directory.

Example:
    python scripts/prepare_dataset.py --zip "C:/Downloads/Pothole detection.v2i.yolov8.zip"
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEST = ROOT / "datasets" / "pothole_detection_v2"


def find_yaml(root: Path) -> Path:
    candidates = list(root.rglob("data.yaml"))
    if not candidates:
        raise FileNotFoundError("The ZIP does not contain data.yaml.")
    if len(candidates) > 1:
        # Prefer a top-level data.yaml when multiple files are present.
        candidates.sort(key=lambda p: len(p.relative_to(root).parts))
    return candidates[0]


def validate_yaml(data_yaml: Path) -> None:
    import yaml

    config = yaml.safe_load(data_yaml.read_text(encoding="utf-8"))
    expected = ["crocodile crack", "longitudinal crack", "pothole"]
    if config.get("names") != expected:
        raise ValueError(
            f"Unexpected classes {config.get('names')!r}. Expected {expected!r}."
        )
    for key in ("train", "val", "test"):
        if key not in config:
            raise ValueError(f"data.yaml is missing '{key}'.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True, type=Path)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DEST)
    args = parser.parse_args()

    if not args.zip.exists():
        raise FileNotFoundError(args.zip)

    destination = args.destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="pothole_dataset_") as tmp:
        tmp_root = Path(tmp)
        with zipfile.ZipFile(args.zip) as archive:
            bad = [name for name in archive.namelist() if Path(name).is_absolute() or ".." in Path(name).parts]
            if bad:
                raise ValueError("Unsafe path detected in dataset ZIP.")
            archive.extractall(tmp_root)

        yaml_path = find_yaml(tmp_root)
        validate_yaml(yaml_path)
        source_root = yaml_path.parent

        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source_root, destination)

    print(f"Dataset ready: {destination / 'data.yaml'}")
    print("Next: python scripts/train_yolo.py --data datasets/pothole_detection_v2/data.yaml")


if __name__ == "__main__":
    main()
