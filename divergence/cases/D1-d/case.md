# CASE D1-d — ABLATION VARIANT

**Base:** D1, unchanged.
**Planted defect:** values USDC at the USDT print with no mention of the proxy
**Checklist item that should catch it:** 4 instrument/date/pair

This is one of our own four real errors, planted deliberately.

Run against **arm C only**, with node 5 ON and OFF. That is the ablation.
Report the result whichever way it comes out — if node 5 catches nothing,
that is a more interesting finding than a working feature.
