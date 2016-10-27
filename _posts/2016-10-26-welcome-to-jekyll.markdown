---
layout: post
title:  "hi there"
date:   2016-10-26 16:12:44 -0700
categories: ''
---

nothing to see here

<pre><code class="language-klipse">

(ns voke.world.generation)

(defn full-grid [w h]
(vec (repeat h
(vec (repeat w :full)))))

(full-grid 5 5)

</code></pre>

<pre><code class="language-klipse">

(defn grid->str [grid]
(apply str
(map (fn [line]
(str (apply str
(map (fn [cell]
(if (= cell :full)
"X"
" "))
line))
"\n"))
grid)))

(grid->str (full-grid 5 5))

</code></pre>

<pre><code class="language-klipse">

(defn count-empty-spaces [grid]
(apply +
(map (fn [line]
(count
(filter #(= % :empty) line)))
grid)))

(count-empty-spaces (full-grid 5 5))

</code></pre>

<pre><code class="language-klipse">

(-> (full-grid 5 5)
    (assoc-in [1 2] :empty)
	(assoc-in [4 4] :empty)
	count-empty-spaces)

</code></pre>

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
