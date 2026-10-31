# Snowflake CoCo workflow for ReliefLens

Snowflake CoCo is the AI coding/data agent used inside Snowflake. It is not an application API dependency. Use CoCo in Snowsight or CoCo CLI to inspect the selected Marketplace dataset, adapt the SQL to its actual schema, run it, and review the result.

## 1. Find a real infrastructure dataset

In Snowflake Marketplace, search for public bridge, road, transport, elevation, or geospatial infrastructure datasets relevant to the affected region. Record the provider, listing, database/schema/table names, license/usage terms, geographic coverage, and last-updated date. Do not treat sample data as a real baseline.

## 2. Ask CoCo to inspect the dataset

Prompt:

> Inspect the Marketplace datasets available to my current Snowflake role. Find public bridge or road infrastructure and geospatial/topography tables suitable for humanitarian route-access analysis. Show exact database, schema, table, column names, geographic coverage, update date, provider and usage terms. Do not invent tables or columns. Recommend the smallest useful set and explain data freshness limitations.

## 3. Ask CoCo to write and run the analysis

Prompt:

> Using only the verified Marketplace tables you just inspected, write Snowflake SQL to compare ReliefLens incident locations against nearby bridge/road infrastructure. Use valid spatial functions and the actual column names. Return incident ID, incident location, priority, nearest infrastructure feature, distance, source dataset and source update date. Clearly distinguish measured data from missing/unknown data. Do not infer that a road or bridge is safe. Show the SQL first, explain joins and coordinate reference assumptions, then run it only after I approve.

## 4. Evidence required

Save the exact SQL, query ID, result export, Marketplace listing URL, dataset provider, coverage and update date. Add sanitized screenshots of CoCo generating/reviewing the query. Never upload private Snowflake credentials or tokens to GitHub.

## 5. Safety

Infrastructure proximity is not structural integrity or proof of passability. ReliefLens outputs are decision support only; responders must verify conditions on site.
