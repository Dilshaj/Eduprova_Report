import pandas as pd
url1 = "https://docs.google.com/spreadsheets/d/1i3Knwzh3I9rklo_8xDxeDVzH8y0aAzG2OayosfPt3mY/export?format=csv&sheet=Daily%20Task"
url2 = "https://docs.google.com/spreadsheets/d/1i3Knwzh3I9rklo_8xDxeDVzH8y0aAzG2OayosfPt3mY/export?format=csv&sheet=Employee%20ID%20%26%20Name"
url3 = "https://docs.google.com/spreadsheets/d/1i3Knwzh3I9rklo_8xDxeDVzH8y0aAzG2OayosfPt3mY/export?format=csv&sheet=Task%20Logs"

for url in [url1, url2, url3]:
    try:
        df = pd.read_csv(url)
        print("Success:", url, "cols:", df.columns.tolist()[:3])
    except Exception as e:
        print("Failed:", url, str(e))
