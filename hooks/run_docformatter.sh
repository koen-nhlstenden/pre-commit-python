#!/bin/bash
docformatter --in-place --wrap-summaries 320 --wrap-descriptions 320 --blank --make-summary-multi-line "$@"
