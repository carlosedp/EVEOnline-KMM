import glob

files = glob.glob("ui_*.py")

__all__ = []

for file in files:
    file = file.replace(".py","")
    __all__.append(file)
