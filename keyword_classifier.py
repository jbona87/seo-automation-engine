```python
#!/usr/bin/env python3
"""
Module: keyword_intent_pipeline.py

Description:
    Futuristic SEO keyword-intent automation engine that validates,
    classifies and exports keyword datasets to CSV and JSON.

Author: jbona87
Version: 2.0.0
"""

from __future__ import annotations

import csv
import json
import logging
import os
import re
import sys
import time

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


APP_NAME = "SEO INTELLIGENCE AUTOMATION ENGINE"
VERSION = "2.0.0"

OUTPUT_DIRECTORY = Path("output")
CSV_OUTPUT = OUTPUT_DIRECTORY / "classified_keywords.csv"
JSON_OUTPUT = OUTPUT_DIRECTORY / "classified_keywords.json"
LOG_OUTPUT = OUTPUT_DIRECTORY / "logs" / "pipeline.log"


# =============================================================================
# TERMINAL DESIGN SYSTEM
# =============================================================================

class Colour:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    CYAN = "\033[96m"
    PURPLE = "\033[95m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    GREY = "\033[90m"


class TerminalInterface:
    """Dependency-free futuristic terminal interface."""

    def __init__(self, colour_enabled: bool = True) -> None:
        self.colour_enabled = colour_enabled and sys.stdout.isatty()

        # Enable ANSI escape sequences in supported Windows terminals.
        if self.colour_enabled and os.name == "nt":
            os.system("")

    def style(self, text: str, *styles: str) -> str:
        if not self.colour_enabled:
            return text

        return f"{''.join(styles)}{text}{Colour.RESET}"

    def display_banner(self) -> None:
        width = 76

        print()
        print(self.style("╔" + "═" * width + "╗", Colour.CYAN))

        print(
            self.style("║", Colour.CYAN)
            + self.style(
                f"  {APP_NAME:<72}",
                Colour.BOLD,
                Colour.WHITE,
            )
            + self.style("║", Colour.CYAN)
        )

        subtitle = (
            f"  VERSION {VERSION}"
            "  //  KEYWORD SIGNAL PROCESSOR"
            "  //  SYSTEM ONLINE"
        )

        print(
            self.style("║", Colour.CYAN)
            + self.style(f"{subtitle:<76}", Colour.PURPLE)
            + self.style("║", Colour.CYAN)
        )

        print(self.style("╚" + "═" * width + "╝", Colour.CYAN))
        print()

    def display_section(self, number: str, title: str) -> None:
        print(
            self.style(
                f" {number} // {title.upper()} ",
                Colour.BOLD,
                Colour.PURPLE,
            )
        )

        print(self.style("─" * 78, Colour.GREY))

    def display_status(
        self,
        label: str,
        message: str,
        state: str = "info",
    ) -> None:
        states = {
            "info": ("◆", Colour.CYAN),
            "success": ("✓", Colour.GREEN),
            "warning": ("!", Colour.YELLOW),
            "error": ("✕", Colour.RED),
        }

        icon, colour = states.get(state, states["info"])

        print(
            f"{self.style(icon, Colour.BOLD, colour)} "
            f"{self.style(f'[{label}]', Colour.BOLD, colour)} "
            f"{message}"
        )

    def display_progress(
        self,
        current: int,
        total: int,
    ) -> None:
        if total <= 0:
            return

        progress_width = 34
        ratio = current / total
        filled = int(progress_width * ratio)

        progress_bar = (
            "█" * filled
            + "░" * (progress_width - filled)
        )

        print(
            f"\r"
            f"{self.style('[PROCESSING]', Colour.BOLD, Colour.CYAN)} "
            f"{self.style(progress_bar, Colour.PURPLE)} "
            f"{ratio:>6.0%}  "
            f"{current}/{total}",
            end="",
            flush=True,
        )

        if current == total:
            print()

    @staticmethod
    def truncate(value: str, width: int) -> str:
        if len(value) <= width:
            return value

        return value[: width - 1] + "…"

    def display_preview(
        self,
        records: Sequence["KeywordRecord"],
        limit: int = 8,
    ) -> None:
        self.display_section("04", "classified intelligence preview")

        headings = (
            "ID",
            "KEYWORD",
            "INTENT",
            "MATCHED SIGNALS",
        )

        widths = (
            9,
            31,
            32,
            20,
        )

        header = " │ ".join(
            self.style(
                f"{heading:<{width}}",
                Colour.BOLD,
                Colour.CYAN,
            )
            for heading, width in zip(headings, widths)
        )

        print(header)

        print(
            self.style(
                "─┼─".join("─" * width for width in widths),
                Colour.GREY,
            )
        )

        for record in records[:limit]:
            matched_signals = (
                ", ".join(record.matched_signals)
                if record.matched_signals
                else "none"
            )

            values = (
                record.id,
                self.truncate(record.keyword, widths[1]),
                self.truncate(
                    record.intent_classification,
                    widths[2],
                ),
                self.truncate(
                    matched_signals,
                    widths[3],
                ),
            )

            print(
                " │ ".join(
                    f"{value:<{width}}"
                    for value, width in zip(values, widths)
                )
            )

        remaining_records = len(records) - limit

        if remaining_records > 0:
            print(
                self.style(
                    f"\n… {remaining_records} additional records exported",
                    Colour.DIM,
                )
            )

    def display_summary(
        self,
        records: Sequence["KeywordRecord"],
        raw_count: int,
        duplicates_removed: int,
        empty_values_removed: int,
        csv_path: Path,
        json_path: Path,
        elapsed_time: float,
    ) -> None:
        self.display_section("05", "execution summary")

        self.display_status(
            "INPUT",
            f"{raw_count:,} raw keyword payloads received",
        )

        self.display_status(
            "VERIFIED",
            f"{len(records):,} records classified",
            "success",
        )

        if duplicates_removed:
            self.display_status(
                "DEDUP",
                f"{duplicates_removed:,} duplicate records removed",
                "warning",
            )

        if empty_values_removed:
            self.display_status(
                "CLEAN",
                f"{empty_values_removed:,} empty records removed",
                "warning",
            )

        classifications = Counter(
            record.intent_classification
            for record in records
        )

        print()

        for intent, count in classifications.most_common():
            print(
                f"  {self.style('▸', Colour.PURPLE)} "
                f"{intent:<46} "
                f"{self.style(f'{count:>6,}', Colour.BOLD, Colour.WHITE)}"
            )

        print()

        self.display_status(
            "CSV",
            str(csv_path.resolve()),
            "success",
        )

        self.display_status(
            "JSON",
            str(json_path.resolve()),
            "success",
        )

        self.display_status(
            "TIME",
            f"Pipeline completed in {elapsed_time:.3f} seconds",
            "success",
        )

        print()

        print(
            self.style(
                "  RAW SIGNALS IN"
                "  //  STRUCTURED SEARCH INTELLIGENCE OUT",
                Colour.BOLD,
                Colour.CYAN,
            )
        )

        print()


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass(frozen=True)
class IntentRule:
    label: str
    modifiers: tuple[str, ...]
    priority: int


@dataclass(frozen=True)
class KeywordRecord:
    id: str
    keyword: str
    intent_classification: str
    matched_signals: tuple[str, ...]
    processed_at: str
    status: str = "Verified"

    def to_json_record(self) -> dict:
        record = asdict(self)
        record["matched_signals"] = list(self.matched_signals)

        return record

    def to_csv_record(self) -> dict:
        record = self.to_json_record()

        record["matched_signals"] = " | ".join(
            self.matched_signals
        )

        return record


# =============================================================================
# KEYWORD AUTOMATION ENGINE
# =============================================================================

class KeywordAutomationEngine:
    """
    Validate, classify and export SEO keyword datasets.

    Classification rules:
        1. The category with the most matching signals wins.
        2. Priority resolves categories with equal signal counts.
        3. Whole-word matching prevents substring false positives.
    """

    def __init__(
        self,
        terminal: TerminalInterface,
        deduplicate: bool = True,
    ) -> None:
        self.terminal = terminal
        self.deduplicate = deduplicate

        self.intent_rules = (
            IntentRule(
                label="Transactional (High Commercial Value)",
                modifiers=(
                    "buy",
                    "price",
                    "pricing",
                    "cost",
                    "quote",
                    "order",
                    "hire",
                    "shop",
                    "sale",
                    "cheap",
                    "purchase",
                    "provider",
                    "supplier",
                    "agency",
                    "service",
                    "subscription",
                ),
                priority=4,
            ),
            IntentRule(
                label="Commercial Investigation",
                modifiers=(
                    "best",
                    "top",
                    "review",
                    "reviews",
                    "compare",
                    "comparison",
                    "vs",
                    "alternative",
                    "alternatives",
                    "software",
                    "platform",
                    "tool",
                    "tools",
                ),
                priority=3,
            ),
            IntentRule(
                label="Navigational (Brand Focus)",
                modifiers=(
                    "login",
                    "dashboard",
                    "official",
                    "website",
                    "portal",
                    "contact",
                    "support",
                ),
                priority=2,
            ),
            IntentRule(
                label="Informational (Content Opportunity)",
                modifiers=(
                    "how",
                    "what",
                    "why",
                    "guide",
                    "tutorial",
                    "tips",
                    "learn",
                    "examples",
                    "case study",
                    "checklist",
                    "optimization",
                    "strategy",
                    "analytics",
                ),
                priority=1,
            ),
        )

    @staticmethod
    def normalize_keyword(keyword: object) -> str:
        """
        Convert the keyword to text, trim it and collapse
        repeated whitespace.
        """

        return re.sub(
            r"\s+",
            " ",
            str(keyword),
        ).strip()

    @staticmethod
    def contains_signal(
        keyword: str,
        signal: str,
    ) -> bool:
        """
        Match complete words and phrases.

        For example:
            "how to rank" matches "how"
            "show results" does not match "how"
        """

        escaped_signal = re.escape(signal).replace(
            r"\ ",
            r"\s+",
        )

        pattern = rf"(?<!\w){escaped_signal}(?!\w)"

        return (
            re.search(
                pattern,
                keyword,
                flags=re.IGNORECASE,
            )
            is not None
        )

    def classify_intent(
        self,
        keyword: str,
    ) -> tuple[str, tuple[str, ...]]:
        """
        Determine the strongest matching intent and return
        the signals responsible for the classification.
        """

        candidates: list[
            tuple[int, int, str, tuple[str, ...]]
        ] = []

        for rule in self.intent_rules:
            matched_signals = tuple(
                signal
                for signal in rule.modifiers
                if self.contains_signal(keyword, signal)
            )

            if matched_signals:
                candidates.append(
                    (
                        len(matched_signals),
                        rule.priority,
                        rule.label,
                        matched_signals,
                    )
                )

        if not candidates:
            return (
                "Generic Informational (Unclassified)",
                (),
            )

        strongest_candidate = max(
            candidates,
            key=lambda candidate: (
                candidate[0],
                candidate[1],
            ),
        )

        _, _, label, matched_signals = strongest_candidate

        return label, matched_signals

    def prepare_dataset(
        self,
        dataset: Iterable[object],
    ) -> tuple[list[str], int, int, int]:
        """
        Normalize the dataset and optionally remove duplicates.
        """

        raw_items = list(dataset)

        cleaned_keywords: list[str] = []
        seen_keywords: set[str] = set()

        duplicates_removed = 0
        empty_values_removed = 0

        for item in raw_items:
            keyword = self.normalize_keyword(item)

            if not keyword:
                empty_values_removed += 1
                continue

            fingerprint = keyword.casefold()

            if (
                self.deduplicate
                and fingerprint in seen_keywords
            ):
                duplicates_removed += 1
                continue

            seen_keywords.add(fingerprint)
            cleaned_keywords.append(keyword)

        return (
            cleaned_keywords,
            len(raw_items),
            duplicates_removed,
            empty_values_removed,
        )

    @staticmethod
    def export_csv(
        records: Sequence[KeywordRecord],
        output_path: Path,
    ) -> None:
        """
        Write the CSV to a temporary file before replacing
        the final output file.
        """

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path = output_path.with_suffix(
            ".csv.tmp"
        )

        fieldnames = [
            "id",
            "keyword",
            "intent_classification",
            "matched_signals",
            "processed_at",
            "status",
        ]

        with temporary_path.open(
            mode="w",
            newline="",
            encoding="utf-8-sig",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            writer.writerows(
                record.to_csv_record()
                for record in records
            )

        temporary_path.replace(output_path)

    @staticmethod
    def export_json(
        records: Sequence[KeywordRecord],
        output_path: Path,
    ) -> str:
        """
        Generate and safely export the structured JSON payload.
        """

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path = output_path.with_suffix(
            ".json.tmp"
        )

        json_payload = json.dumps(
            [
                record.to_json_record()
                for record in records
            ],
            indent=4,
            ensure_ascii=False,
        )

        temporary_path.write_text(
            json_payload,
            encoding="utf-8",
        )

        temporary_path.replace(output_path)

        return json_payload

    def execute_pipeline(
        self,
        dataset: Iterable[object],
        output_csv: str | Path = CSV_OUTPUT,
        output_json: str | Path = JSON_OUTPUT,
    ) -> str | None:
        """
        Execute validation, classification, preview and export.
        """

        started_at = time.perf_counter()

        csv_path = Path(output_csv)
        json_path = Path(output_json)

        self.terminal.display_banner()

        self.terminal.display_section(
            "01",
            "pipeline initialization",
        )

        self.terminal.display_status(
            "BOOT",
            "Loading search-intent signal matrix",
        )

        self.terminal.display_status(
            "RULES",
            f"{len(self.intent_rules)} intent categories active",
            "success",
        )

        self.terminal.display_status(
            "MODE",
            (
                "Deduplication enabled"
                if self.deduplicate
                else "Duplicate keywords retained"
            ),
        )

        try:
            (
                keywords,
                raw_count,
                duplicates_removed,
                empty_values_removed,
            ) = self.prepare_dataset(dataset)

            if not keywords:
                raise ValueError(
                    "No valid keywords remain after validation."
                )

            self.terminal.display_section(
                "02",
                "keyword classification",
            )

            self.terminal.display_status(
                "DATA",
                f"{raw_count:,} raw payloads detected",
            )

            self.terminal.display_status(
                "QUEUE",
                f"{len(keywords):,} valid keywords queued",
                "success",
            )

            records: list[KeywordRecord] = []

            processed_at = datetime.now(
                timezone.utc
            ).isoformat(timespec="seconds")

            for index, keyword in enumerate(
                keywords,
                start=1,
            ):
                (
                    intent_classification,
                    matched_signals,
                ) = self.classify_intent(keyword)

                records.append(
                    KeywordRecord(
                        id=f"KW-{index:04d}",
                        keyword=keyword,
                        intent_classification=(
                            intent_classification
                        ),
                        matched_signals=matched_signals,
                        processed_at=processed_at,
                    )
                )

                self.terminal.display_progress(
                    index,
                    len(keywords),
                )

            self.terminal.display_section(
                "03",
                "secure export sequence",
            )

            self.terminal.display_status(
                "WRITE",
                "Compiling atomic CSV payload",
            )

            self.export_csv(
                records,
                csv_path,
            )

            self.terminal.display_status(
                "CSV",
                "CSV export verified",
                "success",
            )

            self.terminal.display_status(
                "WRITE",
                "Compiling structured JSON payload",
            )

            json_payload = self.export_json(
                records,
                json_path,
            )

            self.terminal.display_status(
                "JSON",
                "JSON export verified",
                "success",
            )

            elapsed_time = (
                time.perf_counter() - started_at
            )

            self.terminal.display_preview(records)

            self.terminal.display_summary(
                records=records,
                raw_count=raw_count,
                duplicates_removed=duplicates_removed,
                empty_values_removed=empty_values_removed,
                csv_path=csv_path,
                json_path=json_path,
                elapsed_time=elapsed_time,
            )

            logging.info(
                (
                    "Pipeline completed | "
                    "input=%s | "
                    "output=%s | "
                    "duplicates=%s | "
                    "empty=%s"
                ),
                raw_count,
                len(records),
                duplicates_removed,
                empty_values_removed,
            )

            return json_payload

        except (OSError, ValueError, TypeError) as error:
            logging.exception(
                "Pipeline execution failed"
            )

            self.terminal.display_status(
                "PIPELINE ERROR",
                str(error),
                "error",
            )

            return None


# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================

def configure_logging() -> None:
    LOG_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        ),
        handlers=[
            logging.FileHandler(
                LOG_OUTPUT,
                encoding="utf-8",
            )
        ],
        force=True,
    )


def main() -> int:
    """
    Demonstration dataset.

    Replace this list with data loaded from a CSV, API,
    database or another automated extraction process.
    """

    raw_seo_dataset = [
        "how to optimize for ai overviews",
        "best igaming supplier link building cost",
        "python data extraction tutorial",
        "buy programmatic seo automation script",
        "advanced technical seo auditing checklist",
        "offsite supplier link velocity analytics",
    ]

    configure_logging()

    terminal = TerminalInterface(
        colour_enabled=True
    )

    engine = KeywordAutomationEngine(
        terminal=terminal,
        deduplicate=True,
    )

    json_output = engine.execute_pipeline(
        dataset=raw_seo_dataset,
        output_csv=CSV_OUTPUT,
        output_json=JSON_OUTPUT,
    )

    return 0 if json_output is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
```
