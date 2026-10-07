"""
Create a BASTA XML input file.

Paper tables:
    1: raw numax
    2: raw numax + good dnu
    3: corrected numax
    4: corrected numax + good dnu

Data subsets:
    a: G + JHK, known evolutionary state
    b: G + JHK, unknown evolutionary state
    c: G only, known evolutionary state
    d: G only, unknown evolutionary state
"""

import os


# Select the run using environment variables.
# Defaults to table 1, subset a.
PAPER_TABLE = os.environ.get("BASTA_TABLE", "1")
DATA_SUBSET = os.environ.get("BASTA_SUBSET", "a")


PAPER_TABLES = {
    "1": {
        "numax_version": "raw",
        "use_dnu": False,
    },
    "2": {
        "numax_version": "raw",
        "use_dnu": True,
    },
    "3": {
        "numax_version": "corrected",
        "use_dnu": False,
    },
    "4": {
        "numax_version": "corrected",
        "use_dnu": True,
    },
}


DATA_SUBSETS = {
    "a": {
        "use_jhk": True,
        "phase_known": True,
    },
    "b": {
        "use_jhk": True,
        "phase_known": False,
    },
    "c": {
        "use_jhk": False,
        "phase_known": True,
    },
    "d": {
        "use_jhk": False,
        "phase_known": False,
    },
}


if PAPER_TABLE not in PAPER_TABLES:
    raise ValueError("PAPER_TABLE must be one of: 1, 2, 3, 4")

if DATA_SUBSET not in DATA_SUBSETS:
    raise ValueError("DATA_SUBSET must be one of: a, b, c, d")


paper = PAPER_TABLES[PAPER_TABLE]
subset = DATA_SUBSETS[DATA_SUBSET]

run_name = f"table{PAPER_TABLE}_{DATA_SUBSET}"


import os

def define_input(define_io, define_fit, define_output,
                 define_plots, define_intpol):

    table = os.environ["BASTA_TABLE"]
    subset = os.environ["BASTA_SUBSET"].lower()

    table_config = {
        "1": ("raw", False),             # numax only
        "2": ("raw_dnu", True),          # numax + dnu
        "3": ("corrected", False),       # corrected numax only
        "4": ("corrected_dnu", True),   # corrected numax + dnu
    }

    stem, use_dnu = table_config[table]

    use_jhk = subset in {"a", "b"}
    phase_known = subset in {"a", "c"}

    xmlfilename = f"input_table{table}_{subset}.xml"

    define_io["gridfile"] = (
        "/Users/z5214708/BASTA/grids/BaSTI_iso2018.hdf5"
    )

    define_io["outputpath"] = f"output/table{table}_{subset}"

    define_io["asciifile"] = f"data/{stem}_{subset}.ascii"

    define_io["missingval"] = -999.999

    define_io["params"] = (
        "starid",
        "numax",
        "numax_err",
        "dnu",
        "dnu_err",
        "Teff",
        "Teff_err",
        "FeH",
        "FeH_err",
        "RA",
        "DEC",
        "G_GAIA",
        "G_GAIA_err",
        "Mj_2MASS",
        "Mj_2MASS_err",
        "Mh_2MASS",
        "Mh_2MASS_err",
        "Mk_2MASS",
        "Mk_2MASS_err",
        "phase",
    )

    fitparams = ["numax", "Teff", "FeH"]

    if use_dnu:
        fitparams.insert(1, "dnuAsf")

    if phase_known:
        fitparams.append("phase")

    define_fit["fitparams"] = tuple(fitparams)

    define_fit["priors"] = {"IMF": "salpeter1955"}
    define_fit["odea"] = (0.2, 1, 0.3, 0)
    define_fit["solarmodel"] = True
    define_fit["dustframe"] = "icrs"

    if use_jhk:
        define_fit["filters"] = (
            "G_GAIA",
            "Mj_2MASS",
            "Mh_2MASS",
            "Mk_2MASS",
        )
    else:
        define_fit["filters"] = ("G_GAIA",)

    outparams = [
        "Teff",
        "FeH",
        "numax",
        "logg",
        "radPhot",
        "massfin",
        "age",
        "distance",
    ]

    if use_dnu:
        outparams.insert(3, "dnuAsf")

    define_output["outparams"] = tuple(outparams)
    define_output["outputfile"] = "results.ascii"
    define_output["optionaloutputs"] = False

    define_plots["cornerplots"] = define_output["outparams"]
    define_plots["kielplots"] = False
    define_plots["freqplots"] = False

    return (
        xmlfilename,
        define_io,
        define_fit,
        define_output,
        define_plots,
        define_intpol,
    )


if __name__ == "__main__":
    from basta.utils_examples import make_basta_input

    make_basta_input(
        define_user_input=define_input,
    )