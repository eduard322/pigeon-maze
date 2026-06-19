from game.storage import MemoryStorage, BestScores

def test_first_record_sets_both():
    bs = BestScores(MemoryStorage())
    improved_time, improved_eff = bs.record(5000, 0.8)
    assert improved_time and improved_eff
    assert bs.best_time_ms() == 5000
    assert bs.best_efficiency() == 0.8

def test_better_time_only_improves_time():
    bs = BestScores(MemoryStorage())
    bs.record(5000, 0.8)
    improved_time, improved_eff = bs.record(4000, 0.7)
    assert improved_time is True
    assert improved_eff is False
    assert bs.best_time_ms() == 4000
    assert bs.best_efficiency() == 0.8

def test_worse_run_changes_nothing():
    bs = BestScores(MemoryStorage())
    bs.record(4000, 0.9)
    improved_time, improved_eff = bs.record(6000, 0.5)
    assert improved_time is False
    assert improved_eff is False
    assert bs.best_time_ms() == 4000
    assert bs.best_efficiency() == 0.9

def test_summary_line_empty_when_no_scores():
    assert BestScores(MemoryStorage()).summary_line() == ""
