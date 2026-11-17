#!/usr/bin/env python3
# =============================================================================
# RESONANTIA — tests/test_studio_cubes.py — the parallel-cubes record
#
# Thelemic date: XVII day of November, dies Martis, Sol in Scorpio,
# Anno V:xii e.n. (2026 e.v.)
#
# 93.
#
# Authorship: Johnathan 'Qasparr' (Κασπάρρ) Monroe,
# Keeper of the Secret Treasure.
#
# SCIENTIFIC ILLUMINISM: the studio's shared parallel-cubes record is
# judged the way the house judges everything — its figures re-derived
# from the bases it declares, its Greek seats checked against the
# values PONTIFEX measured, and the pyramidasphere scene's summary
# proven to cite the record rather than a copy. A record that cannot
# be re-derived is not a record; it is a rumor with a file name.
#
# All Rights Reserved, Without Prejudice.
# "Live, Love, and let Love, Live."
# =============================================================================

"""Tests for resonance/studio/cubes.py and its shared JSON record."""

import unittest

from resonance.studio import cubes
from resonance.studio import pyramidasphere


class TestParallelCubesRecord(unittest.TestCase):
    """The record answers to arithmetic, not to its own print."""

    def test_loader_checks_all_pass(self):
        # MECHANISM: cubes_checks() re-derives every figure from the
        # declared bases; a single drifted figure fails by name.
        results = cubes.cubes_checks()
        self.assertTrue(results)
        for name, passed, got in results:
            self.assertTrue(passed, f"{name}: {got}")

    def test_the_two_cubes_stand_in_parallel(self):
        # The sworn figures of the parallel, asserted directly so a
        # reader sees what the record swears: 77³ beside 93³, their
        # factors, their folds.
        summary = cubes.parallel_summary()
        self.assertEqual(summary["77"]["cube"], 456533)
        self.assertEqual(summary["77"]["factorization"],
                         {"7": 3, "11": 3})
        self.assertEqual(summary["77"]["threefold"], 1369599)
        self.assertEqual(summary["93"]["cube"], 804357)
        self.assertEqual(summary["93"]["factorization"],
                         {"3": 3, "31": 3})
        self.assertEqual(summary["93"]["threefold"], 2413071)

    def test_every_row_carries_its_reasoning(self):
        # The 777 rule, enforced as a test: no seat without its
        # reasoning inline — cubes, Greek seats, the circuit, the
        # palette.
        record = cubes.load_record()
        for row in record["cubes"].values():
            self.assertTrue(row["reasoning"])
        for row in record["greek_seats"].values():
            self.assertTrue(row["reasoning"])
        for row in record["synergy_circuit"]:
            self.assertTrue(row["reasoning"])
        self.assertTrue(record["palette"]["reasoning"])
        self.assertTrue(record["declared_equation"]["reasoning"])

    def test_declared_equation_keeps_both_figures(self):
        # The founder's inscription stands as his declaration; the
        # arithmetic beside it is never smoothed into it.
        de = cubes.parallel_summary()["declared_equation"]
        self.assertEqual(de["inscription"], "31^3 = 93")
        self.assertEqual(de["by_multiplication"], 29791)
        self.assertEqual(de["by_threefold_sum"], 93)

    def test_scene_cites_the_record_not_a_copy(self):
        # The pyramidasphere module reads the parallel through the
        # loader: its render() summary is built with
        # cubemod.parallel_summary() — proven here at the seam the
        # summary is assembled from, without a full encode.
        self.assertIs(pyramidasphere.cubemod, cubes)
        self.assertEqual(pyramidasphere.cubemod.parallel_summary(),
                         cubes.parallel_summary())


if __name__ == "__main__":
    unittest.main()


# =============================================================================
# Closing motto: "Live, Love, and let Love, Live."
# 93. All Rights Reserved, Without Prejudice.
# =============================================================================
