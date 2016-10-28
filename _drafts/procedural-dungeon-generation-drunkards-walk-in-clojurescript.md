---
layout: post
title:  "Procedural Dungeon Generation: A Drunkard's Walk in ClojureScript"
---

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
</code></pre>

TODO goog analytics

I'm working on a toy [game](http://github.com/jrheard/voke), and figured it'd be fun to learn how to write code that generates random levels for it. I'd like to show you a simple algorithm for level generation called the [Drunkard's Walk](http://www.roguebasin.com/index.php?title=Random_Walk_Cave_Generation). It generates levels that look like this:

<canvas id="canvas-4" width="400" height="400"></canvas>

As you can see, our level is a simple two-dimensional grid. Each spot on the grid is either empty or full. If it's empty, the player can wander around in there and find monsters and gold and items and stuff. If it's full, then it's a cave wall and the player smacks into it.

The drunkard's-walk algorithm starts with a totally-filled-in level and then hollows it out one cell at a time, so let's start by defining a function that creates a filled-in level.

<pre><code class="cljs">
(defn full-grid [w h]
(vec (repeat h
(vec (repeat w :full)))))

(full-grid 3 5)

</code></pre>

All of the code snippets in this article are interactive - go ahead and change that to <code>(full-grid 10 10)</code> and see what happens.

Our <code>full-grid</code> function is a good start, but its output doesn't really look like a cave. Let's fix that. I've provided a <code>draw-grid</code> function that takes a grid and draws it for you, like this:

<pre><code class="cljs" data-preamble='(reset! canvas-id "canvas-1")'>
(draw-grid (full-grid 10 10))
</code></pre>

<canvas id="canvas-1" width="200" height="200"></canvas>

Of course, that's not a very interesting cave. Let's try it again with a few empty cells carved out by hand, just so we're sure that this <code>draw-grid</code> function actually works.

<pre><code class="cljs" data-preamble='(reset! canvas-id "canvas-2")'>
(-> (full-grid 10 10)
(assoc-in [1 2] :empty)
(assoc-in [8 5] :empty)
(assoc-in [9 9] :empty)
draw-grid)

</code></pre>

<canvas id="canvas-2" width="200" height="200"></canvas>

Did I mention all the code in this article is interactive? Play around with it, go nuts.

Okay, we're getting closer to the actual meat of the algorithm.

<pre><code class="cljs">

(defn bound-between
[number lower upper]
(cond
(< number lower) lower
(> number upper) upper
:else number))

(bound-between 100 2 50)

</code></pre>

<pre><code class="cljs" data-preamble='(reset! canvas-id "canvas-3")'>

(defn drunkards-walk [grid num-empty-cells]
(let [height (count grid)
width (count (first grid))]

(loop [grid grid
x (rand-int width)
y (rand-int height)
empty-cells 0]

(if (= empty-cells num-empty-cells)
; All done!
grid

; Take a step in a random direction.
(let [cell-was-full? (= (get-in grid [y x]) :full)
direction (rand-nth [:north :east :south :west])]

(recur (assoc-in grid [y x] :empty)
(case direction
:east (bound-between (inc x) 0 (dec width))
:west (bound-between (dec x) 0 (dec width))
x)
(case direction
:north (bound-between (dec y) 0 (dec height))
:south (bound-between (inc y) 0 (dec height))
y)
(if cell-was-full?
(inc empty-cells)
empty-cells)))))))

(-> (full-grid 40 40)
(drunkards-walk 350)
draw-grid)
</code></pre>

<canvas id="canvas-3" width="400" height="400"></canvas>


<pre class="hidden"><code class="cljs" data-preamble='(reset! canvas-id "canvas-4")'>(-> (full-grid 40 40) (drunkards-walk 400) draw-grid)</code></pre>
