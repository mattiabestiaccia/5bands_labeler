#!/usr/bin/env python3
"""
Test per verificare che il FileSelector gestisca correttamente l'aggiunta di immagini
a progetti esistenti senza sostituire le immagini già presenti.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Aggiungi il percorso src al PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.file_selector import FileSelector
from src.core.project_manager import ProjectManager


class MockCallback:
    """Mock callback per testare FileSelector"""
    def __init__(self):
        self.has_active_project = False
        self.selection_changes = []
        self.double_clicks = []
    
    def on_selection_change(self, paths, selection_type):
        self.selection_changes.append((paths[:], selection_type))
        print(f"Selection change: {selection_type} - {len(paths)} paths")
    
    def on_file_double_click(self, path):
        self.double_clicks.append(path)
        print(f"Double click: {path}")
    
    def has_active_project_callback(self):
        return self.has_active_project


def create_test_files(temp_dir):
    """Crea file di test"""
    # Crea alcuni file TIFF di test
    files = []
    for i in range(1, 4):
        file_path = temp_dir / f"test_image_{i}.tif"
        file_path.write_text(f"Mock TIFF content {i}")
        files.append(str(file_path))
    
    # Crea una cartella con file TIFF
    folder_path = temp_dir / "test_folder"
    folder_path.mkdir()
    folder_files = []
    for i in range(1, 3):
        file_path = folder_path / f"folder_image_{i}.tif"
        file_path.write_text(f"Mock folder TIFF content {i}")
        folder_files.append(str(file_path))
    
    return files, str(folder_path), folder_files


def test_file_selector_without_project():
    """Test comportamento senza progetto attivo"""
    print("\n=== Test: Senza progetto attivo ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        files, folder_path, folder_files = create_test_files(temp_path)
        
        # Crea mock callback
        callback = MockCallback()
        callback.has_active_project = False
        
        # Simula FileSelector (senza GUI)
        file_selector = FileSelector.__new__(FileSelector)
        file_selector.on_selection_change = callback.on_selection_change
        file_selector.on_file_double_click_callback = callback.on_file_double_click
        file_selector.has_active_project_callback = callback.has_active_project_callback
        file_selector.selected_paths = []
        file_selector.selection_type = "none"
        
        # Test 1: Seleziona file singolo
        file_selector._add_paths_to_selection([files[0]], "single_file")
        assert file_selector.selected_paths == [files[0]]
        assert file_selector.selection_type == "single_file"
        print("✅ File singolo: OK")
        
        # Test 2: Seleziona file multipli (dovrebbe sostituire)
        file_selector._add_paths_to_selection(files[1:], "multiple_files")
        assert file_selector.selected_paths == files[1:]
        assert file_selector.selection_type == "multiple_files"
        print("✅ File multipli (sostituzione): OK")


def test_file_selector_with_project():
    """Test comportamento con progetto attivo"""
    print("\n=== Test: Con progetto attivo ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        files, folder_path, folder_files = create_test_files(temp_path)
        
        # Crea mock callback
        callback = MockCallback()
        callback.has_active_project = True
        
        # Simula FileSelector (senza GUI)
        file_selector = FileSelector.__new__(FileSelector)
        file_selector.on_selection_change = callback.on_selection_change
        file_selector.on_file_double_click_callback = callback.on_file_double_click
        file_selector.has_active_project_callback = callback.has_active_project_callback
        file_selector.selected_paths = []
        file_selector.selection_type = "none"
        file_selector._find_tiff_files = lambda path: folder_files if path == folder_path else []
        
        # Test 1: Carica file iniziale
        file_selector._add_paths_to_selection([files[0]], "single_file")
        assert file_selector.selected_paths == [files[0]]
        assert file_selector.selection_type == "single_file"
        print("✅ File iniziale: OK")
        
        # Test 2: Aggiungi altro file (dovrebbe aggiungere, non sostituire)
        file_selector._add_paths_to_selection([files[1]], "single_file")
        assert len(file_selector.selected_paths) == 2
        assert files[0] in file_selector.selected_paths
        assert files[1] in file_selector.selected_paths
        assert file_selector.selection_type == "multiple_files"
        print("✅ Aggiunta file singolo: OK")
        
        # Test 3: Aggiungi file multipli
        file_selector._add_paths_to_selection([files[2]], "single_file")
        assert len(file_selector.selected_paths) == 3
        assert all(f in file_selector.selected_paths for f in files)
        assert file_selector.selection_type == "multiple_files"
        print("✅ Aggiunta file multipli: OK")


def test_folder_to_files_conversion():
    """Test conversione cartella + file"""
    print("\n=== Test: Conversione cartella + file ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        files, folder_path, folder_files = create_test_files(temp_path)
        
        # Crea mock callback
        callback = MockCallback()
        callback.has_active_project = True
        
        # Simula FileSelector (senza GUI)
        file_selector = FileSelector.__new__(FileSelector)
        file_selector.on_selection_change = callback.on_selection_change
        file_selector.on_file_double_click_callback = callback.on_file_double_click
        file_selector.has_active_project_callback = callback.has_active_project_callback
        file_selector.selected_paths = []
        file_selector.selection_type = "none"
        file_selector._find_tiff_files = lambda path: folder_files if path == folder_path else []
        
        # Test 1: Carica cartella
        file_selector._add_paths_to_selection([folder_path], "folder")
        assert file_selector.selected_paths == [folder_path]
        assert file_selector.selection_type == "folder"
        print("✅ Cartella iniziale: OK")
        
        # Test 2: Aggiungi file singolo (dovrebbe espandere cartella)
        file_selector._add_paths_to_selection([files[0]], "single_file")
        assert file_selector.selection_type == "multiple_files"
        assert all(f in file_selector.selected_paths for f in folder_files)
        assert files[0] in file_selector.selected_paths
        print("✅ Cartella + file singolo: OK")


def test_files_to_folder_conversion():
    """Test conversione file + cartella"""
    print("\n=== Test: Conversione file + cartella ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        files, folder_path, folder_files = create_test_files(temp_path)
        
        # Crea mock callback
        callback = MockCallback()
        callback.has_active_project = True
        
        # Simula FileSelector (senza GUI)
        file_selector = FileSelector.__new__(FileSelector)
        file_selector.on_selection_change = callback.on_selection_change
        file_selector.on_file_double_click_callback = callback.on_file_double_click
        file_selector.has_active_project_callback = callback.has_active_project_callback
        file_selector.selected_paths = []
        file_selector.selection_type = "none"
        file_selector._find_tiff_files = lambda path: folder_files if path == folder_path else []
        
        # Test 1: Carica file singolo
        file_selector._add_paths_to_selection([files[0]], "single_file")
        assert file_selector.selected_paths == [files[0]]
        assert file_selector.selection_type == "single_file"
        print("✅ File iniziale: OK")
        
        # Test 2: Aggiungi cartella (dovrebbe espandere cartella)
        file_selector._add_paths_to_selection([folder_path], "folder")
        assert file_selector.selection_type == "multiple_files"
        assert files[0] in file_selector.selected_paths
        assert all(f in file_selector.selected_paths for f in folder_files)
        print("✅ File + cartella: OK")


def main():
    """Esegue tutti i test"""
    print("🧪 Test FileSelector - Aggiunta immagini a progetti esistenti")
    
    try:
        test_file_selector_without_project()
        test_file_selector_with_project()
        test_folder_to_files_conversion()
        test_files_to_folder_conversion()
        
        print("\n🎉 Tutti i test sono passati!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test fallito: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
