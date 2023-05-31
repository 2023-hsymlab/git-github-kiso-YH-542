use stocks_situation;

create table transactions (id int unsigned auto_increment not null primary key, stock_code int unsigned not null, 
	company_name char(32), trade_situation char(10), trade_day date, amount int unsigned, trade_price float, sum_trade_price float);