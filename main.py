import mysql.connector
import openai
import os

openai.api_key = "your openai Api key"

mydb = mysql.connector.connect(
    host="Server IP or localhost",
    user="MySQL username",
    password="MySQL password",
    database="Database Name")

cursor = mydb.cursor()

cursor.execute("show tables")

Tables = [i[0] for i in cursor]
DB = {"Tables": {}, "Links": []}

for table in Tables:
    # print(table)
    cursor.execute(f"describe {table}")
    tableInfoRow = [list(i) for i in cursor]
    DB["Tables"][table] = tableInfoRow

cursor.execute("SELECT `TABLE_NAME`,`COLUMN_NAME`,`REFERENCED_TABLE_NAME`,`REFERENCED_COLUMN_NAME`"
               "FROM"
               "`INFORMATION_SCHEMA`.`KEY_COLUMN_USAGE`"
               "WHERE"
               "`TABLE_SCHEMA` = SCHEMA()"
               "AND `REFERENCED_TABLE_NAME` IS NOT NULL;")

for link in cursor:
    DB["Links"].append(list(link))
    # print(list(link))

InfoPrompt = ""

for table in DB["Tables"]:
    InfoPrompt += f"\n The table {table} contains : \n"
    for row in DB["Tables"][table]:
        InfoPrompt += f"\t the field {row[0]} that have for type {row[1]} \n"

InfoPrompt += "\n The tables have the following links : \n"
for link in DB["Links"]:
    InfoPrompt += f"\t the field {link[1]} of the table {link[0]} is connected to the field {link[3]} of the table {link[2]} \n"

# print(InfoPrompt)

prompt_file = os.path.join(os.getcwd(), "Prompt.txt")
DefaultPrompt = open(prompt_file, "r").read()
DefaultPrompt = DefaultPrompt.replace("{SQL}", "MySQL")

NewPrompt = input("Wich Query do you want to execute : ")
Prompt = DefaultPrompt + InfoPrompt + "\n Question : \n" + NewPrompt
print(Prompt)

response = openai.Completion.create(
    engine="text-davinci-002",
    prompt=Prompt,
    max_tokens=500,
    n=1,
    stop=None,
    temperature=0.5,)

message = response.choices[0].text.strip()
print(message)
