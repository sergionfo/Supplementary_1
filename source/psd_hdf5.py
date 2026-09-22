import numpy as np
import pandas as pd
import h5py
import matplotlib.pyplot as plt
from scipy.signal import welch


# ============================================================
# Configuration
# ============================================================

CSV_FILE = "traces.csv"
HDF5_FILE = "traces.hdf5"

OUTPUT_CSV = "average_Z_PSD.csv"
OUTPUT_FIGURE = "average_Z_PSD.png"

PRE_P_SECONDS = 10
POST_P_SECONDS = 100

# Welch PSD segment length
NPERSEG = 4096


# ============================================================
# Read CSV
# ============================================================

df = pd.read_csv(CSV_FILE)

# Only use training traces
df = df[
    df["split"].astype(str).str.lower() == "train"
].copy()

print(f"Number of train traces: {len(df)}")


# ============================================================
# Get P arrival
# ============================================================

def get_p_arrival(row):

    # Prefer P1 arrival
    if (
        "trace_P1_arrival_sample" in row.index
        and pd.notna(row["trace_P1_arrival_sample"])
    ):
        return int(
            round(
                float(row["trace_P1_arrival_sample"])
            )
        )

    # Otherwise use Pg arrival
    if (
        "trace_Pg_arrival_sample" in row.index
        and pd.notna(row["trace_Pg_arrival_sample"])
    ):
        return int(
            round(
                float(row["trace_Pg_arrival_sample"])
            )
        )

    return None


# ============================================================
# Load Z component
# ============================================================

def load_z_trace(h5_file, trace_name):
    """
    Example trace name:

        bucket1$0,:3,:30001

    HDF5 dataset:

        data/bucket1

    Dataset shape:

        (1024, 3, 34099)

    Component order:

        0 = Z
        1 = N
        2 = E

    Therefore:

        bucket1$0,:3,:30001

    corresponds to:

        data/bucket1[0, 0, :30001]
    """

    dataset_name, indexing = trace_name.split("$", 1)

    dataset_path = f"data/{dataset_name}"

    # First item before comma is the trace index
    parts = indexing.split(",")

    trace_index = int(parts[0])

    # We only need the Z component
    z_trace = h5_file[
        dataset_path
    ][trace_index, 0, :]

    return np.asarray(z_trace)


# ============================================================
# Calculate PSDs
# ============================================================

all_psds = []
frequency_axes = []

n_processed = 0
n_skipped = 0


with h5py.File(HDF5_FILE, "r") as h5:

    for _, row in df.iterrows():

        trace_name = str(
            row["trace_name"]
        )

        # ----------------------------------------------------
        # Sampling rate
        # ----------------------------------------------------

        if pd.isna(
            row["trace_sampling_rate_hz"]
        ):
            print(
                f"Skipping {trace_name}: "
                "missing sampling rate"
            )

            n_skipped += 1
            continue

        fs = float(
            row["trace_sampling_rate_hz"]
        )

        # ----------------------------------------------------
        # P arrival
        # ----------------------------------------------------

        p_sample = get_p_arrival(row)

        if p_sample is None:

            print(
                f"Skipping {trace_name}: "
                "no P arrival"
            )

            n_skipped += 1
            continue

        # ----------------------------------------------------
        # Load Z component
        # ----------------------------------------------------

        try:

            trace = load_z_trace(
                h5,
                trace_name
            )

        except Exception as e:

            print(
                f"Skipping {trace_name}: {e}"
            )

            n_skipped += 1
            continue

        # ----------------------------------------------------
        # Samples corresponding to:
        #
        # -10 seconds ---> P ---> +100 seconds
        # ----------------------------------------------------

        samples_before = int(
            PRE_P_SECONDS * fs
        )

        samples_after = int(
            POST_P_SECONDS * fs
        )

        start_sample = (
            p_sample - samples_before
        )

        end_sample = (
            p_sample + samples_after
        )

        # Check boundaries
        if start_sample < 0:

            print(
                f"Skipping {trace_name}: "
                "not enough data before P"
            )

            n_skipped += 1
            continue

        if end_sample > len(trace):

            print(
                f"Skipping {trace_name}: "
                "not enough data after P"
            )

            n_skipped += 1
            continue

        # Extract P-centered window
        window = trace[
            start_sample:end_sample
        ]

        # ----------------------------------------------------
        # Check data
        # ----------------------------------------------------

        if not np.all(
            np.isfinite(window)
        ):

            print(
                f"Skipping {trace_name}: "
                "NaN/Inf in window"
            )

            n_skipped += 1
            continue

        # Remove mean
        window = (
            window - np.mean(window)
        )

        # ----------------------------------------------------
        # PSD
        # ----------------------------------------------------

        nperseg = min(
            NPERSEG,
            len(window)
        )

        frequencies, psd = welch(
            window,
            fs=fs,
            window="hann",
            nperseg=nperseg,
            detrend="constant",
            scaling="density"
        )

        all_psds.append(psd)
        frequency_axes.append(
            frequencies
        )

        n_processed += 1

        print(
            f"Processed {n_processed}: "
            f"{trace_name}"
        )


# ============================================================
# Check
# ============================================================

if len(all_psds) == 0:

    raise RuntimeError(
        "No traces were successfully processed."
    )


# ============================================================
# Average PSD
# ============================================================

# If all traces have the same sampling rate,
# their frequency axes will be identical.

same_frequency_axis = all(
    np.array_equal(
        frequency_axes[0],
        f
    )
    for f in frequency_axes
)


if same_frequency_axis:

    frequencies = frequency_axes[0]

    all_psds = np.asarray(
        all_psds
    )

    average_psd = np.mean(
        all_psds,
        axis=0
    )

else:

    # --------------------------------------------------------
    # Different sampling rates
    #
    # Interpolate onto a common frequency axis.
    # --------------------------------------------------------

    max_frequency = min(
        f[-1]
        for f in frequency_axes
    )

    frequencies = np.linspace(
        0,
        max_frequency,
        len(frequency_axes[0])
    )

    interpolated_psds = []

    for f, psd in zip(
        frequency_axes,
        all_psds
    ):

        interpolated_psd = np.interp(
            frequencies,
            f,
            psd
        )

        interpolated_psds.append(
            interpolated_psd
        )

    average_psd = np.mean(
        interpolated_psds,
        axis=0
    )


# ============================================================
# Save average PSD
# ============================================================

output_df = pd.DataFrame({
    "frequency_hz": frequencies,
    "average_Z_PSD": average_psd
})

output_df.to_csv(
    OUTPUT_CSV,
    index=False
)


# ============================================================
# Plot
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.loglog(
    frequencies[1:],
    average_psd[1:],
    color="black",
    linewidth=2
)

plt.xlabel(
    "Frequency [Hz]"
)

plt.ylabel(
    "PSD [units²/Hz]"
)

plt.title(
    "Average Z-component PSD\n"
    f"{PRE_P_SECONDS} s before P "
    f"to {POST_P_SECONDS} s after P"
)

plt.grid(
    True,
    which="both",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    OUTPUT_FIGURE,
    dpi=300
)

plt.show()


# ============================================================
# Summary
# ============================================================

print()
print("==========================================")
print("Average Z-component PSD")
print("==========================================")
print(f"Train traces     : {len(df)}")
print(f"Processed        : {n_processed}")
print(f"Skipped          : {n_skipped}")
print(
    f"Window           : "
    f"-{PRE_P_SECONDS} to +{POST_P_SECONDS} seconds"
)
print(f"Output CSV       : {OUTPUT_CSV}")
print(f"Output figure    : {OUTPUT_FIGURE}")