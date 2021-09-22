
(define (problem simple_football)
(:domain simple-football)
(:objects
	ball1 ball2
	start_tile
	goal_tile
	c0
	c1
	c2
	c3
	g0
	g1
	g2
	g3
	d0
	d1
	d2
	d3
)
(:init
	(ball ball1)
	(ball ball2)

	(same start_tile start_tile)
	(same goal_tile goal_tile)
	(same c0 c0)
	(same c1 c1)
	(same c2 c2)
	(same c3 c3)
	(same g0 g0)
	(same g1 g1)
	(same g2 g2)
	(same g3 g3)
	(same d0 d0)
	(same d1 d1)
	(same d2 d2)
	(same d3 d3)

	(connected start_tile c0)
	(connected c0 start_tile)
	(connected c3 goal_tile)
	(connected goal_tile c3)

	(connected c0 c1)
	(connected c1 c0)
	(connected c1 c2)
	(connected c2 c1)
	(connected c2 c3)
	(connected c3 c2)

	(connected g0 g1)
	(connected g1 g0)
	(connected g1 g2)
	(connected g2 g1)
	(connected g2 g3)
	(connected g3 g2)

	(connected d0 d1)
	(connected d1 d0)
	(connected d1 d2)
	(connected d2 d1)
	(connected d2 d3)
	(connected d3 d2)

	(connected g0 c0)
	(connected c0 g0)
	(connected d0 c0)
	(connected c0 d0)
	(connected g1 c1)
	(connected c1 g1)
	(connected d1 c1)
	(connected c1 d1)
	(connected g2 c2)
	(connected c2 g2)
	(connected d2 c2)
	(connected c2 d2)
	(connected g3 c3)
	(connected c3 g3)
	(connected d3 c3)
	(connected c3 d3)

	(at-ball ball1 d1)
	(at-ball ball2 g2)
	(at-robby start_tile)

)
(:goal
    (and (at-ball ball1 goal_tile) (at-ball ball2 goal_tile))
	)
)
