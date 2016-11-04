---
layout: post
title:  "Procedural Dungeon Generation: Cellular Automata"
klipse: true
custom_js:
- cellular-blog
- seedrandom.min
---

Last time we looked at generating random dungeons using the [Drunkard's Walk]({% post_url 2016-10-31-procedural-dungeon-generation-drunkards-walk-in-clojurescript %}) algorithm. It's fun to play with, and often generates cool levels, but it's also pretty unreliable. That's not good enough for my purposes: I want to reliably generate big, open, cave-like maps, with lots of space for fast-moving enemies to swarm and surround the player.

To that end, we'll be using a [cellular automaton](http://natureofcode.com/book/chapter-7-cellular-automata/) to generate levels that look like this:

<div id="cellular-example"></div>

<script>
voke.world.visualize.cellular_example()
</script>

We're still using a 2D grid to represent our level, but we'll be using some new vocabulary this time. Each spot on the grid is now a *cell*. Each cell is either *alive* or *dead*. (An alive cell is a cave wall, and a dead cell is empty space where the player can move around freely.)

The algorithm starts by generating a grid of these cells, each of which has a certain chance of being alive.

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
(aset "globalAlpha" 0.3)
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

As usual, all the code snippets in this article are interactive --- try changing that `0.5` to a `0.1` or a `0.99`. You can always focus a snippet and press Ctrl+Enter to rerun it, too!

The basic idea with cellular automata is that you start with an initial grid like the one we've just generated, and then you pretend that its cells are bacteria in a petri dish. We'll be simulating the passage of time, during which cells are born and die.[^1]

The algorithm looks like this:

1. If we've run the simulation `num-iterations` times, we're done.
1. For each cell on the grid,
    1. Calculate the number of its neighbors that are alive.
    1. If the cell is dead and has at least `birth-threshold` alive neighbors, it becomes alive.
	1. If the cell is alive and has at least `survival-threshold` neighbors, it stays alive.
	1. Otherwise, the cell is dead.
1. Go back to step 1.

Cells on the outskirts of the grid will have neighbors that are out of bounds --- for simplicity, we'll say that these nonexistent neighbors are alive. (As a bonus, this rule tends to give our levels nice solid walls around the edges.)

<pre><code class="cljs">
(defn spot-is-off-grid?
[grid x y]
(let [height (count grid)
width (count (first grid))]
(or (< x 0)
(>= x width)
(< y 0)
(>= y height))))

(spot-is-off-grid? (generate-grid 5 5 0.5) -1 0)
</code></pre>

Now let's write a function that finds a given cell's neighbors. (In addition to the `draw-grid` function from last time, I've supplied a `draw-higlighted-grid` function that lets you see what your cell's neighbors look like.)

<pre><code class="cljs" data-preamble='(reset! canvas-id "canvas-2")'>
(defn neighbors
[grid x y]
(for [i (range (dec x) (+ x 2))
j (range (dec y) (+ y 2))
; We only care about our *neighbors*.
:when (not= [i j] [x y])]
(if (spot-is-off-grid? grid i j)
:full
(get-in grid [j i]))))

; Let's try it out.
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

; Let's try it out.
(let [grid (generate-grid 5 5 0.5)
[x y] [2 2]]
(draw-grid-highlighted grid x y)
(new-value-at-position grid x y 4 5))
</code></pre>

<canvas id="canvas-3" width="200" height="200"></canvas>

That's all the groundwork we need --- let's implement the algorithm!

<pre><code class="cljs" data-preamble='(reset! canvas-id "canvas-4")'>

(defn automata-iteration
[grid birth-threshold survival-threshold]
(let [height (count grid)
width (count (first grid))]
(loop [new-grid grid
x 0
y 0]

(if (identical? y height)
; Done!
new-grid

; Otherwise:
(let [new-value (new-value-at-position
grid
x
y
birth-threshold
survival-threshold)]
(recur (assoc-in new-grid [y x] new-value)
(if (identical? (inc x) width) 0 (inc x))
(if (identical? (inc x) width) (inc y) y)))))))

(defn automata
[width height initial-probability
birth-threshold survival-threshold iterations]
(nth
(iterate
#(automata-iteration
%
birth-threshold
survival-threshold)
(generate-grid width height initial-probability))
iterations))

(draw-grid
(automata 40 40 0.35 4 5 4))

</code></pre>

<canvas id="canvas-4" width="200" height="200"></canvas>

It... works?

Well, it sure looks like that code is doing *something* to our grid, but it's not easy to tell how we can use this to generate a cool cave like the one we saw at the beginning of this article. This problem is one of the most interesting things about procedural level generation --- whenever you're evaluating an algorithm, you've got to figure out what its inputs are, and try to develop some understanding of how you can manipulate those inputs to get the type of levels that you want.

I didn't pop out of the womb with a well-developed intuition for how birth and survival thresholds affect the shape of caves generated by a cellular automaton, and so I had some trouble figuring out how to proceed when I got to this point. Like last time, building a little tool helped a lot.

<div id="cellular-tool"></div>

<style>
#cellular-tool .message p {
margin-bottom: 0;
}

#slider-canvas {
margin-bottom: 0.5rem;
}
</style>

<script>
voke.world.visualize.cellular_tool()
</script>

After playing around with the different options available, I've come to like using an initial chance of `0.45`, a survival threshold of `4`, and a birth threshold of `5`. This set of parameters seems to reliably generate the specific kind of open cave areas that I'm interested in. Let's give our implementation another try using those values:

<pre><code class="cljs" data-preamble='(reset! canvas-id "canvas-5")'>
(draw-grid
(automata 40 40 0.45 5 4 4))
</code></pre>

<canvas id="canvas-5" width="200" height="200"></canvas>

Looks good! Kinda small, though.

The snippet above runs our code on a `40x40` grid because this implementation of the algorithm is *really, really slow*, and it takes forever if you run it on e.g. a `100x100` grid. The snippets also use `4` as their default number of iterations, whereas in real life I find that a value around `12` makes for smoother caves.

I've written  an alternate version of this code that's much faster, and it powers the bigger caves in this article. I learned a lot about ClojureScript performance in the process, and will write a future post where we start with this article's version of the code and arrive at the optimized implementation.

## One more thing ##

I learned about today's algorithm from [Kyzrati's post on the topic](http://www.gridsagegames.com/blog/2014/06/mapgen-cellular-automata/). His implementation has an additional step: before running the birth/survival/death rules on all cells at once, he starts by running them on **random, individual cells**.

I have an implementation that does this as well, and I *think* I like the results it gives, but I've been playing with it for a couple of weeks and frankly I still have no idea what actual effect it has. It does *something*, and it doesn't seem to make the levels *worse*, so I'm keeping it for now. Give it a shot yourself using [my visualization tool](http://www.jrheard.com/voke/generation.html).

## Future work ##

There's a lot left to do before these levels are super fun and playable:

* If we generate one of these caves, place the player at one end, and put his goal at the other end, he'll have to do a ton of backtracking along the way, which isn't very fun. [Kyzrati's solution](http://www.gridsagegames.com/blog/2014/06/mapgen-cellular-automata/) is to tweak the boundaries of the input grid so that the algorithm generates longer, narrower caves that require less backtracking.
* The algorithm often generates small "island" caves that are completely disconnected from the main cave; I need to write a step that uses a [flood fill](https://en.wikipedia.org/wiki/Flood_fill) to detect those subcaves and fills them in.

This seems like a good stopping point for now, though. We've written some code that generates neato caves! We'll make it better in future posts.

[^1]: This algorithm will seem very familiar to you if you've ever seen [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life).

