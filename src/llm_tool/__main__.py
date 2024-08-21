from .text import text_llm
from .vision import main
import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python -m llm_tool <path_to_markdown_file>")
        sys.exit(1)
    main(sys.argv[1])