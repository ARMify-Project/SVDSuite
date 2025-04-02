#!/bin/bash
# generate_mkdocs_docs.sh
#
# It checks for required packages (mkdocs, mkdocstrings, mkdocs-material) and installs them if needed.
# Then it generates MkDocs documentation for modules in tests/test_process (excluding files with "conftest"),
# creates a minimal mkdocs.yml with a generated navigation, and builds the site.
#
# The final HTML output will be built into the "resolver_tests_doc" folder.
#
# To use this script, ensure you have pip installed.
set -e

# Function to check if a pip package is installed; if not, install it.
function ensure_installed {
    package=$1
    pip show "$package" > /dev/null 2>&1 || pip install "$package"
}

# Ensure required packages are installed.
ensure_installed mkdocs
ensure_installed "mkdocstrings[python]"
ensure_installed mkdocs-material

# Set the current directory as the project root.
BASE_DIR=$(pwd)
export PYTHONPATH=.

# Remove any existing docs, mkdocs.yml, and the build folder.
rm -rf docs mkdocs.yml resolver_tests_doc

# Create a fresh docs folder.
mkdir docs

# Create a homepage (index.md) with the desired heading and text.
cat <<EOF > docs/index.md
# Resolver Test Cases Documentation

This documentation provides a comprehensive set of System View Description (SVD) tests designed to test and validate the logical processing capabilities of SVD parsers. The main focus is on handling complex SVD features such as \`derivedFrom\`, \`dim\`, and other constructs that require parsers to perform logical expansion and complete derivation of data structures. For each test file, an additional *expanded* version is provided, where the logical processing has already been applied.
EOF

# Initialize the navigation variable.
# We use literal newline characters here. We'll later force their interpretation.
NAV="nav:\n  - Home: index.md"

# Find each test file in tests/test_process excluding files containing "conftest".
while IFS= read -r -d '' file; do
    base=$(basename "$file" .py)
    # Compute the full module path (assuming tests is a package and tests/test_process contains __init__.py).
    module="tests.test_process.$base"
    md_file="docs/${base}.md"
    cat <<EOF > "$md_file"
# ${base}

::: ${module}
    options:
      show_source: true
      show_signature: false
EOF
    NAV="${NAV}\n  - ${base}: ${base}.md"
done < <(find tests/test_process -type f -name "test_*.py" ! -name "*conftest*" -print0)

# Create the mkdocs.yml file with a minimal configuration.
# We force the interpretation of newline escapes using echo -e.
cat <<EOF > mkdocs.yml
site_name: Test Documentation
theme:
  name: material
docs_dir: docs
use_directory_urls: false
plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          setup_commands:
            - import sys
            - sys.path.insert(0, ".")
hooks:
  - mkdocs_hook.py
$(echo -e "$NAV")
EOF

# Create a minimal mkdocs_hook.py file to handle the mkdocstrings plugin.
cat <<EOF > mkdocs_hook.py
import os
import re
from bs4 import BeautifulSoup
from pygments import highlight
from pygments.lexers import XmlLexer
from pygments.formatters import HtmlFormatter


class CodeHtmlFormatter(HtmlFormatter):

    def wrap(self, source):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        yield 0, "<pre><code>"
        for i, t in source:
            yield i, t
        yield 0, "</code></pre>"


def on_page_content(html: str, **_) -> str:
    soup = BeautifulSoup(html, "html.parser")
    pattern = re.compile(
        r'(?:get_processed_device_from_testfile\(\s*"([^"]+\.svd)"\s*\)|file_name\s*=\s*"([^"]+\.svd)")'
    )
    formatter = CodeHtmlFormatter(linenos="table", nobackground=True)

    # Find all <details> elements with class "quote"
    for details in soup.find_all("details", class_="quote"):
        text = details.get_text()
        match = pattern.search(text)
        if match:
            # Choose the captured group
            svd_rel_path = match.group(1) if match.group(1) is not None else match.group(2)
            # Compute full SVD file path (assuming SVD files live in "tests/svd")
            full_svd_path = os.path.join("tests/svd", svd_rel_path)
            if os.path.exists(full_svd_path):
                with open(full_svd_path, "r", encoding="utf-8") as f:
                    svd_content = f.read()

                highlighted = highlight(svd_content, XmlLexer(), formatter)

                # Parse the entire highlighted output as HTML.
                highlighted_fragment = BeautifulSoup(highlighted, "html.parser")

                # Create a new <details> element for the SVD file.
                new_details = soup.new_tag("details", **{"class": "quote"})

                # Create summary with "SVD file: " text and the svd_rel_path wrapped in a <code> element.
                summary = soup.new_tag("summary")
                summary.append("SVD file: ")
                code_tag = soup.new_tag("code")
                code_tag.string = svd_rel_path
                summary.append(code_tag)
                new_details.append(summary)

                # Append the entire highlighted_fragment, preserving all inner elements.
                new_details.append(highlighted_fragment)

                # Insert the new details element immediately after the current details element.
                details.insert_after(new_details)
            else:
                print(f"Warning: SVD file not found at {full_svd_path}")

    # Return the modified HTML as a string.
    return str(soup)
EOF

# Build the documentation with mkdocs.
# The output folder is set to resolver_tests_doc (change as desired).
mkdocs build --site-dir resolver_tests_doc

# Remove mkdocs.yml and docs folder.
rm -rf mkdocs.yml mkdocs_hook.py docs

echo "MkDocs documentation generated in the 'resolver_tests_doc' folder."
