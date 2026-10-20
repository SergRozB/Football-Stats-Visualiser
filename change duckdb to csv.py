import duckdb, os

con = duckdb.connect("Football-Stats-Visualiser\\Data\\transfermarkt-datasets.duckdb", read_only=True)
os.makedirs("csv_export", exist_ok=True)

tables = con.execute("SHOW TABLES").fetchall()
for (name,) in tables:
    con.execute(f"COPY {name} TO 'csv_export/{name}.csv' (HEADER, DELIMITER ',')")
    print(f"exported {name}")