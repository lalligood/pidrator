select
    job_data.moment
    , job_data.temperature
    , job_info.jobname
    , job_info.temperature_deg
    , job_info.temperature_setting
    , job_info.starttime
    , job_info.endtime
    , job_info.cookminutes
    , job_info.food_amount
    , users.username
    , users.fullname
    , users.email_address
    , users.password
    , devices.devicename
    , foods.foodname
    , foodcomments.foodcomments
from job_data
    left outer join job_info on job_data.job_id = job_info.id
    left outer join users on job_info.user_id = users.id
    left outer join devices on job_info.device_id = devices.id
    left outer join foods on job_info.food_id = foods.id
    left outer join foodcomments on job_info.id = foodcomments.jobinfo_id