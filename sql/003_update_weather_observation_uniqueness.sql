-- Weather observations are now identified by their logical location
-- and observation timestamp rather than API-returned coordinates.

ALTER TABLE weather_observations
DROP CONSTRAINT weather_observations_location_time_unique;


ALTER TABLE weather_observations
ADD CONSTRAINT weather_observations_location_time_unique
UNIQUE (location_id, observed_at);