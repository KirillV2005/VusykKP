import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

url = 'https://www.worldometers.info/coronavirus/'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table', id='main_table_countries_today')

headers = []
for th in table.find_all('th'):
    headers.append(th.text.strip())

data = []
for row in table.tbody.find_all('tr'):
    cells = row.find_all('td')
    if len(cells) > 1:
        data.append([cell.text.strip() for cell in cells])

df = pd.DataFrame(data, columns=headers)

print("Опис набору даних:\n", df.describe())
print("Заголовки стовпців:\n", df.columns)
print("Інформація про типи даних та відсутні значення:\n", df.info())
print("Докладний опис усіх стовпців:\n", df.describe(include='all'))

columns_to_drop = ['#', 'NewCases', 'NewDeaths', 'NewRecovered', 'Serious,Critical', 'Tot Cases/1M pop', 'Deaths/1M pop', 'TotalTests', 'Tests/1M pop', 'Population', 'Continent']
existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]
df.drop(existing_columns_to_drop, axis=1, inplace=True)

df.fillna(0, inplace=True)
df.rename(columns={'Country,Other': 'Country', 'TotalCases': 'Total_Cases', 'TotalDeaths': 'Total_Deaths', 'TotalRecovered': 'Total_Recovered', 'ActiveCases': 'Active_Cases'}, inplace=True)

def clean_and_convert(column):
    return column.str.replace(',', '').replace('N/A', '0').replace('', '0').astype(int)

df['Total_Cases'] = clean_and_convert(df['Total_Cases'])
df['Total_Deaths'] = clean_and_convert(df['Total_Deaths'])
df['Total_Recovered'] = clean_and_convert(df['Total_Recovered'])
df['Active_Cases'] = clean_and_convert(df['Active_Cases'])

print("Інформація про типи даних після очистки:\n", df.info())

df['Mortality_Rate'] = (df['Total_Deaths'] / df['Total_Cases']) * 100
df['Recovery_Rate'] = (df['Total_Recovered'] / df['Total_Cases']) * 100

sorted_df = df.sort_values(by='Total_Cases', ascending=False)
print("Топ 5 країн за кількістю випадків COVID-19:\n", sorted_df.head())

plt.figure(figsize=(10, 5))
sns.barplot(x='Country', y='Total_Cases', data=sorted_df.head(10))
plt.title('Топ 10 країн за кількістю випадків COVID-19')
plt.xlabel('Країна')
plt.ylabel('Загальна кількість випадків')
plt.xticks(rotation=45)
plt.show()

plt.figure(figsize=(10, 5))
sns.barplot(x='Country', y='Mortality_Rate', data=sorted_df.head(10))
plt.title('Топ 10 країн за рівнем смертності від COVID-19')
plt.xlabel('Країна')
plt.ylabel('Рівень смертності (%)')
plt.xticks(rotation=45)
plt.show()

plt.figure(figsize=(10, 5))
sns.barplot(x='Country', y='Recovery_Rate', data=sorted_df.head(10))
plt.title('Топ 10 країн за рівнем одужань від COVID-19')
plt.xlabel('Країна')
plt.ylabel('Рівень одужань (%)')
plt.xticks(rotation=45)
plt.show()

if 'Ukraine' in df['Country'].values:
    df_ukraine = df[df['Country'] == 'Ukraine']
    ukraine_data = df_ukraine.iloc[0][['Total_Cases', 'Total_Deaths', 'Total_Recovered', 'Active_Cases']].astype(int)
    columns = ['Загальна кількість випадків', 'Загальна кількість смертей', 'Загальна кількість одужань', 'Активні випадки']
plt.figure(figsize=(10, 5))
sns.barplot(x=columns, y=ukraine_data.values)
plt.title('Статистика COVID-19 в Україні')
plt.ylabel('Кількість')
plt.xlabel('Показник')
plt.xticks(rotation=45)
plt.show()

