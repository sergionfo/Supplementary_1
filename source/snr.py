import pandas as pd
import numpy as np
from obspy import read, UTCDateTime

# -----------------------------
# PARAMETERS
# -----------------------------
INPUT_CSV = "G:/AI/Data/metadataTodas_B.csv"
OUTPUT_CSV = "G:/AI/Data/snr_results_p.csv"

P_TIME_COL = "path_p_travel_s"
S_TIME_COL = "path_s_travel_s"
STATION_COL = "station_code"
COMPONENT = "1"
EVENT_COL = "source_origin_time"
FILE_COL = "filename"

PRE_WINDOW = 5.0   # seconds before P
POST_WINDOW = 3.0  # seconds after P

CALC_S = False
# -----------------------------
# FUNCTION TO COMPUTE SNR
# -----------------------------
def compute_snr(trace, p_time):
    """
    Compute SNR using 2s before and 2s after P arrival.
    """
    t = trace.times("utcdatetime")

    # Define windows
    noise_start = p_time - PRE_WINDOW - 0.5
    noise_end = p_time - 0.5
    #noise_start = t[0]
    #noise_end = t[0] + PRE_WINDOW
    if noise_end > p_time:
        print ("Pouco tempo disponivel")
        noise_end = p_time - 0.5
    signal_start = p_time - 0.5
    signal_end = p_time + POST_WINDOW

    # Slice trace
    noise = trace.slice(noise_start, noise_end).data
    signal = trace.slice(signal_start, signal_end).data

    # Avoid empty slices
    if len(noise) == 0 or len(signal) == 0:
        return np.nan

    # RMS-based SNR
    noise_rms = np.sqrt(np.mean(noise**2))
    signal_rms = np.sqrt(np.mean(signal**2))

    if noise_rms == 0 or signal_rms == 0:
        return np.nan

    return  10 * np.log10(signal_rms / noise_rms)


# -----------------------------
# MAIN PROCESSING
# -----------------------------
df = pd.read_csv(INPUT_CSV)

results = []

# Loop over stations
for station, group in df.groupby(STATION_COL):
    print(f"Processing station: {station}")

    snr_values = []

    for _, row in group.iterrows():
        try:
            file_path = f"G:/AI/Data/Waveforms_SEI/{row[FILE_COL]}"
            if not (pd.isna(row[P_TIME_COL]) or str(row[P_TIME_COL]).strip() == ""):
                #continue
                p_time = UTCDateTime(row[P_TIME_COL])
                #s_time = UTCDateTime(row[S_TIME_COL])

                # Read waveform
                st = read(file_path)

                # Select trace for station
                tr = st.select(station=station)

                if len(tr) == 0:
                    print (station + " " + row[FILE_COL])
                    continue
                snr = 0
                for x in range(3):
    #                tr = tr[x]
                    # Compute SNR
                    snr = snr + compute_snr(tr[x], p_time)
                snr = snr/3
                snr_values.append(snr)
            else :
                snr = np.nan
            results.append({
                "event": row[EVENT_COL],
                "station": station,
                "file": file_path,
                "p_time": row[P_TIME_COL],
                "snr": snr
            })

        except Exception as e:
            print(f"Error processing row: {row[FILE_COL]} - {e}")
            continue

    # Remove NaNs
    #snr_values = [x for x in snr_values if not np.isnan(x)]

    if len(snr_values) > 0:
        print(f"{station} -> min: {np.min(snr_values):.2f}, "
              f"max: {np.max(snr_values):.2f}, "
              f"median: {np.median(snr_values):.2f}, "
              f"average: {np.average(snr_values):.2f}")


# -----------------------------
# SAVE RESULTS
# -----------------------------
results_df = pd.DataFrame(results)
results_df.to_csv(OUTPUT_CSV, index=False)


# -----------------------------
# STATION STATISTICS
# -----------------------------
stats = results_df.groupby("station")["snr"].agg(["min", "max", "median", "mean"])
print("\nStation SNR statistics:")
print(stats)

stats.to_csv("./snr_station_stats.csv")