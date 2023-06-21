# https://www.kaggle.com/code/residentmario/creating-reading-and-writing
import pandas as pd

# 2 main objects, data frame and series

# DATAFRAME
# dataframe is a table containing an array of individual entities, each of which has a certain value

# int
pd.DataFrame({'Yes': [50, 21], 'NO': [131, 2]})

# str
pd.DataFrame({'Ashley': ['I liked it.', 'It was awful'], 'Andrew': ['Pretty good', 'Bland.']})

# Keys are column headers and the row labels start from 0++. Row labels are Index and can assign your own index
# pd.Dataframe() constructor creates data frame objects
pd.DataFrame({'Ashley': ['Munchies', 'Lately'], 'Andrew': ['Bob is your uncle.', 'Money monet']}, index=['Product A', 'Product B'])

# SERIES
# A single column of a dataframe, list
pd.Series([1, 2, 3, 4, 5])

# can also assign index of choice as opposed to 0++ and a general name
pd.Series([22, 33, 43, 99], index=['2013 sales', '2013 inquiries', '2013 views', '2013 pays'], name='Product A')

# Reading from CSV file .Comma separated values
# pd.read_csv("../input/wine-reviews/winemag-data-130k-v2.csv")

