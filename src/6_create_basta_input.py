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


def define_input(
    define_io,
    define_fit,
    define_output,
    define_plots,
    define_intpol,
):
    """
    Define the BASTA input for the selected paper table and data subset.
    """

    xmlfilename = f"input_{run_name}.xml"

    # -------------------------------------------------------------------------
    # Input/output files
    # -------------------------------------------------------------------------

    define_io["gridfile"] = os.path.join(
        "/Users/z5214708/BASTA/grids",
        "BaSTI_iso2018.hdf5",
    )

    define_io["outputpath"] = os.path.join(
        "output",
        run_name,
    )

    dnu_suffix = "_dnu" if paper["use_dnu"] else ""

    ascii_filename = (
        f"{paper['numax_version']}"
        f"{dnu_suffix}_"
        f"{DATA_SUBSET}.ascii"
    )

    define_io["asciifile"] = os.path.join(
        "data",
        ascii_filename,
    )


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

    # Missing numeric values in the ASCII files should be written as -999.999.
    define_io["missingval"] = -999.999

    # -------------------------------------------------------------------------
    # Fitting parameters
    # -------------------------------------------------------------------------

    fitparams = [
        "numax",
        "Teff",
        "FeH"
    ]

    if paper["use_dnu"]:
        fitparams.insert(1, "dnuAsf")

    if subset["phase_known"]:
        fitparams.append("phase")

    define_fit["fitparams"] = tuple(fitparams)

    define_fit["priors"] = {
        "IMF": "salpeter1955",
    }

    define_fit["odea"] = (
        0.2,  # overshooting
        1,    # diffusion
        0.3,  # mass loss
        0,    # alpha enhancement
    )

    # -------------------------------------------------------------------------
    # Photometric filters
    # -------------------------------------------------------------------------

    filters = ("G_GAIA",)

    if subset["use_jhk"]:
        filters += (
            "Mj_2MASS",
            "Mh_2MASS",
            "Mk_2MASS",
        )

    define_fit["filters"] = filters
    define_fit["dustframe"] = "icrs"
    define_fit["solarmodel"] = True

    # -------------------------------------------------------------------------
    # Output
    # -------------------------------------------------------------------------

    outparams = [
        "Teff",
        "numax",
        "logg",
        "radPhot",
        "massfin",
        "age",
        "distance",
    ]

    if paper["use_dnu"]:
        outparams.insert(2, "dnuAsf")

    define_output["outparams"] = tuple(outparams)
    define_output["outputfile"] = "results.ascii"
    define_output["optionaloutputs"] = False


    # -------------------------------------------------------------------------
    # Plots
    # -------------------------------------------------------------------------

    define_plots["cornerplots"] = define_output["outparams"]
    define_plots["kielplots"] = True
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