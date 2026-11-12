#!/usr/bin/env python3
"""Build the public release of the video segmentation dataset v1.

Input is the training-ready COCO instance-segmentation dataset that was used to
train the RF-DETR Seg models reported in deliverable D4.2
(``<src>/{train,valid,test}/_annotations.coco.json`` plus images).

Output is ``release/video_segmentation_dataset_v1/`` with:

- ``train/``, ``valid/``, ``test/``  images and ``_annotations.coco.json`` (copied 1:1)
- ``splits.csv``                    split assignment per image and its grouping keys
- ``metadata.csv``                  per-image metadata
- ``label_taxonomy.csv``            category ids and labels
- ``data_dictionary.csv``           description of all CSV columns and COCO fields
- ``summary.json``                  counts per split, category and source task
- ``anonymization_regions.csv``     image regions blurred to remove personal data
- ``checksums.sha256``              SHA-256 of every file in the release

Personal data visible in the source photos (handwriting, letters, invoices, address
labels) are removed by blurring the regions listed in the anonymization CSV. Only
pixels inside those boxes change; annotations are untouched. All other images are
copied unchanged.

Requires Pillow for the anonymization step.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

SPLITS = ("train", "valid", "test")
HAND_WRITTEN = ("README.md", "DATASET_CARD.md")

# Source CVAT bundle of each annotation task (raw bundles are not published).
TASK_TO_BUNDLE = {
    "01_pet": "WasteR_01_02_03_Backup.zip",
    "02_hdpe": "WasteR_01_02_03_Backup.zip",
    "03_ldpe_hrube": "WasteR_01_02_03_Backup.zip",
    "04_ldpe_farebne": "WasteR_04_05_06_Backup.zip",
    "05_pp_tenke": "WasteR_04_05_06_Backup.zip",
    "06_ps": "WasteR_04_05_06_Backup.zip",
    "07_ost_plast": "WasteR_07_Backup.zip",
    "08_occ_karton": "WasteR_08_Backup.zip",
    "09_paper": "WasteR_09_Backup.zip",
    "10_napojove_kartony": "WasteR_10_Backup.zip",
    "11_primesy": "WasteR_11_Backup.zip",
}

LABEL_DESCRIPTIONS = {
    "PET": ("PET bottles, clear and colored", "PET fľaše, číre a farebné"),
    "HDPE": ("HDPE containers, white and colored", "HDPE obaly, biele a farebné"),
    "LDPE_hrube": ("thick LDPE films", "LDPE hrubé fólie"),
    "LDPE_farebne": ("colored LDPE films", "LDPE farebné fólie"),
    "PP_tenke": ("thin PP films", "PP tenké fólie"),
    "PS": ("polystyrene", "polystyrén"),
    "OST_plast": ("other rigid plastics", "ostatný tvrdený plast"),
    "OCC_karton": ("corrugated cardboard (OCC)", "kartón (OCC)"),
    "paper": ("mixed paper", "zmiešaný papier"),
    "napojove_kartony": ("beverage cartons", "nápojové kartóny"),
    "contaminant": ("admixture / foreign object in a sorted fraction", "prímes / cudzí predmet v triedenej frakcii"),
}

# <task>__<scene>_vid<video>_<frame>.jpg
FILE_RE = re.compile(r"^(?P<task>\d{2}_[a-z_]+?)__(?P<scene>.+?)_vid(?P<vid>\d+)_(?P<frame>\d+)\.(?P<ext>jpg|jpeg|png)$")

EXPECTED_IMAGES = 322
EXPECTED_ANNOTATIONS = 7124

DATA_DICTIONARY = [
    ("splits.csv", "file_name", "string", "Image file name inside the split folder."),
    ("splits.csv", "split", "string", "Split: train, valid or test."),
    ("splits.csv", "task", "string", "Annotation task (material fraction or admixture series), e.g. 01_pet, 11_primesy."),
    ("splits.csv", "scene_group", "string", "Scene or mixture prefix parsed from the source frame name."),
    ("splits.csv", "video_id", "integer", "Source video number within the task and scene group."),
    ("splits.csv", "frame_id", "integer", "Frame number within the source video."),
    ("splits.csv", "group_key", "string", "Grouping key task|scene_group|video_id. All frames of one group are in the same split."),
    ("splits.csv", "source_bundle", "string", "CVAT export bundle the image comes from (raw bundles are not published)."),
    ("metadata.csv", "image_id", "integer", "COCO image id, unique within its split."),
    ("metadata.csv", "file_name", "string", "Image file name inside the split folder."),
    ("metadata.csv", "split", "string", "Split: train, valid or test."),
    ("metadata.csv", "width", "integer", "Image width in pixels."),
    ("metadata.csv", "height", "integer", "Image height in pixels."),
    ("metadata.csv", "task", "string", "Annotation task, see splits.csv."),
    ("metadata.csv", "scene_group", "string", "Scene or mixture prefix, see splits.csv."),
    ("metadata.csv", "video_id", "integer", "Source video number, see splits.csv."),
    ("metadata.csv", "frame_id", "integer", "Frame number within the source video."),
    ("metadata.csv", "source_bundle", "string", "CVAT export bundle the image comes from."),
    ("metadata.csv", "annotation_count", "integer", "Number of polygon instances in the image."),
    ("metadata.csv", "categories", "string", "Labels present in the image, separated by |."),
    ("metadata.csv", "anonymized_regions", "integer", "Number of regions blurred in the image to remove personal data (0 = unchanged)."),
    ("metadata.csv", "sha256", "string", "SHA-256 checksum of the published image file."),
    ("anonymization_regions.csv", "file_name", "string", "Image file name."),
    ("anonymization_regions.csv", "x / y", "integer", "Top-left corner of the blurred box in pixels."),
    ("anonymization_regions.csv", "w / h", "integer", "Width and height of the blurred box in pixels."),
    ("anonymization_regions.csv", "reason", "string", "Type of personal data removed, e.g. handwriting, address_label, invoice_address."),
    ("label_taxonomy.csv", "category_id", "integer", "COCO category id (1-11)."),
    ("label_taxonomy.csv", "label", "string", "Canonical label name used in the COCO files."),
    ("label_taxonomy.csv", "supercategory", "string", "COCO supercategory (always waste)."),
    ("label_taxonomy.csv", "description_en", "string", "Label description in English."),
    ("label_taxonomy.csv", "description_sk", "string", "Label description in Slovak."),
    ("_annotations.coco.json", "images[].id", "integer", "Image id, unique within the split file."),
    ("_annotations.coco.json", "images[].file_name", "string", "Image file name in the same folder."),
    ("_annotations.coco.json", "images[].width / height", "integer", "Image size in pixels."),
    ("_annotations.coco.json", "annotations[].id", "integer", "Annotation id, unique within the split file."),
    ("_annotations.coco.json", "annotations[].image_id", "integer", "Id of the annotated image."),
    ("_annotations.coco.json", "annotations[].category_id", "integer", "Category id, see label_taxonomy.csv."),
    ("_annotations.coco.json", "annotations[].segmentation", "list of float", "Polygon [x1, y1, x2, y2, ...] in pixel coordinates."),
    ("_annotations.coco.json", "annotations[].bbox", "list of float", "Bounding box [x, y, width, height] of the polygon in pixels."),
    ("_annotations.coco.json", "annotations[].area", "float", "Polygon area in square pixels (shoelace formula)."),
    ("_annotations.coco.json", "annotations[].iscrowd", "integer", "Always 0 (individual instances)."),
    ("_annotations.coco.json", "categories[]", "object", "Category list {id, name, supercategory}, identical in all splits."),
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksums(root: Path) -> None:
    lines = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if rel.name == "checksums.sha256":
            continue
        lines.append(f"{sha256_file(path)}  {rel.as_posix()}")
    (root / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def load_regions(path: Path | None) -> dict[str, list[tuple[int, int, int, int]]]:
    regions: dict[str, list[tuple[int, int, int, int]]] = defaultdict(list)
    if path is None:
        return regions
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            regions[row["file_name"]].append((int(row["x"]), int(row["y"]), int(row["w"]), int(row["h"])))
    return regions


def anonymize(src_img: Path, dst_img: Path, boxes: list[tuple[int, int, int, int]]) -> None:
    """Blur the given boxes so that text inside them is unreadable."""
    from PIL import Image, ImageFilter

    with Image.open(src_img) as image:
        image = image.convert("RGB")
        for x, y, w, h in boxes:
            x0, y0 = max(0, x), max(0, y)
            x1, y1 = min(image.width, x + w), min(image.height, y + h)
            if x1 <= x0 or y1 <= y0:
                continue
            region = image.crop((x0, y0, x1, y1))
            # pixelate, then blur: removes fine strokes of handwriting and print
            small = region.resize((max(1, (x1 - x0) // 12), max(1, (y1 - y0) // 12)), Image.BILINEAR)
            region = small.resize(region.size, Image.BILINEAR).filter(ImageFilter.GaussianBlur(6))
            image.paste(region, (x0, y0))
        image.save(dst_img, quality=95)


def parse_file_name(name: str) -> dict:
    m = FILE_RE.match(name)
    if not m:
        raise ValueError(f"Unexpected image file name: {name}")
    task = m.group("task")
    if task not in TASK_TO_BUNDLE:
        raise ValueError(f"Unknown task {task!r} in {name}")
    return {
        "task": task,
        "scene_group": m.group("scene").lower(),
        "video_id": int(m.group("vid")),
        "frame_id": int(m.group("frame")),
        "source_bundle": TASK_TO_BUNDLE[task],
    }


def build(src: Path, out: Path, regions_csv: Path | None = None) -> dict:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    regions = load_regions(regions_csv)
    seen_names: set[str] = set()

    categories = None
    split_rows, meta_rows = [], []
    summary = {
        "dataset": "video_segmentation_dataset_v1",
        "format": "COCO instance segmentation",
        "splits": {},
        "per_category": Counter(),
        "per_task": defaultdict(lambda: {"images": 0, "annotations": 0}),
    }
    group_split: dict[str, str] = {}

    for split in SPLITS:
        coco_path = src / split / "_annotations.coco.json"
        coco = json.loads(coco_path.read_text(encoding="utf-8"))
        cat_names = {c["id"]: c["name"] for c in coco["categories"]}
        if categories is None:
            categories = coco["categories"]
        elif coco["categories"] != categories:
            raise ValueError(f"Category list differs in split {split}")

        (out / split).mkdir()
        shutil.copy2(coco_path, out / split / "_annotations.coco.json")

        anns_by_image = defaultdict(list)
        for ann in coco["annotations"]:
            anns_by_image[ann["image_id"]].append(ann)

        split_cats = Counter()
        for img in sorted(coco["images"], key=lambda i: i["file_name"]):
            name = img["file_name"]
            src_img = src / split / name
            dst_img = out / split / name
            if regions.get(name):
                anonymize(src_img, dst_img, regions[name])
            else:
                shutil.copy2(src_img, dst_img)
            seen_names.add(name)
            info = parse_file_name(name)
            group = f"{info['task']}|{info['scene_group']}|{info['video_id']}"
            if group_split.setdefault(group, split) != split:
                raise ValueError(f"Group {group} appears in {group_split[group]} and {split}")

            anns = anns_by_image[img["id"]]
            labels = sorted({cat_names[a["category_id"]] for a in anns})
            for a in anns:
                split_cats[cat_names[a["category_id"]]] += 1
            summary["per_task"][info["task"]]["images"] += 1
            summary["per_task"][info["task"]]["annotations"] += len(anns)

            split_rows.append([name, split, info["task"], info["scene_group"], info["video_id"],
                               info["frame_id"], group, info["source_bundle"]])
            meta_rows.append([img["id"], name, split, img["width"], img["height"], info["task"],
                              info["scene_group"], info["video_id"], info["frame_id"], info["source_bundle"],
                              len(anns), "|".join(labels), len(regions.get(name, [])), sha256_file(dst_img)])

        summary["splits"][split] = {
            "images": len(coco["images"]),
            "annotations": len(coco["annotations"]),
            "groups": len({r[6] for r in split_rows if r[1] == split}),
            "per_category": dict(sorted(split_cats.items())),
        }
        summary["per_category"].update(split_cats)

    write_csv(out / "splits.csv",
              ["file_name", "split", "task", "scene_group", "video_id", "frame_id", "group_key", "source_bundle"],
              split_rows)
    write_csv(out / "metadata.csv",
              ["image_id", "file_name", "split", "width", "height", "task", "scene_group", "video_id", "frame_id",
               "source_bundle", "annotation_count", "categories", "anonymized_regions", "sha256"],
              meta_rows)
    unknown = sorted(set(regions) - seen_names)
    if unknown:
        raise ValueError(f"Anonymization regions refer to unknown images: {unknown[:5]}")
    if regions_csv is not None:
        with regions_csv.open(newline="", encoding="utf-8") as handle:
            rows = [[r["file_name"], r["x"], r["y"], r["w"], r["h"], r.get("reason", "")]
                    for r in csv.DictReader(handle)]
        write_csv(out / "anonymization_regions.csv", ["file_name", "x", "y", "w", "h", "reason"], sorted(rows))
    summary["anonymized_images"] = len(regions)
    summary["anonymized_regions"] = sum(len(v) for v in regions.values())
    write_csv(out / "label_taxonomy.csv",
              ["category_id", "label", "supercategory", "description_en", "description_sk"],
              [[c["id"], c["name"], c.get("supercategory", "waste"), *LABEL_DESCRIPTIONS.get(c["name"], ("", ""))]
               for c in categories])
    write_csv(out / "data_dictionary.csv", ["file", "field", "type", "description"],
              [list(r) for r in DATA_DICTIONARY])

    total_images = sum(s["images"] for s in summary["splits"].values())
    total_anns = sum(s["annotations"] for s in summary["splits"].values())
    summary["total_images"] = total_images
    summary["total_annotations"] = total_anns
    summary["categories"] = [c["name"] for c in categories]
    summary["per_category"] = dict(sorted(summary["per_category"].items()))
    summary["per_task"] = {k: summary["per_task"][k] for k in sorted(summary["per_task"])}
    summary["source_bundles"] = sorted(set(TASK_TO_BUNDLE.values()))
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Sanity checks against the dataset reported in D4.2.
    names = [r[0] for r in split_rows]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate image file names across splits")
    if total_images != EXPECTED_IMAGES or total_anns != EXPECTED_ANNOTATIONS:
        raise ValueError(f"Expected {EXPECTED_IMAGES} images / {EXPECTED_ANNOTATIONS} annotations, "
                         f"got {total_images} / {total_anns}")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--src", type=Path, required=True,
                        help="training-ready COCO dataset (all_classes_v1) with train/valid/test folders")
    parser.add_argument("--out", type=Path, default=Path("release/video_segmentation_dataset_v1"))
    parser.add_argument("--regions", type=Path,
                        default=Path("docs/datasets/video_segmentation_dataset_v1/anonymization_regions.csv"),
                        help="CSV file_name,x,y,w,h,reason of regions to blur")
    args = parser.parse_args()

    # README.md and DATASET_CARD.md are maintained by hand in the release folder; keep them across rebuilds.
    kept = {doc: (args.out / doc).read_bytes() for doc in HAND_WRITTEN if (args.out / doc).exists()}
    if not args.regions.exists():
        raise SystemExit(f"Anonymization regions file not found: {args.regions} (required, the release must not contain personal data)")
    summary = build(args.src, args.out, args.regions)
    for doc, content in kept.items():
        (args.out / doc).write_bytes(content)
    write_checksums(args.out)
    print(json.dumps({k: summary[k] for k in ("total_images", "total_annotations")}),
          {s: (v["images"], v["annotations"]) for s, v in summary["splits"].items()})


if __name__ == "__main__":
    main()
