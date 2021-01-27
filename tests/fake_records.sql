INSERT INTO recordings (repeat, week_day, start_date, stop_date, duration, start_time, camera_topics) 
VALUES 
-- current job
(TRUE, '{0, 1, 2, 3, 4, 5, 6}', '2021-1-1', '2021-12-30', '00:08:30', '12:15', '{"talker1", "talker2"}'),
-- previous job
(TRUE, '{0, 1, 4, 5}', '2008-12-1', '2008-12-25', '00:04:30', '14:15', '{"talker1", "talker2"}'),
-- future job
(TRUE, '{0, 1, 2, 3, 4, 5, 6}', '2022-11-11', '2022-11-15', '00:04:30', '14:15', '{"talker1", "talker2"}'),
-- non repeat
(FALSE, '{6}', '2021-1-11', '2021-1-15', '00:04:30', '14:15', '{"talker1", "talker2"}'),
-- job goes from one day to another
(TRUE, '{0, 1, 2, 3, 4, 5, 6}', '2021-1-1', '2021-12-15', '00:08:00', '20:45', '{"talker1", "talker2"}'),
-- short job
(TRUE, '{0, 1, 2, 3, 4, 5, 6}', '2021-1-1', '2021-11-15', '00:04:30', '14:15', '{"talker1", "talker2"}'),
-- very long job
(TRUE, '{0}', '2021-1-1', '2021-11-15', '03:00:00', '14:15', '{"talker1", "talker2"}'),
-- more and more topics
(TRUE, '{0, 1, 2, 3, 4, 5, 6}', '2021-1-1', '2021-11-15', '00:04:30', '14:15', '{"talker0"}'),
(TRUE, '{0, 1, 2, 3, 4, 5, 6}', '2021-1-1', '2021-11-15', '00:04:30', '14:15', '{"talker0", "talker1"}'),
(TRUE, '{0, 1, 2, 3, 4, 5, 6}', '2021-1-1', '2021-11-15', '00:04:30', '14:15', '{"talker0", "talker1", "talker2"}'),
(TRUE, '{0, 1, 2, 3, 4, 5, 6}', '2021-1-1', '2021-11-15', '00:04:30', '14:15', '{"talker0", "talker1", "talker2", "talker3"}')
;
