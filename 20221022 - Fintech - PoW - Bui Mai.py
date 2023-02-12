# -*- coding: utf-8 -*-

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1b6orZCZ7ZrSfH_aTkY5sJTjZuT_1O7qu

# Quiz 3: PoW


---


**Author:** thi-thanh-mai.bui@tsm-education.fr
**Version:** 22/10/2022


---

This list describes the fields in the dataset (and their unit) provided for this session:

1. `time`:
Block timestamp, as set by the miner
(Datetime, UTC)
1. `height`:
Block height
(Height)
1. `revenue`:
Total revenue collected by the miner, that is, sum of outputs of the coinbase transaction. This is equal to the block reward pocketed by the miner (i.e. new bitcoins created) plus total fees collected by the miner.
(Satoshi)
1. `fee`:
Total fees collected by the miner: sum for all transactions (but excluding the coinbase) of the difference between the total input and total output of the transaction.
(Satoshi)
1. `tx_count`:
Number of transactions in the block (including the coinbase)
(Number)
1. `base_size`:
Size of the part of the block which counts against the 1MB (1 million bytes) block size limit.
(Byte)
1. `input_count`:
Total number of inputs of all transactions in the block
(Number)
1. `input_value`:
Total input value of all transactions in the block
(Satoshi)
1. `output_count`:
Total number of outputs of all transactions in the block (including the coinbase transaction)
(Number)
1. `output_value`:
Total output value of all transactions in the block (including the output of the coinbase transaction)
(Satoshi)
1. `protocol_block_reward`:
Block reward as set by the protocol (note: this value is not stored into the block itself; according to the protocol, a block is considered as invalid if the miner tries to collect more than this value)
(Satoshi)
1. `difficulty`:
Block difficulty
(Difficulty)
"""

# mount my Google Drive on the VM

from google.colab import drive
drive.mount('/gdrive')

#
# Setup
#

import os
from pathlib import Path
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

#
# Read the csv file containing block data
#

# where the data file is located
DIR_DATA = "/gdrive/MyDrive/Classroom/UE05 FinTech M2 Finance FIT 2022-2023/data"

bk = pd.read_csv(os.path.join(DIR_DATA, 'blocks_for_FIT_satoshis.csv'), 
                 parse_dates=['time'],
                 nrows=None) # use a number instead of None to read only a few lines

display(bk.dtypes)
bk

"""## 1) Check whether blocks always have their timestamp greater than the timestamp of the previous block."""

# blocks having a timestamp lower than the timestamp of their immediate parent 
bk['negative_block_time'] = bk.sort_values('height')['time'].diff().dt.total_seconds() < 0

r = bk[bk['negative_block_time']]
if not r.empty:
  print("{:,} blocks have a negative block time.".format(r.shape[0]))

"""## 2) If it is not the case, explain how is it even possible to observe that.

The Bitcoin protocol allows for negative time betwwen blocks, to some extent.

See https://en.bitcoin.it/wiki/Protocol_rules:

```
13. Reject if timestamp is the median time of the last 11 blocks or before
```

The timetsamp of a block is freely set by the miner which mined that block. Of course, we can expect the miner to set this timestamp in compliance with the rule above, because if it does not the block will be considered as invalid. But there is no guarantee that the timetsamp is "accurate" (e.g., set by a time server synced with an atomic clock).

Thus, when a block is marked as "unsynced" by the code above, it does not mean that the miner which mined that block is out of sync with the true world clock. It may be the miner which mined the parent block, or both.
"""

r

"""## 3)​ Check that difficulty adjustments only occur as specified by the protocol, that is, only once every 2016 blocks."""

# compute 2016-block sequence number (first sequence is numbered 0)
bk['diff_seq'] = bk['height'] // 2016

# compute a series of the number of difficulty values per sequence number
dc = bk.groupby(['diff_seq'])['difficulty'].nunique()

# select sequence numbers for which a difficulty adjustment occurred within the sequence
bad_dc = dc[dc > 1]

# check that difficulty level is unique within each sequence number 
if bad_dc.size != 0:
  print("Difficulty adjustment occurred within the following sequences:")
  print(bad_dc)
else:
  print("Checked")

"""## 4) Measure the congestion of the bitcoin network through time, that is, to what extent (in percent) blocks are full.

### Block size (measure of congestion)
The 1 MB limit was introduced in July 2010. However, until 2013, a bug limited the actual size 
to 500-750 kb.

Thus, using a 1 MB capacity for all the blocks is an approximation. However, since the actual 
size has always been tiny when the 1 MB limit was implemented, the congestion rate computed 
with that limit is very close to zero. Moreover, the limit introduced by the bug was unknown,
hit only once, and has been quickly resolved.

See https://en.bitcoin.it/wiki/Block_size_limit_controversy

Commits in the reference client that set the 1 MB limit:
* 2010-07-15: https://github.com/bitcoin/bitcoin/commit/a30b56eb
* 2010-09-30: https://github.com/bitcoin/bitcoin/commit/a790fa46f40
"""

MAX_BLOCK_SIZE = 1_000_000
bk['congestion_pct'] = bk['base_size']/MAX_BLOCK_SIZE * 100

pct_full = bk['congestion_pct'].mean()

print("On average blocks are {:.2f}% full.".format(pct_full))

"""## 5) Plot the monthly average block congestion rate."""

# plot monthly average congestion rate
ax = bk[['time','congestion_pct']].set_index('time').resample('M').mean() \
    .plot(figsize=(10, 6), grid=True, title="Bitcoin block congestion (monthly average)", legend=False)
ax.set_ylabel('congestion (% of maximum block size)')
ax.yaxis.set_major_formatter(mtick.PercentFormatter())

"""## (+) Difficulty"""

# weekly average difficulty
ax = bk[['time','difficulty']].set_index('time').resample('W').mean() \
    .plot(figsize=(10, 6), grid=True, title="Difficulty (weekly average)", legend=False)
ax.set_ylabel('Difficulty')