"""One-command rebuild from deterministic synthetic generation through reporting."""
from src.generate_data import generate
from src.analyze import analyze
if __name__=='__main__':
    generate()
    analyze()
