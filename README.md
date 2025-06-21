# 🌈 5-Band Multispectral Labeler

Graphical interface for labeling and cropping 5-band multispectral images, optimized for the MicaSense RedEdge camera.

## 🚀 Quick Start

```bash
# Method 1 - Automatic script (recommended)
cd /home/brus/Projects/HPL/paper/5bands_labeler
bash scripts/start_labeler.sh

# Method 2 - Manual with virtual environment
cd /home/brus/Projects/HPL/paper/5bands_labeler
source venv_labeler/bin/activate
python3 scripts/run_labeler.py

# Method 3 - One-liner
cd /home/brus/Projects/HPL/paper/5bands_labeler && source venv_labeler/bin/activate && python3 scripts/run_labeler.py
```

## 📁 Project Structure

```
5bands_labeler/
├── src/                           # Main source code
│   ├── gui/                       # GUI components
│   │   ├── labeling_gui.py        # Main interface
│   │   ├── coordinate_viewer.py   # Viewer with click-to-select coordinates
│   │   ├── crop_controls.py       # Crop controls
│   │   ├── file_selector.py       # File/folder selector
│   │   └── project_selector.py    # Project selector
│   ├── core/                      # Business logic
│   │   ├── image_cropper.py       # Image cropping logic
│   │   └── project_manager.py     # Project management
│   ├── utils/                     # Utility functions
│   │   ├── image_utils.py         # Image processing helpers
│   │   └── superpixel_utils.py    # Superpixel algorithms
│   └── 5bands_labeler.egg-info/   # Installation metadata
├── scripts/                       # Startup and utility scripts
│   ├── run_labeler.py             # Main entrypoint
│   ├── start_labeler.sh           # Automatic startup script
│   └── create_light_augmented_dataset.py  # Dataset creation utility
├── docs/                          # Detailed documentation
│   └── README.md
├── projects/                      # User projects
│   ├── test_proj/                 # Test project (included in git)
│   ├── project_metadata.json      # Global metadata file
│   └── labeling_project_*/        # User projects (excluded from git)
│       ├── originals/             # Original images
│       ├── crops/                 # Extracted crops
│       └── project_metadata.json  # Project metadata
├── venv_labeler/                  # Python virtual environment
├── setup.py                       # Installation configuration
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## ✨ Features

* **Image loading**: Single, multiple, or TIFF folders
* **5 visualization modes**:

  * Single bands (1–5)
  * Natural RGB (3,2,1)
  * False Color IR (5,3,2) – vegetation in red
  * Red Edge Enhanced (4,3,2) – stress detection
  * NDVI-like (5,4,3) – vegetation health
* **Click to select coordinates**: Get precise pixel location
* **Real-time crop preview**: Dashed yellow box on image
* **Preview extracted crop**: Display of actual cropped patch
* **Square crop**: Centered square crop on selected coordinates
* **Advanced crop controls**: Spinbox, slider, and presets (16–512px)
* **Automatic project management**: `proj/originals/crops/` structure
* **Load existing projects**: Resume previous work
* **Organized saving**: Descriptive crop filenames
* **Automatic cleanup**: Empty projects removed on close

## 📋 Requirements

* **Python 3.7+** (tested up to 3.11)
* **tkinter** (included with Python)
* **Main dependencies**:

  * `Pillow>=9.0.0` – Image processing
  * `numpy>=1.21.0` – Numerical computing
  * `tifffile>=2021.11.2` – TIFF file handling
  * `imagecodecs>=2021.11.20` – TIFF compression support
  * `scikit-image>=0.19.0` – Superpixel algorithms

### Dependency Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

## 📂 Project Management

The labeler automatically organizes work into standardized project folders:

```
projects/
├── project_metadata.json              # Global project registry
├── test_proj/                         # Example project
└── labeling_project_YYYYMMDD_HHMMSS/  # User projects
    ├── originals/                     # Loaded images
    ├── crops/                         # Extracted crops
    │   ├── image1_crop_001.tif
    │   ├── image1_crop_002.tif
    │   └── ...
    └── project_metadata.json          # Project-specific metadata
```

**Highlights**:

* **Automatic creation**: New projects named by timestamp
* **Resume existing**: Continue previous work
* **Safe cleanup**: Empty projects are removed on exit
* **Safe backup**: Only `test_proj` is versioned; user projects are ignored by git

## 📖 Documentation

For detailed instructions, see the [full documentation](docs/README.md).

## 🔧 Development

### Code Overview

**GUI (`src/gui/`)**:

* `labeling_gui.py`: Main GUI and component coordination
* `coordinate_viewer.py`: Image viewer with coordinate click
* `crop_controls.py`: Advanced controls for crop size
* `file_selector.py`: File/folder selection with preview
* `project_selector.py`: Project creation and selection

**Core logic (`src/core/`)**:

* `image_cropper.py`: Cropping algorithms and logic
* `project_manager.py`: Metadata and project structure handling

**Utilities (`src/utils/`)**:

* `image_utils.py`: Visualization and preprocessing functions
* `superpixel_utils.py`: Advanced superpixel segmentation

### Development Installation

```bash
# Clone and set up environment
git clone <repository-url>
cd 5bands_labeler

# Create virtual environment
python3 -m venv venv_labeler
source venv_labeler/bin/activate

# Install in development mode
pip install -e .

# Or install dependencies manually
pip install -r requirements.txt
```

### Testing and Debugging

```bash
# Standard launch
bash scripts/start_labeler.sh

# Launch with virtual environment
source venv_labeler/bin/activate
python3 scripts/run_labeler.py

# Debug with verbose output
python3 -u scripts/run_labeler.py
```

## 📄 License

HPL Project – 5-Band Multispectral Labeler