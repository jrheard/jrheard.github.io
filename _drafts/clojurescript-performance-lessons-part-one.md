---
layout: post
title:  "ClojureScript Performance Lessons: Part One"
klipse: true
---

Last time, we wrote some code that generated cool caves using a cellular automaton. Our code worked great, but it was really slow. Let's figure out why it's slow.

When you're in a situation like this --- you have some code, it's slow, and you want to make it faster --- you should follow these steps:

1. Run your code a bunch of times and measure how long it takes.
1. Profile it to see why it's slow.
1. Think for a while, come up with an idea, change your code
1. Do step 1 again and see whether (and how much) your idea worked
1. Repeat the whole process until your code isn't too slow any more

So, let's start by measuring our code from the last post.

<pre>
<code>(dotimes [_ 10]
	(automata 40 40 0.45 5 4 12))

Calls: 10 | Min: 1.26s | Max: 2.24s | Mean: 1.61s | Time: 16.07s</code>
</pre>

Now it's time to profile this code so we can find out what parts of it are the slowest.

{% img perf-1-1 %}

Looks like we're spending most of our time in this `count` call in `new-value-at-position`: 

<pre>
<code>(count
  (filter #(= % :alive)
    (neighbor-values grid x y)))
</code></pre>

Well, we're calling `new-value-at-position` 192000 times, so we want this function to be as fast as possible - and this `count` + `filter` setup is probably doing a lot more work than it has to. I bet it's setting up 192000 lazy sequences and all sorts of stuff. Let's try doing this with a manual `loop` + `recur`:

<pre><code>
(defn num-alive-neighbors
[grid x y]
(loop [i (dec x)
j (dec y)
num-alive 0]
(when (= j (+ y 2))
num-alive

(recur (if (= i (inc x)) (dec x) (inc i))
(if (= i (inc x)) (inc j) j)
(if (or (spot-is-off-grid? grid i j)
(and (not= [i j] [x y])
(= (get-in grid [j i]) :alive)))
(inc num-alive)
num-alive)))))

</code></pre>

new time:

{:id :automata, :n-calls 10, :min "122ms", :max "139ms", :mad "3.84ms", :mean "130.2ms", :time% 100, :time "1.3s"}

cranking number of iterations up to 100 from now on so we get more data points

new baseline:

{:id :automata, :n-calls 100, :min "72ms", :max "203ms", :mad "15.91ms", :mean "95.74ms", :time% 100, :time "9.57s"}



caveats:
* all these times/profiles are gathered from dev builds, because production builds take a while and i tend to get distracted and lose my train of thought while i wait for them to finish
* i could have sworn there was something else
