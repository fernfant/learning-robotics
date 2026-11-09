"""For course maintainers: rebuild homework/ from solutions/.

Every block between "# BEGIN SOLUTION" and "# END SOLUTION" becomes a TODO that raises
NotImplementedError. Files without markers (world.py, the optional real-LLM file) are copied as-is.
"""

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC, DST = ROOT / "solutions", ROOT / "homework"

BLOCK = re.compile(r"(?P<indent>[ \t]*)# BEGIN SOLUTION\n.*?[ \t]*# END SOLUTION\n", re.S)


def starter(text, lesson):
    def repl(m):
        ind = m.group("indent")
        return (f"{ind}# TODO: write this part. Read the docstring above carefully.\n"
                f"{ind}raise NotImplementedError(\"Lesson {lesson}: write this function\")\n")
    return BLOCK.sub(repl, text)


def main():
    DST.mkdir(exist_ok=True)
    for f in sorted(SRC.glob("*.py")):
        text = f.read_text()
        m = re.match(r"lesson(\d+)", f.name)
        out = starter(text, int(m.group(1))) if m and "# BEGIN SOLUTION" in text else text
        target = DST / f.name
        if target.exists() and target.read_text() != out:
            print(f"skipped {f.name}: homework/{f.name} has your changes (delete it to reset)")
            continue
        target.write_text(out)
        print(f"wrote homework/{f.name}")


if __name__ == "__main__":
    main()
