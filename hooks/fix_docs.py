#!/usr/bin/env python3
import logging
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

USE_CAPITALIZATION = False

blacklist = [
    "tensor", "albumentations", "boundingbox", "numpy", "iou", "cvat", "abcdatasetInfo", "pytorch", "datasetinfo", "dataloader", ",matplotlib", "samplecontainer", "tba", "annotationdict", "id", "cuda", "few-shot", "false", "true", "callable", "pillow", "genericdataset", "patchcore", "markdown", "dataframe", "mnist"
]
blacklist_folders = ["build"]


def process_file(file_path: str, use_capitalization: bool, string_to_check: str = ":param ") -> None:
    """
    Processes a single file, ensuring the first letter of the first word
    after `:param` and before the colon is properly capitalized or lowercased,
    ensures a colon is present after the parameter name, and preserves
    the leading whitespace for each `:param` line.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.readlines()

            i = 1
            while i < len(content):
                line = content[i].strip()
                prev_line = content[i - 1].strip()
                if line == '"""' and prev_line == "":
                    # Remove the blank line before the closing triple quotes
                    del content[i - 1]
                    i -= 1  # Move index back since we removed a line
                i += 1

        for i, line in enumerate(content):
            stripped_line = line.lstrip()  # Remove leading whitespace for processing
            leading_whitespace = line[:len(line) - len(stripped_line)]  # Capture leading whitespace

            if (i > 1 and stripped_line.startswith(":return") and content[i - 1].lstrip().startswith(":param")):
                content.insert(i, "\n")
                i += 1  # Advance to skip the inserted blank line

            if stripped_line.startswith(string_to_check):
                # Ensure the line contains a colon after the parameter name
                param_line = stripped_line.split(string_to_check, 1)[1]
                if ":" not in param_line:
                    logger.warning(f"Malformed {string_to_check} docstring (missing colon) in file: {file_path}")
                    continue

                # Extract the parameter name and description
                param_name, description = param_line.split(":", 1)
                param_name = param_name.strip()
                description = description.strip()

                # Capitalize or lowercase the first word in the description
                if description:
                    first_word = description.split()[0]
                    if any([first_word.lower().startswith(word.lower()) for word in blacklist]):  # Don´t update these strings
                        continue
                    else:
                        updated_first_word = (first_word[0].upper() + first_word[1:] if use_capitalization else first_word[0].lower() + first_word[1:])
                        updated_description = updated_first_word + description[len(first_word):]
                else:
                    updated_description = description  # Leave it unchanged if empty

                # Reconstruct the line with the preserved leading whitespace
                updated_line = f"{leading_whitespace}{string_to_check}{param_name}: {updated_description}\n"
                content[i] = updated_line

        with open(file_path, "w", encoding="utf-8", newline="") as file:
            file.writelines(content)
        logger.info(f"Processed file: {file_path}")

    except Exception as e:
        logger.exception(f"Error processing file {file_path}: {e}")


def main():
    """
    Main function to process files passed via command-line arguments.
    """
    for filepath in sys.argv[1:]:
        if not filepath.endswith(".py"):
            continue
        process_file(file_path=filepath, use_capitalization=True, string_to_check=":param ")
        process_file(file_path=filepath, use_capitalization=True, string_to_check=":return")

    # Do NOT return non-zero exit code
    sys.exit(0)


if __name__ == "__main__":
    main()
