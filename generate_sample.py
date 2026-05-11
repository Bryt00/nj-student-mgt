import pandas as pd

data = [
    ['Doe', 'John', 'Junior', 'M', '2010-05-20', 'Jane Doe', '0551234567', '2H3', 'Boarder'],
    ['Smith', 'Jane', None, 'F', '2011-03-15', 'Bob Smith', '0249876543', '2H3', 'Day'],
    ['Brown', 'Charlie', 'B', 'M', '2010-08-22', 'Sally Brown', '0201112222', '3A1', 'Boarder'],
]

df = pd.DataFrame(data, columns=[
    'Surname', 'Firstname', 'Other Names', 'Gender', 'DOB', 'Guardian', 'Phone', 'Class', 'Residence'
])

df.to_excel('sample_students.xlsx', index=False)
print("sample_students.xlsx created successfully.")
