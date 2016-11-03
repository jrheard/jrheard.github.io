---
layout: post
title:  "Procedural Dungeon Generation: Cellular Automata"
klipse: true
custom_js:
- seedrandom.min
---

Last time we looked at generating random dungeons using the [Drunkard's Walk]({% post_url 2016-10-31-procedural-dungeon-generation-drunkards-walk-in-clojurescript %}) algorithm. It's fun to play with, and sometimes generates cool levels, but it's also pretty unreliable. That's not good enough for my purposes: I want to reliably generate big, open, cave-like maps, with lots of space for fast-moving enemies to swarm and surround the player.

We'll be using a concept called [cellular automata](http://natureofcode.com/book/chapter-7-cellular-automata/) this time to generate levels that look like this:

<div id="cellular-example"></div>

Again, we're using a 2D grid to represent our level. We'll be using some new vocabulary this time, though.

Each spot on the grid is a *cell*. Each cell is either *alive* or *dead*. (An alive cell is a cave wall, and a dead cell is empty space where the player can move around freely.)

The algorithm starts by generating a grid of cells, each of which has a certain chance of being alive.

<pre class="hidden"><code class="cljs">

(def canvas-id (atom "canvas-1"))

(defn draw-grid
 [grid]
 (let [canvas (js/document.getElementById @canvas-id)
  ctx (.getContext canvas "2d")
  width (count (first grid))
  height (count grid)
  canvas-width (.-width canvas)
  canvas-height (.-height canvas)
  cell-width (/ canvas-width width)
  cell-height (/ canvas-height height)]

  (.clearRect ctx 0 0 canvas-width canvas-height)
  (set! (.-fillStyle ctx) "#CCC")

  (loop [x 0 y 0]

   (when (< y height)
	(when (= (-> grid
			  (get y)
			  (get x))
		   :empty)

	 (doto ctx
	  (.beginPath)
	  (.rect (* x cell-width) (* y cell-height) cell-width cell-height)
	  (.fill)))

	(recur (if (identical? (dec x) width) 0 (inc x))
	 (if (identical? (dec x) width) (inc y) y))))))

(defn highlight-neighbors
[grid x y]
(let [canvas (js/document.getElementById @canvas-id)
  ctx (.getContext canvas "2d")
  width (count (first grid))
  height (count grid)
  canvas-width (.-width canvas)
  canvas-height (.-height canvas)
  cell-width (/ canvas-width width)
  cell-height (/ canvas-height height)]

  (set! (.-fillStyle ctx) "#00ff00")
  (doto ctx
  (.save)
(aset "globalAlpha" 0.2)
(.beginPath)
(.rect (* cell-width (dec x)) (* cell-height (dec y)) (* 3 cell-width) cell-height)
(.fill)
(.beginPath)
(.rect (* cell-width (dec x)) (* cell-height y) cell-width cell-height)
(.fill)
(.beginPath)
(.rect (* cell-width (inc x)) (* cell-height y) cell-width cell-height)
(.fill)
(.beginPath)
(.rect (* cell-width (dec x)) (* cell-height (inc y)) (* 3 cell-width) cell-height)
(.fill)
(.restore))))

(defn draw-grid-highlighted
[grid x y]
(draw-grid grid)
(highlight-neighbors grid x y))

</code></pre>


<pre><code class="cljs" data-preamble='(reset! canvas-id "canvas-1")'>

(defn generate-row
[width full-probability]
(vec
(take width
(repeatedly #(if (< (rand) full-probability)
:full
:empty)))))

