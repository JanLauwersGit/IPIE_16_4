import pandas as pd

# create a sample DataFrame
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6],
    'C': [7, 8, 9]
})


def my_function(row):  # define a function that takes values from two columns
    print(row)
    return row['A'] + row['B']


df['D'] = df[['A', 'B']].apply(my_function, axis=1)  # apply the function to each row in the DataFrame

# print the resulting DataFrame
print(df)
