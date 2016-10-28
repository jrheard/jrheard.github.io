---
layout: post
title:  "Procedural Dungeon Generation: A Drunkard's Walk in ClojureScript"
---

nothing to see here

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

<pre><code class="cljs">
(defn full-grid [w h]
(vec (repeat h
(vec (repeat w :full)))))

(full-grid 3 5)

</code></pre>

<pre><code class="cljs" data-preamble='(reset! canvas-id "canvas-1")'>
(draw-grid (full-grid 10 10))

</code></pre>
<canvas id="canvas-1" width="200" height="200"></canvas>

<pre><code class="cljs" data-preamble='(reset! canvas-id "canvas-2")'>
(-> (full-grid 10 10)
(assoc-in [1 2] :empty)
(assoc-in [8 5] :empty)
(assoc-in [9 9] :empty)
draw-grid)

</code></pre>

<canvas id="canvas-2" width="200" height="200"></canvas>

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
(drunkards-walk 250)
draw-grid)
</code></pre>

<canvas id="canvas-3" width="400" height="400"></canvas>
