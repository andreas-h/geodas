#!/bin/bash
PYLIT=_utils/pylit
OUTDIR=src
OUTPUT=${1%.txt}.rst
OUTPUT=${OUTPUT#../}
OUTPUT=${OUTPUT//\//.}
OUTPUT=$OUTDIR/$OUTPUT
$PYLIT ${1%.txt} $OUTPUT

