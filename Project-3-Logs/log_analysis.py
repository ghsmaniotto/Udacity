#!/usr/bin/env python3

# "Database code" for the DB Forum.
import psycopg2


def connect(database_name="news"):
    """Returns a two item tuple,
    the database and the cursor database
    Args:
        database_name - database to

    """
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print("Was not possible to connect to the database")


def execute_query(query=""):
    """execute_query takes a SQL query as parameter,
    executes the query and returns the database response as a list of tuples

    args:
        query - SQL statement to be executed.

    returns:
        A list of tuples containing the result of the query
    """
    try:
        # Connect to database and get the db cursor
        db, db_cursor = connect()
        # Request the SQL query
        db_cursor.execute(query)
        # Get the db reponse
        output = db_cursor.fetchall()
        # Close the database connection
        db.close()
        return output
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def get_top_articles():
    """Returns a list of two item tuple
    (name article and total views for the article),
    for the three most popular articles by views"""

    # SQL query to find the top articles
    sql_query_top_articles = """
    WITH articles_slug AS (
        SELECT '/article/' || slug AS path, title
        FROM articles
    )
    SELECT articles_slug.title as title, articles_log.qntd as views
    FROM articles_slug, articles_log
    WHERE articles_slug.path = articles_log.path
    ORDER BY views DESC LIMIT 3;"""
    return execute_query(sql_query_top_articles)


def get_top_authors():
    """Return a list of two item tuples
    (authors name and total author views),
    for the most popular authors by views
    """
    # SQL query to the second question
    sql_query_top_authors = """
    WITH articles_author AS (
        SELECT '/article/' || slug as path, author
        FROM articles
        GROUP BY path, author
    )
    SELECT authors.name as author, sum(articles_log.qntd) as views
    FROM authors, articles_author, articles_log
    WHERE articles_author.path = articles_log.path
        and articles_author.author = authors.id
    GROUP BY authors.name
    ORDER BY views DESC;"""
    # Request the SQL query
    return execute_query(sql_query_top_authors)


def get_day_error_ratio():
    """Returns a list of two item tuple
    (day and day error ratio),
    for the days that more than 1% of request are error"""
    # SQL query to the second question
    sql_query_error_ratio = """
    SELECT to_char(date, 'FMMonth FMDD, YYYY'), err/total as ratio
    from (select time::date as date,
        count(*) as total,
        sum((status != '200 OK')::int)::float as err
        from log
        group by date) as errors
    where err/total > 0.01;"""
    # Request the SQL query
    return execute_query(sql_query_error_ratio)


def print_solution(top_articles=[('', '')],
                   top_authors=[('', '')],
                   error_ratio=[('', '')]):
    """Prints the sql request for the
    top articles by views, top authors by views and day error ratio"""

    print("\n1) The most popular three articles of all time are:")
    for title, views in top_articles:
        print("\tTitle: \"{}\" - {} views".format(title, views))

    print("\n2) The most popular authors articles of all time are:")
    for author, views in top_authors:
        print("\tAuthor: {} - {} views".format(author, views))

    print("\n3) Days that more than 1% of requests lead to errors:")
    for day, error_ratio in error_ratio:
        print("\tDay: {} - Error ratio: {:.2%}".format(day, float(error_ratio)))


if __name__ == '__main__':
    print_solution(get_top_articles(),
                   get_top_authors(),
                   get_day_error_ratio())
