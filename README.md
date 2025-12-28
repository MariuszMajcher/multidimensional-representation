# 🌀 Recursive HyperCone Visualizer

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Plotly](https://img.shields.io/badge/Render-Plotly-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

**A novel 3D visualization engine for representing high-dimensional data (4D, 5D, 6D+) using a "Nested Cone" topology.**

Unlike standard hypercubes (tesseracts) which can be visually cluttered, this engine visualizes higher dimensions as **recursive vector sums**. Each dimension acts as a specific directional vector constrained within a progressively larger conical shell, offering a cleaner, "mechanical" view of multi-dimensional position.

---

## Screenshots

![HyperCone Demo](Screenshot%202025-12-28%20103951.png)

---

##  Key Features

* ** Infinite Scalability:** The system is modular. You can define 4, 10, or 50 dimensions, and the engine automatically generates the necessary cones and vectors.
* ** Recursive Vector Sums:** Dimensions >3 are treated as angular vectors (e.g., D4 at 90°, D5 at 135°). The final position is the sum of these translations.
* ** Physics Clamping:** Includes a "Safety Clamp" feature. If a data point attempts to move outside the valid volume of its dimension, it is automatically constrained to the shell boundary.
* ** Batch Processing:** Easily ingest lists of multi-dimensional points (e.g., from CSV or Pandas) and render them as simultaneous paths.
* ** Interactive Output:** Generates standalone, interactive HTML files via Plotly that can be shared, rotated, and zoomed in any browser.

---

## Installation

1.  **Clone the repository**
    ```bash
    git clone [git@github.com:MariuszMajcher/multidimensional-representation.git](git@github.com:MariuszMajcher/multidimensional-representation.git)
    cd HyperCone-Visualizer
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

---
🧩 Code Breakdown
Class: RecursiveHyperSpace

The core engine managing dimensional physics and visualization.
__init__(limit_dimensions=6, system_length=12, base_slope=0.25, ...)

Initializes the coordinate system and safety constraints.

    limit_dimensions: Hard cap on input coordinates (e.g., set to 6 to prevent processing 10D data).

    system_length: Length of the Time (X) axis.

    slope_growth: Determines the volumetric expansion rate for each nested dimension.

_calculate_cone_slope(dim_index_offset)

Internal geometry helper.

    Calculates the precise shell width for any given dimension index using base + (growth * index).

    Ensures strict nesting (e.g., the 5D shell is mathematically guaranteed to be larger than the 4D shell).

add_point(coords, label="Point")

The primary physics logic. Transforms raw coordinates into a constrained 3D path.

    Dimensional Clamping: Checks if a new vector position falls outside its valid dimensional shell. If true, mathematically "clamps" the point to the shell surface to enforce physics constraints.

    Vector Summing: Recursively adds vectors for dimensions >3 based on unique axis angles (default 45° steps).

    Truncation Warning: Automatically detects and truncates inputs that exceed limit_dimensions to prevent runtime crashes.

add_points_from_list(list_of_points)

Batch processor for bulk data.

    Accepts a list of coordinate lists (e.g., [[x,y,z,d4], [x,y,z,d4,d5]]).

    Ideal for ingesting datasets from CSVs or Pandas DataFrames.
---

## 🚀 Quick Start

You can run the engine directly to see a demo:

```bash
python hypercone_engine.py

draw()