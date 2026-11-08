# 93
# ---------------------------------------------------------------------
# __main__.py -- `python3 -m resonance.studio ...` starts here.
#
# Authorship attributed exclusively to Johnathan 'Qasparr' Monroe, ARR,
# All Rights Reserved, Without Prejudice.
# Written VII day of November, Anno V:xii e.n. (2026 e.v.), under the
# Method of Science, Aim of Religion -- Scientific Illuminism.
#
# MECHANISM: a two-line door. All behaviour lives in cli.main; this
# module exists so the package is executable as a module, which is
# the form both the desk's shell and an agent's tool-call take.
# ---------------------------------------------------------------------

import sys

from resonance.studio.cli import main

if __name__ == "__main__":
    sys.exit(main())

# 93 -- Live, Love, and let Love, Live.
