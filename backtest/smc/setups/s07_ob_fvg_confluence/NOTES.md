# s07: Order block + fair value gap confluence

**Idea:** an order block is stronger when the same move also left a fair value gap.

**Rules:** exactly setup 5, but only for order blocks whose leg (from the pullback extreme to the break) contains a
fair value gap in the break direction.

**Event, direction, code:** as setup 5 (`core/orderblocks.py`, flag `has_fvg`).
