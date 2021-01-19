INSERT INTO recordings (repeat, week_day, start_date, stop_date, duration, start_time, camera_topics) 
VALUES 
-- current job
(1, [0, 1, 2, 3, 4, 5, 6], 2021-1-1, 2021-12-30, 8.5, 12:15, ['/camera1', '/camera2']),
-- previous job
(1, [0, 1, 4, 5], 2008-12-1, 2008-12-25, 4.5, 14:15, ['/camera1', '/camera2']),
-- future job
(1, [0, 1, 2, 3, 4, 5, 6], 2022-11-11, 2022-11-15, 4.5, 14:15, ['/camera1', '/camera2']),
-- non repeat
(0, [6], 2021-1-11, 2021-1-15, 4.5, 14:15, ['/camera1', '/camera2']),
-- job goes from one day to another
(1, [0, 1, 2, 3, 4, 5, 6], 2021-1-1, 2021-12-15, 8.0, 20:45, ['/camera1', '/camera2']),
-- short job
(1, [0, 1, 2, 3, 4, 5, 6], 2021-1-1, 2021-11-15, 4.5, 14:15, ['/camera1', '/camera2']),
-- very long job
(1, [0], 2021-1-1, 2021-11-15, 72.0, 14:15, ['/camera1', '/camera2'])
;