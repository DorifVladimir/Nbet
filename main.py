import argparse
import hashlib
import json
import shutil
from pathlib import Path


JSON_FILES = {
    "backup": "BackupFileInfo.json",
    "remote_backup": "RemoteBackupInfo.json",
    "remote_key": "RemoteKeyInfo.json",
}


def sha256_file(path: Path, chunk_size=1024 * 1024):
    h = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()


def read_json(path: Path):
    try:
        with path.open("r", encoding="utf-8-sig") as f:
            return json.load(f)
    except UnicodeDecodeError:
        with path.open("r", encoding="utf-16") as f:
            return json.load(f)


def print_tree(obj, prefix="", depth=0, max_depth=6):
    if depth > max_depth:
        print(prefix + "...")
        return

    if isinstance(obj, dict):
        for key, value in obj.items():
            print(f"{prefix}{key}: {type(value).__name__}")

            if isinstance(value, (dict, list)):
                print_tree(
                    value,
                    prefix + "  ",
                    depth + 1,
                    max_depth
                )

    elif isinstance(obj, list):
        print(f"{prefix}[list: {len(obj)} items]")

        for i, value in enumerate(obj[:10]):
            print(f"{prefix}  [{i}]: {type(value).__name__}")

            if isinstance(value, (dict, list)):
                print_tree(
                    value,
                    prefix + "    ",
                    depth + 1,
                    max_depth
                )


def find_interesting_values(obj, path=""):
    """
    Searches recursively for fields that may be related to
    encryption, keys, hashes, IVs, nonces, algorithms, etc.
    """

    keywords = (
        "key",
        "encrypt",
        "decrypt",
        "cipher",
        "aes",
        "iv",
        "nonce",
        "salt",
        "hash",
        "digest",
        "hmac",
        "mac",
        "algorithm",
        "password",
        "secret",
        "token",
        "verify",
        "signature",
        "checksum",
    )

    results = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key

            if any(k in key.lower() for k in keywords):
                results.append((current_path, value))

            results.extend(
                find_interesting_values(value, current_path)
            )

    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            current_path = f"{path}[{i}]"

            results.extend(
                find_interesting_values(value, current_path)
            )

    return results


def file_signature(path: Path):
    with path.open("rb") as f:
        data = f.read(32)

    return data


def classify_file(path: Path):
    signature = file_signature(path)

    if signature.startswith(b"\xff\xd8\xff"):
        return "JPEG"

    if signature.startswith(b"\x89PNG"):
        return "PNG"

    if signature.startswith(b"GIF8"):
        return "GIF"

    if signature.startswith(b"RIFF"):
        return "RIFF/WEBP/AVI/etc."

    if signature.startswith(b"\x00\x00\x00"):
        return "Possible MP4/ISO-BMFF"

    return "Unknown/encrypted"


