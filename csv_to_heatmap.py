"""
Connectivity Logger CSV → Heatmap
Converts a CSV with columns:
  timestamp, lat, lon, fix_valid, signal_dbm, network_type
into an interactive HTML heatmap using folium.

Usage:
    pip install folium pandas
    python csv_to_heatmap.py your_log_file.csv
"""

import sys
import os
import pandas as pd
import folium
from folium.plugins import HeatMap


def load_csv(path):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]

    # Keep only rows with a valid GPS fix and real coordinates
    df = df[df["fix_valid"].astype(str).str.upper() == "TRUE"]
    df = df.dropna(subset=["lat", "lon"])
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df["signal_dbm"] = pd.to_numeric(df["signal_dbm"], errors="coerce")
    df = df.dropna(subset=["lat", "lon", "signal_dbm"])
    return df


def signal_to_weight(dbm_series):
    """
    Convert dBm to a 0-1 weight where stronger signal = higher weight.
    Typical range: -50 (excellent) to -110 (very poor).
    """
    clipped = dbm_series.clip(lower=-110, upper=-50)
    return (clipped - (-110)) / ((-50) - (-110))


def build_heatmap(df, output_path):
    center_lat = df["lat"].mean()
    center_lon = df["lon"].mean()

    m = folium.Map(location=[center_lat, center_lon], zoom_start=15,
                   tiles="CartoDB positron")

    # --- Signal strength heatmap layer ---
    weights = signal_to_weight(df["signal_dbm"])
    heat_data = list(zip(df["lat"], df["lon"], weights))

    HeatMap(
        heat_data,
        name="Signal strength",
        min_opacity=0.3,
        radius=18,
        blur=12,
        gradient={0.0: "red", 0.4: "orange", 0.7: "yellow", 1.0: "green"},
    ).add_to(m)

    # --- Individual point markers (click for details) ---
    marker_group = folium.FeatureGroup(name="Data points", show=False)
    for _, row in df.iterrows():
        color = point_color(row["signal_dbm"])
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=4,
            color=color,
            fill=True,
            fill_opacity=0.8,
            popup=folium.Popup(
                f"<b>{row.get('network_type', 'N/A')}</b><br>"
                f"Signal: {row['signal_dbm']} dBm<br>"
                f"Time: {row.get('timestamp', 'N/A')}",
                max_width=200,
            ),
        ).add_to(marker_group)
    marker_group.add_to(m)

    # --- Legend ---
    legend_html = """
    <div style="position:fixed; bottom:30px; left:30px; z-index:1000;
                background:white; padding:12px 16px; border-radius:8px;
                border:1px solid #ccc; font-family:sans-serif; font-size:13px;">
      <b>Signal strength</b><br>
      <span style="color:green">●</span> Strong (&gt; -70 dBm)<br>
      <span style="color:orange">●</span> Fair (-70 to -90 dBm)<br>
      <span style="color:red">●</span> Weak (&lt; -90 dBm)
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    folium.LayerControl().add_to(m)

    m.save(output_path)
    print(f"Heatmap saved → {output_path}")
    print(f"Open it in any browser to view.")


def point_color(dbm):
    if dbm >= -70:
        return "green"
    elif dbm >= -90:
        return "orange"
    else:
        return "red"


def main():
    # CSV file in the same folder as this script
    #file to change
    csv_path = "log_1.csv"   # Add .csv if that's the extension

    # Output HTML file
    output_path = "heatmap.html"

    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        sys.exit(1)

    print(f"Loading {csv_path} ...")
    df = load_csv(csv_path)

    if df.empty:
        print("No valid GPS rows found in the CSV. Make sure fix_valid=TRUE rows exist.")
        sys.exit(1)

    print(f"Found {len(df)} valid GPS points. Building heatmap ...")
    build_heatmap(df, output_path)


if __name__ == "__main__":
    main()
