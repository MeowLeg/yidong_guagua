create table flows(
	id integer primary key autoincrement,
	phone varchar(20) unique,
	deviceToken varchar(50) unique,
	flows integer default 0,
	left integer default 3
);

/*

create table buffer (
	phone varchar(20) unique,
	code char(6)
);

insert into flows(phone, deviceToken) values("1234567890", "111");

*/
