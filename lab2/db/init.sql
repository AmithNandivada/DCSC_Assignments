drop table if exists animal_dim;
create table animal_dim(
   animal_dim_key serial primary key,
   animal_id varchar,
   animal_type varchar,
   animal_name varchar,
   dob date,
   breed varchar,
   color varchar,
   reprod varchar,
   gender varchar,
   timestmp timestamp
);

drop table if exists timing_dim;
create table timing_dim(
   time_dim_key serial primary key,
   mnth varchar,
   yr int
);

drop table if exists outcome_dim;
create table outcome_dim(
   outcome_dim_key serial primary key,
   outcome_type varchar,
   outcome_subtype varchar
);

drop table if exists outcome_fct;
create table outcome_fct(
   outcome_fct_key serial primary key,
   outcome_dim_key int references outcome_dim(outcome_dim_key),
   animal_dim_key int references animal_dim(animal_dim_key),
   time_dim_key int references timing_dim(time_dim_key)
);

drop table if exists temp_table;
create table temp_table(
   temp_key serial primary key,
   animal_id varchar,
   animal_type varchar,
   animal_name varchar,
   dob date,
   breed varchar,
   color varchar,
   reprod varchar,
   gender varchar,
   timestmp timestamp,
   mnth varchar,
   yr int,
   outcome_type varchar,
   outcome_subtype varchar
);