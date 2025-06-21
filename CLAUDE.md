# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

5bands_labeler is a Python desktop application for labeling and cropping multispectral images with 5 bands, optimized for MicaSense Red Edge cameras. It provides a tkinter-based GUI for scientific image processing and machine learning dataset creation.

## Common Commands

### Running the Application
```bash
# Recommended: Automated startup with virtual environment management
bash scripts/start_labeler.sh

# Manual startup with virtual environment
source venv_labeler/bin/activate
python3 scripts/run_labeler.py

# Single command startup
cd /home/brus/Projects/HPL/paper/5bands_labeler && source venv_labeler/bin/activate && python3 scripts/run_labeler.py
```

### Development Setup
```bash
# Install dependencies (from requirements.txt)
pip install pillow numpy tifffile imagecodecs scikit-image

# Install package in editable mode (recommended for development)
pip install -e .

# For development dependencies
pip install pytest pytest-cov black flake8
```

### Virtual Environment
The project uses `venv_labeler/` virtual environment which is automatically managed by `scripts/start_labeler.sh`. Dependencies are installed from `requirements.txt`.

## Architecture

### High-Level Structure
- **GUI Layer** (`src/gui/`): tkinter-based user interface components
- **Core Logic** (`src/core/`): Business logic for image processing and project management
- **Utilities** (`src/utils/`): Reusable image processing functions and superpixel algorithms
- **Scripts** (`scripts/`): Entry points and utility scripts
- **Projects** (`projects/`): User data storage with automatic project management

### Key Components

#### GUI Architecture
- `labeling_gui.py`: Main application controller and window management
- `coordinate_viewer.py`: Image display with click-to-select coordinates
- `crop_controls.py`: Controls for crop size and preview
- `file_selector.py`: File/folder selection interface
- `project_selector.py`: Project management dialog

#### Core Processing
- `project_manager.py`: Handles project creation, loading, and metadata management
- `image_cropper.py`: Multispectral image cropping logic with band preservation
- `image_utils.py`: Common image processing utilities
- `superpixel_utils.py`: SLIC, Felzenszwalb, and Quickshift superpixel segmentation algorithms

### Import System
The codebase uses a clean package-based import structure with proper setuptools configuration:
- No `sys.path` manipulation required
- Uses standard Python package imports throughout
- `setup.py` configures the package with `src/` layout using `find_packages(where="src")` and `package_dir={"": "src"}`
- Modules use absolute imports without `src.` prefix (e.g., `from gui.labeling_gui import main`)
- Package installed in development mode enables clean imports

### Project Data Structure
```
projects/
├── project_name_YYYYMMDD_HHMMSS/
│   ├── originals/              # Source images
│   ├── crops/                  # Generated crops
│   └── project_metadata.json   # Project configuration
└── project_metadata.json       # Global projects index
```

## Multispectral Image Processing

### Supported Formats
- Primary: TIFF multispectral images (5 bands optimal)
- Bands: Blue (475nm), Green (560nm), Red (668nm), Red Edge (717nm), Near-IR (840nm)

### Visualization Modes
- Individual bands (1-5)
- RGB Natural (3,2,1)
- False Color IR (5,3,2) - vegetation in red
- Red Edge Enhanced (4,3,2) - vegetation stress
- NDVI-like (5,4,3) - vegetation health

### Cropping System
- Square crops from 16x16 to 512x512 pixels
- Center-coordinate based cropping
- Real-time preview with overlay
- Automatic file naming based on coordinates and dimensions
- Superpixel-based cropping with SLIC, Felzenszwalb, and Quickshift algorithms

## Development Notes

### Entry Points
- Primary: `scripts/start_labeler.sh` (handles environment setup)
- Direct: `scripts/run_labeler.py` (requires manual environment)
- Module: `src/gui/labeling_gui.py:main()`

### Dependencies
- **Core**: `pillow`, `numpy`, `tifffile`, `imagecodecs`, `scikit-image`
- **GUI**: `tkinter` (standard library)
- **Dev**: `pytest`, `black`, `flake8` (optional)

### File Organization
- Source code in `src/` with modular package structure
- User data isolated in `projects/` (auto-managed)
- Virtual environment in `venv_labeler/` (auto-created)
- Documentation in `docs/` and `README.md`

## Testing

Currently no automated tests are implemented. The application relies on manual testing through the GUI interface.

## Performance Considerations

- Images are displayed at max 800px for GUI performance
- Crops are saved at original resolution
- Memory usage scales with image size and number of bands
- Project cleanup removes empty projects automatically