(defn generate-grid
[width height full-probability]
(vec
(take height
(repeatedly #(generate-row width full-probability)))))

(draw-grid (generate-grid 50 50 0.5))

</code></pre>

<canvas id="canvas-1" width="200" height="200"></canvas>

As usual, all the code snippets in this article are interactive - try changing that `0.5` to a `0.1` or a `0.99`. You can always focus a snippet and press Ctrl+Enter to rerun it, too!

The basic idea with cellular automata is that you're mimicking the patterns of bacteria in a petri dish (sort of, if you squint a little). You simulate the passage of time, during which cells are born and die.[^1]

The algorithm looks like this:

1. If we've run the simulation `num-iterations` times, we're done.
1. For each cell on the grid,
    1. Calculate the number of its eight neighbors that are alive.
    1. If the cell is dead and has at least `birth-threshold` alive neighbors, mark it as alive.
	1. If the cell is alive and has at least `survival-threshold` neighbors, it stays alive.
	1. Otherwise, the cell is dead.
1. Go back to step 1.

Cells on the outskirts of the grid have neighbors that are out of bounds - for simplicity, we'll count these nonexistent neighbors as full. As a nice bonus, this rule tends to give our levels nice solid walls around the edges.

<pre><code class="cljs">
(defn spot-is-off-grid?
[grid x y]
(let [height (count grid)
width (count (first grid))]
(or (< x 0)
(>= x width)
(< y 0)
(>= y height))))

(spot-is-off-grid? (generate-grid 5 5 0.5) 5 5)
</code></pre>

Now let's write a function that finds a given cell's neighbors. (In addition to the `draw-grid` function from last time, I've supplied a `draw-higlighted-grid` function that lets you see what your cell's neighbors look like.)

<pre><code class="cljs" data-preamble='(reset! canvas-id "canvas-2")'>
(defn neighbors
[grid x y]
(for [i (range (dec x) (+ x 2))
j (range (dec y) (+ y 2))
; We only care about our _neighbors_, not ourself.
:when (not= [i j] [x y])]

(if (spot-is-off-grid? grid i j)
:full
(get-in grid [j i]))))

(let [grid (generate-grid 5 5 0.5)
[x y] [2 2]]
(draw-grid-highlighted grid x y)
(neighbors grid x y))
</code></pre>

<canvas id="canvas-2" width="200" height="200"></canvas>

Now that we're able to count how many of our neighbors are alive, let's figure out how to determine a cell's new value at each step of the simulation.

<pre><code class="cljs" data-preamble='(reset! canvas-id "canvas-3")'>

(defn new-value-at-position
[grid x y birth-threshold survival-threshold]
(let [cell-is-full? (= (get-in grid [y x]) :full)
num-full-neighbors (count
(filter #(= % :full)
(neighbors grid x y)))]
(cond
(and cell-is-full?
(>= num-full-neighbors survival-threshold)) :full
(and (not cell-is-full?)
(>= num-full-neighbors birth-threshold)) :full
:else :empty)))

(let [grid (generate-grid 5 5 0.5)
[x y] [2 2]]
(draw-grid-highlighted grid x y)
(new-value-at-position grid x y 4 5))
</code></pre>

<canvas id="canvas-3" width="200" height="200"></canvas>

and with that...

<pre><code class="cljs" data-preamble='(reset! canvas-id "canvas-4")'>

; TODO
(defn automata-smoothing-pass
[js-grid w h survival-threshold birth-threshold]
(let [new-grid (-copy-js-grid js-grid)]
(loop [x 0
y 0]
(when (< y h)
(-> new-grid
(aget y)
(aset x (-new-value-at-position js-grid x y w h survival-threshold birth-threshold)))
(recur (if (identical? (inc x) w) 0 (inc x))
(if (identical? (inc x) w) (inc y) y))))
new-grid))

</code></pre>

<canvas id="canvas-4" width="200" height="200"></canvas>

how to show before/after?

well, it *looks* like that's working, but that simple before/after doesn't really give us a good idea of what's going on.

i've introduced an `animate-automata` function, which you can use like this:

<pre><code class="cljs" data-preamble='(reset! canvas-id "canvas-5")'>

; TODO
;blat 

</code></pre>

<canvas id="canvas-5" width="200" height="200"></canvas>


[^1]: This algorithm will seem very familiar to you if you've ever seen [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life).

