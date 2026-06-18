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

from game.pigeon import should_flip, Anim
from game.directions import UP, DOWN, LEFT, RIGHT

def test_should_flip_left_true_right_false():
    assert should_flip(LEFT, RIGHT) is True
    assert should_flip(RIGHT, LEFT) is False

def test_should_flip_vertical_keeps_last_horizontal():
    assert should_flip(UP, LEFT) is True
    assert should_flip(DOWN, RIGHT) is False
    assert should_flip(None, LEFT) is True

def test_anim_loops():
    a = Anim(["a", "b", "c"], fps=10)  # 100 ms/frame
    a.update(100); assert a.i == 1
    a.update(100); assert a.i == 2
    a.update(100); assert a.i == 0

def test_anim_no_loop_clamps_and_finishes():
    a = Anim(["a", "b"], fps=10, loop=False)
    a.update(1000)
    assert a.i == 1
    assert a.finished is True
