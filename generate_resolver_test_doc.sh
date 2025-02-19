#!/bin/bash
# generate_mkdocs_docs.sh
# Run this script from /mnt/data/Temp/ARMify/svdsuite.
# It checks for required packages (mkdocs, mkdocstrings, mkdocs-material) and installs them if needed.
# Then it generates MkDocs documentation for modules in tests/test_process (excluding files with "conftest"),
# creates a minimal mkdocs.yml with a generated navigation, and builds the site.
#
# The final HTML output will be built into the "resolver_test_doc" folder.
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
rm -rf docs mkdocs.yml resolver_test_doc

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
    rendering:
      show_source: false
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
$(echo -e "$NAV")
EOF

# Build the documentation with mkdocs.
# The output folder is set to resolver_test_doc (change as desired).
mkdocs build --site-dir resolver_test_doc

# Remove mkdocs.yml and docs folder.
rm -rf mkdocs.yml docs

echo "MkDocs documentation generated in the 'resolver_test_doc' folder."
