from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

import pandas as pd

from app.config import PROJECT_ROOT


DEFAULT_KEYWORDS = [
    "Artificial Intelligence",
    "Machine Learning",
    "Neural Networks",
    "Deep Learning",
    "Large Language Models",
]


def generate_keywords_file(
    destination: str | Path | None = None,
    keywords: Sequence[str] | None = None,
    overwrite: bool = True,
) -> Path:
    output_path = Path(destination) if destination else PROJECT_ROOT / "keywords.xlsx"
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path

    if output_path.exists() and not overwrite:
        raise FileExistsError(f"{output_path} already exists. Use overwrite=True to replace it.")

    rows = list(keywords or DEFAULT_KEYWORDS)
    dataframe = pd.DataFrame({"Keyword": rows})
    dataframe.to_excel(output_path, index=False)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a starter keywords.xlsx file.")
    parser.add_argument(
        "--output",
        default="keywords.xlsx",
        help="Output path for the generated Excel file.",
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Fail if the output file already exists.",
    )
    args = parser.parse_args()

    output_path = generate_keywords_file(
        destination=args.output,
        overwrite=not args.no_overwrite,
    )
    print(f"Generated keyword file at {output_path}")


if __name__ == "__main__":
    main()
