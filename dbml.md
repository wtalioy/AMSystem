// Use DBML to define your database structure
// Docs: https://dbml.dbdiagram.io/docs

Table users {
  user_id integer [primary key]
  username varchar
  password varchar
}

Table workers {
  worker_id integer [primary key]
  username varchar
  password varchar
  worker_type varchar
}

Table managers {
  manager_id integer [primary key]
  username varchar
  password varchar
}

Table hourly_wage {
  worker_type varchar [primary key]
  wage_per_hour numeric
}

Table wage_distribution {
  worker_id integer
  distribute_time timestamp
  wage_amount numeric
  primary key (worker_id, distribute_time)
}

Table cars {
  car_id integer [primary key]
  car_type varchar
}

Table repair_orders {
  order_id integer [primary key]
  customer_id integer
  car_id integer
  car_type varchar
}

Table reviews {
  review_id integer [primary key]
  rating integer
  comment text
}

Table repair_progress {
  log_id integer [primary key]
  percentage numeric
  consumption numeric
  cost numeric
  duration numeric
  order_id integer
}

Table repair_records {
  order_id integer [primary key]
  review_id integer
  log_id integer
  is_finished boolean
}

// Relationships

Ref: repair_orders.customer_id > users.user_id
Ref: repair_orders.car_id > cars.car_id
Ref: workers.worker_type > hourly_wage.worker_type
Ref: wage_distribution.worker_id > workers.worker_id
Ref: repair_progress.order_id > repair_orders.order_id
Ref: repair_records.order_id > repair_orders.order_id
Ref: repair_records.review_id > reviews.review_id
Ref: repair_records.log_id > repair_progress.log_id