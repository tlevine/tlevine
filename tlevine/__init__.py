__version__ = '0.0.7'
try:
    from tlevine.links import main
except ImportError:
    from links import main
