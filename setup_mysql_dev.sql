-- prepares a MySQL server for the project

CREATE DATABASE IF NOT EXISTS yelp_dev_db;
CREATE USER IF NOT EXISTS 'yelp_dev'@'localhost' IDENTIFIED BY 'yelp_dev_pwd';
GRANT ALL PRIVILEGES ON `yelp_dev_db`.* TO 'yelp_dev'@'localhost';
GRANT SELECT ON `performance_schema`.* TO 'yelp_dev'@'localhost';
FLUSH PRIVILEGES;
