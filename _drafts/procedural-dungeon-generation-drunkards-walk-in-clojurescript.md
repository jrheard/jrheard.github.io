---
layout: post
title:  "hi there"
---

nothing to see here

<pre class="hidden">
<code class="language-klipse">

(def canvas-id (atom "canvas-1"))
(def canvas-width 400)
(def canvas-height 400)

(defn get-ctx []
(-> @canvas-id
(js/document.getElementById)
(.getContext "2d")))

(defn draw-grid
[grid]
(let [ctx (get-ctx)
width (count (first grid))
height (count grid)
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
</code>
</pre>

<pre><code class="language-klipse">
(defn full-grid [w h]
(vec (repeat h
(vec (repeat w :full)))))

(full-grid 3 10)

</code></pre>


<pre><code class="language-klipse">
(-> (full-grid 10 10)
(assoc-in [1 2] :empty)
(assoc-in [8 5] :empty)
(assoc-in [9 9] :empty)
draw-grid)

</code></pre>

<canvas id="canvas-1" width="400" height="400"></canvas>

<pre><code class="language-klipse">

(defn bound-between
[num lower upper]
(cond
(< num lower) lower
(> num upper) upper
:else num))

(defn drunkards-walk [grid num-empty-cells]
(let [height (count grid)
width (count (first grid))]

(loop [grid grid
[x y] [(rand-int width) (rand-int height)]]

(if (= (count-empty-spaces grid)
num-empty-cells)
grid

(recur (assoc-in grid [y x] :empty)
(case (rand-nth [:north :east :south :west])
:north [x
(bound-between (dec y) 0 height)]
:east [(bound-between (inc x) 0 width)
y]
:south [x
(bound-between (inc y) 0 height)]
:west [(bound-between (dec x) 0 width)
y]))))))

(-> (full-grid 10 10)
(drunkards-walk 20)
grid->str
)
</code>
</pre>
