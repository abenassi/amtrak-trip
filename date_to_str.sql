SELECT *, to_char(arrival_date, 'mm-DD-yyyy HH:MIhs') as arrival_date_str, to_char(departure_date, 'mm-DD-yyyy HH:MIhs') as departure_date_str FROM amtrak_trip_points
