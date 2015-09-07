insert into users (username, fullname, email_address, password) values
('lalligood', 'Lance Alligood', 'lalligood@gmail.com', crypt('demoman8', gen_salt('bf')))
returning *