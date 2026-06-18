import pygame
from game.pigeon import slice_sheet

def test_slice_sheet_walk_counts_and_sizes():
    sheet = pygame.Surface((96, 32), pygame.SRCALPHA)
    frames = slice_sheet(sheet, 32, 32)
    assert len(frames) == 3
    assert all(f.get_size() == (32, 32) for f in frames)

def test_slice_sheet_peck_width():
    sheet = pygame.Surface((192, 32), pygame.SRCALPHA)
    frames = slice_sheet(sheet, 48, 32)
    assert len(frames) == 4
    assert all(f.get_size() == (48, 32) for f in frames)
