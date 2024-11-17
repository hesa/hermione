# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

HERMIONE_MATRIX_SRC_UNMOD=hermione-matrix-DistributionNonSource-Unmodified.json
HERMIONE_MATRIX_SRC_ALT=hermione-matrix-DistributionNonSource-Altered.json
HERMIONE_MATRIX_BIN_UNMOD=hermione-matrix-DistributionSource-Unmodified.json
HERMIONE_MATRIX_BIN_ALT=hermione-matrix-DistributionSource-Altered.json

MATRICES=$(HERMIONE_MATRIX_SRC_UNMOD) $(HERMIONE_MATRIX_SRC_ALT) $(HERMIONE_MATRIX_BIN_UNMOD) $(HERMIONE_MATRIX_BIN_ALT)


matrices: $(MATRICES)

%.json:
	PYTHONPATH=. scripts/hermine_data.py

lint:
	reuse lint

clean:
	rm -f *.json
	find . -type f -name "*~" | xargs rm -f
	rm -fr scripts/__pycache__
