"""
This is a Python wrapper around `config.ini`.
Modify the actual settings in the aforementioned file.
"""

from configparser import ConfigParser
from pathlib import Path


config = ConfigParser()
config.read(Path(__file__).parent / "config.ini")


# Additional post-processing

# Add project root directory
config["DEFAULT"].update({
    "root_directory": str(Path(__file__).parent.parent.absolute())
})

# Get the correct output directory
if bool(config["RESULTS"]["SAVE_RESULTS"]):
    _results_directory = Path(config["RESULTS"]["OUTPUT_DIRECTORY"])
    if _results_directory.is_absolute():
        final_output_directory = Path(_results_directory)
    else:
        final_output_directory = _results_directory.relative_to(config["DEFAULT"]["root_directory"])
        config["RESULTS"].update({
            "OUTPUT_DIRECTORY": str(final_output_directory)
        })
    # Create it
    final_output_directory.mkdir(exist_ok=True, parents=True)
