# Planning
currently, each agent goes in circles around the graph and collects pokemons on the go.\
the first step is to make an agent take the shortest path to a pokemon.\
first, find the edge that is closest to a pokemon, using this formula:\
![equation](https://wikimedia.org/api/rest_v1/media/math/render/svg/aad3f60fa75c4e1dcbe3c1d3a3792803b6e78bf6)
while one of P1, P2 is the source and the other is the destination.\
to calculate now the shortest path from the agent to the pokemon, we need to look at the type of the pokemon:\
if the type of the pokemon is negative, it means the pokemon is on the edge going from the higher number to the lower number. so we calculate the shortest path from the agent to the higher number, and the add the distance from it to the lower number (to simply put, the weight of the edge).\
if the type is positive, then we do the same but first to the lower number and then to the higher.\