def main():
    parser = argparse.ArgumentParser(
        description="Samsung Smart Switch SECUREFOLDER_SELF recovery analyzer"
    )

    parser.add_argument(
        "source",
        nargs="?",
        default=None,
        help="Path to SECUREFOLDER_SELF (defaults to current directory)"
    )

    parser.add_argument(
        "--output",
        default=None,
        help="Output recovery directory"
    )

    args = parser.parse_args()

    if args.source:
        source = Path(args.source).resolve()
    else:
        source = Path.cwd().resolve()
        print("[INFO] No source folder was provided; checking current directory.")

    if not source.exists():
        print(f"[ERROR] Folder does not exist: {source}")
        print("Usage: python main.py <path-to-SECUREFOLDER_SELF>")
        return 1

    if not source.is_dir():
        print(f"[ERROR] Not a directory: {source}")
        print("Usage: python main.py <path-to-SECUREFOLDER_SELF>")
        return 1

    if args.output:
        output = Path(args.output).resolve()
    else:
        output = source.parent / "SECUREFOLDER_RECOVERY"

    output.mkdir(parents=True, exist_ok=True)

    analysis_dir = output / "analysis"
    analysis_dir.mkdir(exist_ok=True)

    print()
    print("=" * 70)
    print(" Samsung Secure Folder Recovery Analyzer")
    print("=" * 70)
    print()

    print(f"Source : {source}")
    print(f"Output : {output}")
    print()

    # ------------------------------------------------------------
    # 1. Check required JSON files
    # ------------------------------------------------------------

    print("[1] Checking Smart Switch metadata...")
    print()

    json_data = {}

    for name, filename in JSON_FILES.items():

        path = source / filename

        if path.exists():

            print(f"[OK] {filename}")
            print(f"     Size: {path.stat().st_size:,} bytes")
            print(f"     SHA256: {sha256_file(path)}")

            try:
                data = read_json(path)
                json_data[name] = data

                print("     JSON: valid")

            except Exception as e:
                print(f"     JSON: ERROR - {e}")

        else:
            print(f"[MISSING] {filename}")

    print()

    # ------------------------------------------------------------
    # 2. Analyze JSON structure
    # ------------------------------------------------------------

    for name, data in json_data.items():

        filename = JSON_FILES[name]

        print("=" * 70)
        print(f" ANALYZING {filename}")
        print("=" * 70)

        structure_file = (
            analysis_dir /
            f"{filename}.structure.txt"
        )

        interesting_file = (
            analysis_dir /
            f"{filename}.interesting.txt"
        )

        with structure_file.open("w", encoding="utf-8") as f:

            original_print = print

            def file_print(*args, **kwargs):
                original_print(*args, **kwargs, file=f)

            file_print(f"FILE: {filename}")
            file_print()

            print_tree(
                data,
                prefix="",
                depth=0,
                max_depth=8
            )

        interesting = find_interesting_values(data)

        with interesting_file.open(
            "w",
            encoding="utf-8"
        ) as f:

            f.write(f"FILE: {filename}\n\n")

            for path, value in interesting:

                f.write(f"{path}\n")
                f.write(f"  VALUE TYPE: {type(value).__name__}\n")
                f.write(f"  VALUE: {repr(value)}\n\n")

        print(f"Structure saved to:")
        print(f"  {structure_file}")

        print(f"Interesting fields saved to:")
        print(f"  {interesting_file}")

        print()

    # ------------------------------------------------------------
    # 3. Analyze encrypted content
    # ------------------------------------------------------------

    print("=" * 70)
    print(" ANALYZING SECURE FOLDER FILES")
    print("=" * 70)
    print()

    files = []

    for path in source.rglob("*"):

        if not path.is_file():
            continue

        if path.name in JSON_FILES.values():
            continue

        files.append(path)

    files.sort()

    print(f"Found {len(files)} content files.")
    print()

    report = output / "files_report.csv"

    with report.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        f.write(
            "filename,size,sha256,classification,first_bytes\n"
        )

        for index, path in enumerate(files, 1):

            size = path.stat().st_size
            sha = sha256_file(path)

            classification = classify_file(path)

            signature = file_signature(path)

            hex_signature = signature.hex()

            print(
                f"[{index}/{len(files)}] "
                f"{path.name} "
                f"{size:,} bytes "
                f"{classification}"
            )

            f.write(
                f'"{path.name}",'
                f"{size},"
                f"{sha},"
                f'"{classification}",'
                f'"{hex_signature}"\n'
            )

    print()
    print(f"File report:")
    print(f"  {report}")

    # ------------------------------------------------------------
    # 4. Make a completely untouched backup copy
    # ------------------------------------------------------------

    backup_copy = output / "ORIGINAL_COPY"

    if not backup_copy.exists():

        print()
        print("[4] Creating untouched backup copy...")

        shutil.copytree(
            source,
            backup_copy
        )

        print(f"[OK] Created:")
        print(f"     {backup_copy}")

    else:

        print()
        print("[4] Original copy already exists.")
        print(f"     {backup_copy}")

    # ------------------------------------------------------------
    # 5. Summary
    # ------------------------------------------------------------

    print()
    print("=" * 70)
    print(" SUMMARY")
    print("=" * 70)

    print()

    for name, filename in JSON_FILES.items():

        path = source / filename

        if path.exists():
            print(f"[OK] {filename}")
        else:
            print(f"[MISSING] {filename}")

    print()
    print(f"Content files: {len(files)}")
    print(f"Analysis directory: {analysis_dir}")
    print(f"File report: {report}")

    print()
    print("=" * 70)
    print(" NEXT STEP")
    print("=" * 70)
    print()
    print(
        "The backup has NOT been modified."
    )
    print(
        "Review the generated *.interesting.txt files."
    )
    print(
        "The actual decryption algorithm must be determined "
        "from the Smart Switch metadata before attempting "
        "to decrypt the content files."
    )
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())