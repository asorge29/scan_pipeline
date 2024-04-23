from scan_pipeline.app import main
from pathlib import Path

if __name__ == "__main__":
    print('_'*100)
    p = list(Path(__file__).resolve().parent.iterdir())
    print([p for p in p if p.is_file()])