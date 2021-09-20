
    (define (problem satellite_multi_effect-prob1)
    (:domain  satellite_multi_effect)
    (:objects
        
	planet11
	phenomenon13
	satellite3
	satellite2
	satellite1
	satellite0
	star10
	thermograph1
	phenomenon12
	thermograph2
	phenomenon14
	groundstation1
	instrument8
	instrument9
	instrument2
	instrument3
	instrument0
	instrument1
	instrument6
	instrument7
	instrument4
	instrument5
	phenomenon5
	image0
	phenomenon8
	phenomenon9
	spectrograph3
	star4
	star7
	star6
	star0
	star3
	star2)
(:init
	(power_on instrument5)
	(power_on instrument9)
	(satellite satellite1)
	(satellite satellite3)
	(satellite satellite0)
	(satellite satellite2)
	(pointing satellite0 phenomenon14)
	(pointing satellite2 star6)
	(pointing satellite1 phenomenon5)
	(pointing satellite3 phenomenon12)
	(have_image star6 thermograph1)
	(have_image phenomenon5 thermograph1)
	(have_image star10 spectrograph3)
	(have_image phenomenon9 image0)
	(have_image phenomenon13 thermograph1)
	(have_image star7 spectrograph3)
	(have_image planet11 thermograph2)
	(have_image phenomenon14 thermograph2)
	(have_image phenomenon8 image0)
	(direction star0)
	(direction planet11)
	(direction star3)
	(direction star2)
	(direction star6)
	(direction phenomenon8)
	(direction groundstation1)
	(direction phenomenon9)
	(direction phenomenon12)
	(direction star10)
	(direction phenomenon13)
	(direction star4)
	(direction phenomenon14)
	(direction star7)
	(direction phenomenon5)
	(on_board instrument3 satellite1)
	(on_board instrument9 satellite3)
	(on_board instrument7 satellite2)
	(on_board instrument6 satellite2)
	(on_board instrument4 satellite1)
	(on_board instrument0 satellite0)
	(on_board instrument1 satellite0)
	(on_board instrument8 satellite3)
	(on_board instrument2 satellite0)
	(on_board instrument5 satellite1)
	(power_avail satellite0)
	(power_avail satellite2)
	(instrument instrument5)
	(instrument instrument8)
	(instrument instrument2)
	(instrument instrument9)
	(instrument instrument3)
	(instrument instrument0)
	(instrument instrument1)
	(instrument instrument6)
	(instrument instrument7)
	(instrument instrument4)
	(calibrated instrument5)
	(calibrated instrument9)
	(mode thermograph2)
	(mode spectrograph3)
	(mode image0)
	(mode thermograph1)
	(supports instrument0 thermograph1)
	(supports instrument7 thermograph1)
	(supports instrument1 thermograph1)
	(supports instrument9 thermograph1)
	(supports instrument5 thermograph2)
	(supports instrument3 thermograph2)
	(supports instrument9 spectrograph3)
	(supports instrument2 spectrograph3)
	(supports instrument5 spectrograph3)
	(supports instrument4 thermograph1)
	(supports instrument6 thermograph1)
	(supports instrument1 spectrograph3)
	(supports instrument3 image0)
	(supports instrument1 thermograph2)
	(supports instrument7 image0)
	(supports instrument5 thermograph1)
	(supports instrument6 thermograph2)
	(supports instrument0 image0)
	(supports instrument7 thermograph2)
	(supports instrument8 image0)
	(supports instrument9 image0)
	(calibration_target instrument4 star4)
	(calibration_target instrument9 star4)
	(calibration_target instrument5 star0)
	(calibration_target instrument7 star0)
	(calibration_target instrument1 star2)
	(calibration_target instrument8 star3)
	(calibration_target instrument3 groundstation1)
	(calibration_target instrument2 star4)
	(calibration_target instrument0 star3)
	(calibration_target instrument6 star3)
            )
    (:goal
        (and (have_image phenomenon5 thermograph1) (have_image star6 thermograph1) (have_image star7 spectrograph3) (have_image phenomenon8 image0) (have_image phenomenon9 image0) (have_image star10 spectrograph3) (have_image planet11 thermograph2) (have_image phenomenon12 image0) (have_image phenomenon13 thermograph1) (have_image phenomenon14 thermograph2))
        )
    )
    