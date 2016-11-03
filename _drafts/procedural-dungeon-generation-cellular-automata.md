---
layout: post
title:  "Procedural Dungeon Generation: Cellular Automata"
klipse: true
custom_js:
- seedrandom.min
---

recap last post, brief intro to this post
intention is to generate random caves, favoring lots of wide open areas so that fast-moving monsters can surround the player
show example cellular automata finished product


<canvas width="400" height="400"></canvas>

button

we'll be generating caves today using a techniqued called "cellular automata".
this algorithm starts by generating a grid of "cells", each of which has a certain chance of being "alive".
for our purposes, each cell is a location in our dungeon, and if the cell is "alive", then the location is a cave wall.
if the cell is "dead", then the location is empty space where the player can move around and explore.
so let's start off by writing a function that does just that.

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
(.rect (* cell-width (dec x)) (* cell-height (dec y)) (* 3 cell-width) (* 3 cell-height))
(.fill)
(aset "globalAlpha" 0.4)
(.beginPath)
(.rect (* cell-width x) (* cell-height y) cell-width cell-height)
(.fill)
(.restore))))

</code></pre>


<pre><code class="cljs">

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

as usual, all the code snippets in this article are interactive - try changing that `0.5` to a `0.1` or a `0.99`. you can always focus a snippet and press ctrl+enter to rerun it, too!

now that we've got a grid of "alive" and "dead" cells, we'll be running some rules on this grid
explain thresholds for survival, birth, death
you may recognize this as conway's game of life

show example game of life grid

slider for speeding up / slowing down

it turns out that it's useful for generating caves too!

explain neighbors

<pre><code class="cljs" data-preamble='(reset! canvas-id "canvas-2")'>
(defn neighbors
[grid x y]
(let [height (count grid)
width (count (first grid))]

(for [i (range (dec x) (+ x 2))
j (range (dec y) (+ y 2))
:when (not= [i j] [x y])]
(if (or (< i 0)
(>= i width)
(< j 0)
(>= j height))
:full
(get-in grid [j i])))))

(let [grid (generate-grid 5 5 0.5)
x 2
y 3]
(draw-grid grid)
(highlight-neighbors grid x y)
(neighbors grid x y))
</code></pre>

<canvas id="canvas-2" width="200" height="200"></canvas>

the next thing we'll need is a function that takes a `grid`, an `x` position, and a `y` position, and tells us whether or not the cell at that `x,y` position will be alive this round

<pre><code class="cljs" data-preamble='(reset! canvas-id "canvas-3")'>

(defn new-value-at-position
[grid x y birth-threshold survival-threshold]
(let [cell-is-full? (= (get-in grid [y x]) :full)
num-full-neighbors (count
(filter #(= % :full)
(neighbors grid x y)))]
(cond
(and cell-is-full?
(> num-full-neighbors survival-threshold)) :full
(and (not cell-is-full?)
(> num-full-neighbors birth-threshold)) :full
:else :empty)))

(let [grid (generate-grid 5 5 0.5)
x 2
y 3]
(draw-grid grid)
(highlight-neighbors grid x y)
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
