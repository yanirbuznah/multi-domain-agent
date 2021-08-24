(define (problem simple_maze)
(:domain maze_food)
(:objects
	person0
	food1
	start tile
	goal_tile0
	t0A
	t1A
	t2A
	t3A
	t4A
	t5A
	t6A
	t7A
	t8A
	t9A
	t0B
	t1B
	t2B
	t3B
	t4B
	t5B
	t6B
	t7B
	t8B
	t9B
	t0C
	t1C
	t2C
	t3C
	t4C
	t5C
	t6C
	t7C
	t8C
	t9C
	t0D
	t1D
	t2D
	t3D
	t4D
	t5D
	t6D
	t7D
	t8D
	t9D
	t0E
	t1E
	t2E
	t3E
	t4E
	t5E
	t6E
	t7E
	t8E
	t9E
	t0F
	t1F
	t2F
	t3F
	t4F
	t5F
	t6F
	t7F
	t8F
	t9F
	t0G
	t1G
	t2G
	t3G
	t4G
	t5G
	t6G
	t7G
	t8G
	t9G
	t0H
	t1H
	t2H
	t3H
	t4H
	t5H
	t6H
	t7H
	t8H
	t9H
	t0I
	t1I
	t2I
	t3I
	t4I
	t5I
	t6I
	t7I
	t8I
	t9I
	t0J
	t1J
	t2J
	t3J
	t4J
	t5J
	t6J
	t7J
	t8J
	t9J
)
(:init
	(empty t0A)
	(south t0A t0B)
	(empty t1A)
	(east t1A t2A)
	(empty t2A)
	(east t2A t3A)
	(west t2A t1A)
	(empty t3A)
	(east t3A t4A)
	(west t3A t2A)
	(empty t4A)
	(east t4A t5A)
	(west t4A t3A)
	(empty t5A)
	(east t5A t6A)
	(west t5A t4A)
	(empty t6A)
	(south t6A t6B)
	(east t6A t7A)
	(west t6A t5A)
	(empty t7A)
	(south t7A t7B)
	(west t7A t6A)
	(empty t8A)
	(east t8A t9A)
	(empty t9A)
	(south t9A t9B)
	(west t9A t8A)
	(empty t0B)
	(north t0B t0A)
	(east t0B t1B)
	(empty t1B)
	(east t1B t2B)
	(west t1B t0B)
	(empty t2B)
	(east t2B t3B)
	(west t2B t1B)
	(empty t3B)
	(south t3B t3C)
	(west t3B t2B)
	(empty t4B)
	(south t4B t4C)
	(east t4B t5B)
	(empty t5B)
	(south t5B t5C)
	(west t5B t4B)
	(empty t6B)
	(south t6B t6C)
	(north t6B t6A)
	(empty t7B)
	(south t7B t7C)
	(north t7B t7A)
	(empty t8B)
	(south t8B t8C)
	(east t8B t9B)
	(empty t9B)
	(south t9B t9C)
	(north t9B t9A)
	(west t9B t8B)
	(empty t0C)
	(south t0C t0D)
	(east t0C t1C)
	(empty t1C)
	(south t1C t1D)
	(west t1C t0C)
	(empty t2C)
	(south t2C t2D)
	(empty t3C)
	(south t3C t3D)
	(north t3C t3B)
	(empty t4C)
	(south t4C t4D)
	(north t4C t4B)
	(empty t5C)
	(south t5C t5D)
	(north t5C t5B)
	(empty t6C)
	(south t6C t6D)
	(north t6C t6B)
	(empty t7C)
	(north t7C t7B)
	(east t7C t8C)
	(empty t8C)
	(north t8C t8B)
	(west t8C t7C)
	(empty t9C)
	(north t9C t9B)
	(empty t0D)
	(south t0D t0E)
	(north t0D t0C)
	(empty t1D)
	(north t1D t1C)
	(east t1D t2D)
	(empty t2D)
	(south t2D t2E)
	(north t2D t2C)
	(west t2D t1D)
	(empty t3D)
	(south t3D t3E)
	(north t3D t3C)
	(empty t4D)
	(south t4D t4E)
	(north t4D t4C)
	(empty t5D)
	(north t5D t5C)
	(east t5D t6D)
	(empty t6D)
	(north t6D t6C)
	(west t6D t5D)
	(empty t7D)
	(south t7D t7E)
	(east t7D t8D)
	(empty t8D)
	(east t8D t9D)
	(west t8D t7D)
	(empty t9D)
	(south t9D t9E)
	(west t9D t8D)
	(empty t0E)
	(north t0E t0D)
	(east t0E t1E)
	(empty t1E)
	(south t1E t1F)
	(west t1E t0E)
	(empty t2E)
	(south t2E t2F)
	(north t2E t2D)
	(empty t3E)
	(south t3E t3F)
	(north t3E t3D)
	(empty t4E)
	(north t4E t4D)
	(east t4E t5E)
	(empty t5E)
	(east t5E t6E)
	(west t5E t4E)
	(empty t6E)
	(east t6E t7E)
	(west t6E t5E)
	(empty t7E)
	(north t7E t7D)
	(east t7E t8E)
	(west t7E t6E)
	(empty t8E)
	(west t8E t7E)
	(empty t9E)
	(south t9E t9F)
	(north t9E t9D)
	(empty t0F)
	(south t0F t0G)
	(east t0F t1F)
	(empty t1F)
	(north t1F t1E)
	(west t1F t0F)
	(empty t2F)
	(north t2F t2E)
	(empty t3F)
	(north t3F t3E)
	(east t3F t4F)
	(empty t4F)
	(south t4F t4G)
	(west t4F t3F)
	(empty t5F)
	(south t5F t5G)
	(east t5F t6F)
	(empty t6F)
	(east t6F t7F)
	(west t6F t5F)
	(empty t7F)
	(south t7F t7G)
	(west t7F t6F)
	(empty t8F)
	(south t8F t8G)
	(east t8F t9F)
	(empty t9F)
	(south t9F t9G)
	(north t9F t9E)
	(west t9F t8F)
	(empty t0G)
	(south t0G t0H)
	(north t0G t0F)
	(east t0G t1G)
	(empty t1G)
	(east t1G t2G)
	(west t1G t0G)
	(empty t2G)
	(east t2G t3G)
	(west t2G t1G)
	(empty t3G)
	(east t3G t4G)
	(west t3G t2G)
	(empty t4G)
	(north t4G t4F)
	(west t4G t3G)
	(empty t5G)
	(south t5G t5H)
	(north t5G t5F)
	(empty t6G)
	(south t6G t6H)
	(east t6G t7G)
	(empty t7G)
	(north t7G t7F)
	(west t7G t6G)
	(empty t8G)
	(south t8G t8H)
	(north t8G t8F)
	(empty t9G)
	(south t9G t9H)
	(north t9G t9F)
	(empty t0H)
	(north t0H t0G)
	(east t0H t1H)
	(empty t1H)
	(south t1H t1I)
	(west t1H t0H)
	(empty t2H)
	(south t2H t2I)
	(east t2H t3H)
	(empty t3H)
	(east t3H t4H)
	(west t3H t2H)
	(empty t4H)
	(east t4H t5H)
	(west t4H t3H)
	(empty t5H)
	(north t5H t5G)
	(west t5H t4H)
	(empty t6H)
	(north t6H t6G)
	(east t6H t7H)
	(empty t7H)
	(east t7H t8H)
	(west t7H t6H)
	(empty t8H)
	(north t8H t8G)
	(west t8H t7H)
	(empty t9H)
	(south t9H t9I)
	(north t9H t9G)
	(empty t0I)
	(south t0I t0J)
	(empty t1I)
	(south t1I t1J)
	(north t1I t1H)
	(empty t2I)
	(south t2I t2J)
	(north t2I t2H)
	(empty t3I)
	(south t3I t3J)
	(east t3I t4I)
	(empty t4I)
	(east t4I t5I)
	(west t4I t3I)
	(empty t5I)
	(east t5I t6I)
	(west t5I t4I)
	(empty t6I)
	(south t6I t6J)
	(west t6I t5I)
	(empty t7I)
	(south t7I t7J)
	(east t7I t8I)
	(empty t8I)
	(east t8I t9I)
	(west t8I t7I)
	(empty t9I)
	(north t9I t9H)
	(west t9I t8I)
	(empty t0J)
	(north t0J t0I)
	(east t0J t1J)
	(empty t1J)
	(north t1J t1I)
	(east t1J t2J)
	(west t1J t0J)
	(empty t2J)
	(north t2J t2I)
	(west t2J t1J)
	(empty t3J)
	(north t3J t3I)
	(east t3J t4J)
	(empty t4J)
	(east t4J t5J)
	(west t4J t3J)
	(empty t5J)
	(west t5J t4J)
	(empty t6J)
	(north t6J t6I)
	(east t6J t7J)
	(empty t7J)
	(north t7J t7I)
	(east t7J t8J)
	(west t7J t6J)
	(empty t8J)
	(east t8J t9J)
	(west t8J t7J)
	(empty t9J)
	(west t9J t8J)
	(person person0)
	(at person0 t6F)
	(east t1C goal_tile0)
	(west goal_tile0 t1C)
	(food food1)
	(empty goal_tile0)
)
(:reveal ((at person0 goal_tile0) (at food1 goal_tile0) 1))
(:goal
	(and (has person0 food1))
	)
)