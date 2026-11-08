# 93
# ---------------------------------------------------------------------
# resonance.studio -- the production pipeline of the house.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Founded VII day of November, Anno V:xii e.n. (2026 e.v.).
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: RESONANTIA composes and grounds (the Sigma binaural
# layer), local MusicGen voices the bed through the venv bridge, and
# the mastering chain finishes -- loudness to target, ceiling as law.
# One spec in; one mastered track and one honest manifest out.
# DOCTRINE: usable two ways or it is not usable at all -- from the
# command line by a human, and from a JSON spec by an agent. AGENT.md
# in this package is the contract for the second door.
# ---------------------------------------------------------------------

from resonance.studio.pipeline import (
    TARGET_SR,
    master_signal,
    measure_loudness_lufs,
    produce,
    validate_spec,
)

__all__ = [
    "TARGET_SR",
    "master_signal",
    "measure_loudness_lufs",
    "produce",
    "validate_spec",
]

# 93 -- Live, Love, and let Love, Live.
