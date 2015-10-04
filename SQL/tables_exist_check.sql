select
    table_name
from information_schema.tables
where
    table_schema = 'public';

'''
QUERY RETURNS:

table_name  
--------------
devices
foodcomments
foods
job_data
job_info
users
(6 rows)
'''
