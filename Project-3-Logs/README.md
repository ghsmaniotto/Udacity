# Logs Analysis Project
## By Gustavo Smaniotto

This project sets up a mock PostgreSQL database for a fictional news website.

The provided Python script uses the psycopg2 library to query the database and produce a report that answers the following three questions:

**1)  What are the most popular three articles of all time?**

**2)  Who are the most popular article authors of all time?**

**3) On which days did more than 1% of requests lead to errors?**


The database file is compressed in `database.zip`. Because that is necessary to uncompress this file and follow **Usage** section to set up the database.

### Usage

First of all, you need to set up the database using the file `newsdata.sql` and the comand

``` sh
    psql -d news -f newsdata.sql
```

After that, you need to connect to the table `news` to add a view. To do it, run:

```sh
    psql -d news
```

and type the SQL command:

```sql
    CREATE VIEW articles_log AS
        SELECT path,
            count(*) as qntd
        FROM log
        WHERE path LIKE '/article/%'
        GROUP BY log.path
        ORDER BY qntd DESC;
```

Next, exit the database connection `\q` command, like:

```sh
    \q
```

Finally, to run the project you need to run this code:

```sh
$    python3 logs_analysis.py
```

### Output example

An example of output from this project is:

```
1) The most popular three articles of all time are:
	Title: "Candidate is jerk, alleges rival" - 338647 views
	Title: "Bears love berries, alleges bear" - 253801 views
	Title: "Bad things gone, say good people" - 170098 views

2) The most popular authors articles of all time are:
	Author: Ursula La Multa - 507594 views
	Author: Rudolf von Treppenwitz - 423457 views
	Author: Anonymous Contributor - 170098 views
	Author: Markoff Chaney - 84557 views

3) Days that more than 1% of requests lead to errors:
	Day: July 17, 2016 - Error ratio: 2.26%
```
