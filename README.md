# Simon Says Party Board

A pass-and-play board game for 1 to 4 players, ages 4 to 6. Roll the dice, move around the board, and do the card on your space. Every right answer earns a star. **First to 10 stars wins!**

**Spaces**
- 🤸 **Move** – a Simon Says action ("Simon says touch your nose!"). On the Stars and Champs levels, sometimes Simon does *not* say it, so you must stay still!
- 🌿 **Nature** – move like an animal or the weather (flap like a bird, sway like a tree).
- 🔤 **Letters** – first letters, missing letters, and spelling words with letter tiles.
- ➕ **Math** – counting, adding, taking away, number patterns.
- 🔷 **Shapes & more** – colors, shapes, counting sides, patterns, rhymes.

**Three levels**
| Level | For | Examples |
|---|---|---|
| 🌱 Sprouts | age 4 | first letters, counting to 6, tap the color or shape, easy moves |
| ⭐ Stars | age 5 | missing letter, add and subtract within 10, sides of shapes, trick Simon cards |
| 🏆 Champs | age 6 | spell 4-letter words, math to 20, number patterns, rhymes, harder moves |

Everything is read aloud (the 🔊 button repeats it), so little ones do not need to read. Move cards are on the honor system: a grown-up can watch and say "good job!". Wrong answers are never scary: you just see the right answer and the game moves on.

Single-file HTML5 game. Open `index.html` in any browser, phone or tablet; it can be added to the home screen. Settings are remembered.

## Tests
`python3 tests/run.py` checks thousands of generated cards on every level, plays full games (1, 2 and 4 players at every level, with right and wrong answers) and checks the layout on phone and tablet sizes. `python3 tests/shots.py` makes screenshots.
