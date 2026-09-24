from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile


# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

# Official UCI dataset
DATA_URL = (
    "https://archive.ics.uci.edu/ml/"
    "machine-learning-databases/00501/"
    "PRSA2017_Data_20130301-20170228.zip"
)

ZIP_PATH = RAW_DIR / "airshift_dataset.zip"

EXPECTED_FILES = [
    "PRSA_Data_Aotizhongxin_20130301-20170228.csv",
    "PRSA_Data_Changping_20130301-20170228.csv",
    "PRSA_Data_Dingling_20130301-20170228.csv",
    "PRSA_Data_Dongsi_20130301-20170228.csv",
    "PRSA_Data_Guanyuan_20130301-20170228.csv",
    "PRSA_Data_Gucheng_20130301-20170228.csv",
    "PRSA_Data_Huairou_20130301-20170228.csv",
    "PRSA_Data_Nongzhanguan_20130301-20170228.csv",
    "PRSA_Data_Shunyi_20130301-20170228.csv",
    "PRSA_Data_Tiantan_20130301-20170228.csv",
    "PRSA_Data_Wanliu_20130301-20170228.csv",
    "PRSA_Data_Wanshouxigong_20130301-20170228.csv",
]


def download_dataset():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    existing_files = [
        file.name
        for file in RAW_DIR.glob("*.csv")
    ]

    if all(
        filename in existing_files
        for filename in EXPECTED_FILES
    ):
        print("Dataset already exists in data/raw/.")
        print("No download is required.")
        return

    print("Downloading AirShift dataset...")
    print(f"Source: {DATA_URL}")

    urlretrieve(DATA_URL, ZIP_PATH)

    print("Download completed.")
    print("Extracting dataset...")

    with ZipFile(ZIP_PATH, "r") as zip_file:
        zip_file.extractall(RAW_DIR)

    # Move CSV files from the extracted folder
    extracted_dirs = list(
        RAW_DIR.glob("PRSA_Data_20130301-20170228")
    )

    if extracted_dirs:
        extracted_dir = extracted_dirs[0]

        for csv_file in extracted_dir.glob("*.csv"):
            target = RAW_DIR / csv_file.name
            csv_file.replace(target)

        extracted_dir.rmdir()

    # Remove temporary ZIP file
    ZIP_PATH.unlink()

    missing_files = [
        filename
        for filename in EXPECTED_FILES
        if not (RAW_DIR / filename).exists()
    ]

    if missing_files:
        raise RuntimeError(
            "Dataset download completed, but some files "
            f"are missing: {missing_files}"
        )

    print("Dataset successfully downloaded and extracted.")
    print(f"Location: {RAW_DIR}")
    print(f"Station files found: {len(EXPECTED_FILES)}")


if __name__ == "__main__":
    download_dataset()