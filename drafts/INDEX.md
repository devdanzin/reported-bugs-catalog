# Drafts — found-but-not-filed (excluded from filed counts)

These are real findings communicated or written up but **not filed as a GitHub
issue/PR anywhere** (or only sent to a maintainer). They feed the *unfiled-
findings* headline, never the *filed-artifacts* count. Files are pointers to the
source report; nothing is copied here.

| slug | tool | target | findings | status |
|---|---|---|---|---|
| [h5py-get-name-oom-nullderef](h5py-get-name-oom-nullderef.md) | fusil-plugin-h5py | h5py/h5py | 2 | fix-verified, not filed |
| [hdf5-property-list-oom-family](hdf5-property-list-oom-family.md) | fusil-plugin-h5py | The HDF Group / HDF5 (+ h5py) | 4 | 4 ASan stacks, not filed |
| [astropy-cext-review](astropy-cext-review.md) | cext-review-toolkit | astropy/astropy | TBD | gist sent, not filed |
| [coveragepy-ctracer-review](coveragepy-ctracer-review.md) | cext-review-toolkit | nedbat/coveragepy | TBD | sent to maintainer, not filed |
| [numpy-oom-contract](numpy-oom-contract.md) | fusil | numpy/numpy | 1 | optional, not filed |
| [cpython-decimal-dec-addstatus-race](cpython-decimal-dec-addstatus-race.md) | ft-review-toolkit | python/cpython | 1 | M3->M4 backlog, not filed |
| [couchbase-python-client-review](couchbase-python-client-review.md) | cext-review-toolkit | couchbase/couchbase-python-client | 31 | report ready, no outreach |
| [frozendict-review](frozendict-review.md) | cext-review-toolkit | Marco-Sulla/python-frozendict | 13 | report ready, no outreach |
| [uvloop-review](uvloop-review.md) | cext-review-toolkit | MagicStack/uvloop | 41 | paused, not filed |
| [ijson-review](ijson-review.md) | cext-review-toolkit | ICRAR/ijson | 76 | outreach pending |
| [cpython-itertools-grouper-uaf](cpython-itertools-grouper-uaf.md) | cpython-review-toolkit | python/cpython | 1 | draft, not filed |
| [igraph-double-free-48-site](igraph-double-free-48-site.md) | cext-review-toolkit | igraph/python-igraph | 1 | older backlog |

**12 drafts; ~171+ unfiled findings counted here** (h5py/HDF5/astropy/
coveragepy = fusil-plugin + review-toolkit finds; couchbase/frozendict/uvloop/ijson
= review-toolkit backlog; itertools/_decimal = CPython review drafts).

**Note:** the ~22 OOM bugs that are gisted-but-not-individually-filed are NOT here —
they are *findings under the filed umbrella python/cpython#151763*, counted as
findings of that artifact, not as drafts.
