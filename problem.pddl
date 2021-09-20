
    (define (problem maze_food-prob2)
    (:domain  maze_food)
    (:objects
        
	start_tile
	person1
	d8
	d6
	d7
	d4
	d5
	d2
	d3
	d0
	d1
	g7
	g6
	g5
	g4
	g3
	g2
	g1
	g0
	g8
	food1
	c8
	c3
	c2
	c1
	c0
	c7
	c6
	c5
	c4
	food2)
(:init
	(has person1 food2)
	(north d2 d1)
	(north d5 d4)
	(north g5 g6)
	(north d1 d0)
	(north g0 g1)
	(north g4 g5)
	(north g6 g7)
	(north g1 g2)
	(north d8 d7)
	(north g7 g8)
	(north d4 d3)
	(north c8 g0)
	(north d6 d5)
	(north d3 d2)
	(north g2 g3)
	(north g3 g4)
	(north d0 c8)
	(north d7 d6)
	(food food1)
	(food food2)
	(west c3 c2)
	(west c8 c7)
	(west c6 c5)
	(west c0 start_tile)
	(west c2 c1)
	(west c7 c6)
	(west c5 c4)
	(west c1 c0)
	(west c4 c3)
	(person person1)
	(empty d8)
	(empty d4)
	(empty d0)
	(empty g7)
	(empty c0)
	(empty start_tile)
	(empty d6)
	(empty c2)
	(empty d3)
	(empty g8)
	(empty c1)
	(empty c3)
	(empty d5)
	(empty g6)
	(empty d2)
	(empty g5)
	(empty c6)
	(empty c7)
	(empty g4)
	(empty c5)
	(empty g3)
	(empty c4)
	(empty g2)
	(empty d7)
	(empty g0)
	(empty c8)
	(empty d1)
	(empty g1)
	(at food1 g4)
	(at food2 d4)
	(at person1 g2)
	(east c0 c1)
	(east c3 c4)
	(east c2 c3)
	(east c6 c7)
	(east c5 c6)
	(east start_tile c0)
	(east c1 c2)
	(east c4 c5)
	(east c7 c8)
	(south d1 d2)
	(south g3 g2)
	(south g7 g6)
	(south d5 d6)
	(south g5 g4)
	(south g1 g0)
	(south g2 g1)
	(south g6 g5)
	(south g4 g3)
	(south d4 d5)
	(south g0 c8)
	(south d7 d8)
	(south g8 g7)
	(south d6 d7)
	(south d2 d3)
	(south d0 d1)
	(south d3 d4)
	(south c8 d0)
            )
    (:goal
        (and (has person1 food1) (has person1 food2))
        )
    )
    