
import json
import sys
from pathlib import Path

REQUIRED_LIBRARIES = {
    "pandas",
    "numpy",
    "scikit-learn",
    "matplotlib",
    "seaborn"
}

CODE_EXTENSIONS = {
    ".py", ".pyi", ".js", ".jsx", ".ts", ".tsx",
    ".mjs", ".cjs", ".java", ".go", ".rs",
    ".cpp", ".c", ".h", ".cs", ".php", ".rb"
}


def block(message):
    print(message, file=sys.stderr)
    sys.exit(2)


try:
    event = json.load(sys.stdin)
except Exception:
    block("Documentation gate: invalid hook input.")

tool_name = event.get("tool_name")
tool_input = event.get("tool_input", {})

# The hook is configured for Write and Edit.
if tool_name not in {"Write", "Edit"}:
    sys.exit(0)

target = tool_input.get("file_path")

if not target:
    block("Documentation gate: target file path is missing.")

# Claude Code supplies an absolute path for Write/Edit.
target_path = Path(target)

if target_path.suffix.lower() not in CODE_EXTENSIONS:
    sys.exit(0)

project_dir = Path(event.get("cwd", "."))

evidence_file = (
    project_dir / "artifacts" / "context7-docs-evidence.json"
)

if not evidence_file.is_file():
    block(
        "SOURCE WRITE BLOCKED: Context7 documentation evidence "
        "is missing. Ask the Documentation Research Agent to "
        "complete its checks first."
    )

try:
    evidence = json.loads(evidence_file.read_text(encoding="utf-8"))
except Exception:
    block("Documentation gate: evidence file is invalid JSON.")

if (
    evidence.get("status") != "verified"
    or evidence.get("provider") != "Context7"
):
    block("Documentation gate: Context7 evidence is not verified.")

libraries = evidence.get("libraries", [])

verified_libraries = {
    item.get("name")
    for item in libraries
    if isinstance(item, dict)
    and item.get("library_id")
    and item.get("version")
    and item.get("topics_checked")
    and item.get("documentation_summary")
}

missing = REQUIRED_LIBRARIES - verified_libraries

if missing:
    block(
        "SOURCE WRITE BLOCKED: Context7 evidence is incomplete. "
        "Missing documentation for: "
        + ", ".join(sorted(missing))
    )

print("Context7 evidence record passed the documentation gate.")
sys.exit(0)
