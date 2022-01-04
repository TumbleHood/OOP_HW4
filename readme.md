# Planning
Method 1:\
currently, each agent goes in circles around the graph and collects pokemons on the go.\
the first step is to make an agent take the shortest path to a pokemon.\
first, find the edge that is closest to a pokemon, using this formula:\
![formula of the distance between a line and a point](https://wikimedia.org/api/rest_v1/media/math/render/svg/aad3f60fa75c4e1dcbe3c1d3a3792803b6e78bf6)\
while one of P1(x1,y1), P2(x2,y2) is the source and the other is the destination, and (x0,y0) is the pokemon.\
to calculate now the shortest path from the agent to the pokemon, we need to look at the type of the pokemon:\
if the type of the pokemon is negative, it means the pokemon is on the edge going from the higher number to the lower number. so we calculate the shortest path from the agent to the higher number, and the add the distance from it to the lower number (to simply put, the weight of the edge).\
if the type is positive, then we do the same but first to the lower number and then to the higher.\
we do this calculation each time the agent takes a step, in case something in the graph changed.

Results:\
this works perfectly... with only 1 agent. the agent indeed takes the most optimal path everytime.\
however, when more than 1 agent is added, things get complicated, since the previous method checked every agent by order and asserted it the pokemon which is closest to him, regarding the fact that there might be closer agents.\

Method 2:\
for each pokemon, we calculate the "time" it takes to each agent to get to him from their current position. the "time" will be calculate by diving the distance from the pokemon by the agent's speed.\
after that, we decide which agent goes to which pokemon by lookin at who will arrive first.\

Results:\
this works exactly as intended;\
each pokemon gets asserted to the agent which can catch it the fastest, taking into account that the agent will not go directly to it.\
if an agent sees that it will not reach any pokemon faster than all other agents, it stays in place since it better hope a closer pokemon will appear.