"""
Evaluate accuracy of the model
"""
from pathlib import Path


def main():
    lang_enum = (Path(__file__).parent / "tglang" / "langs_enum_r2.txt").read_text().strip().split("\n")
    lang_enum = [l.strip() for l in lang_enum if bool(l)]

    output_file = Path(__file__).parent.parent / "data" / "output.txt"
    output = output_file.read_text().strip().split("\n")

    correct = 0
    total = 0
    for line in output:
        total += 1
        file, lang_index = line.split(",")
        gt = Path(file).parent.name.strip()
        try:
            if lang_enum.index(gt) == int(lang_index.strip()):
                correct += 1
        except ValueError as e:
            print(f"Error: {e} at {file=!r} and {lang_index=!r}")
            total -= 1

    print(f"Accuracy: {correct / total * 100:.2f}%")


if __name__ == "__main__":
    main()
