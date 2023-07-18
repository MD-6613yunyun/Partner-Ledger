from flask import Blueprint, render_template,request
from website import db_connection,password_hash

admin = Blueprint('admin',__name__)

all_units = {}
all_shops = {}

def get_all_data():
    global all_units,all_shops
    conn = db_connection()
    cur = conn.cursor()
    cur.execute(""" SELECT id,name FROM res_company;""")
    units = cur.fetchall()
    all_units = {unit[0]:unit[1] for unit in units}
    cur.execute(""" SELECT id,name FROM analytic_shop;""")
    shops = cur.fetchall()
    all_shops = {shop[0]:shop[1] for shop in shops}

def get_all_users(cur):
    cur.execute("""SELECT id,code,name,mail,admin,unit_code,shop_code FROM user_auth""")
    all_datas = cur.fetchall()
    result = []
    for all_data in all_datas:
        units = all_data[5].split(",")
        shops = all_data[6].split(",")
        data = list(all_data[:5]) + [{key:value for key,value in all_units.items() if key in units},
                                {key:value for key,value in all_shops.items() if key in shops}]
        result.append(data)
    return result

@admin.route("/")
def admin_home_authenticate():
    return render_template('admin.html')

@admin.route("/login",methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        conn = db_connection()
        cur = conn.cursor()
        code = request.form.get('log-code')
        pwd = request.form.get('log-pwd')
        cur.execute("""SELECT pwd,admin FROM user_auth WHERE code = %s""",(code,))
        data = cur.fetchall()
        if data != []:
            decrypted_pwd = password_hash.A3Decryption().startDecryption(data[0][0])
            if decrypted_pwd == pwd and data[0][1]:
                get_all_data()
                result = get_all_users(cur)
                cur.close()
                conn.close()
                return render_template('admin.html',authenticate=True,result = result,all_units=all_units,all_shops=all_shops)
        cur.close()
        conn.close()
    return render_template('admin.html')


@admin.route('/grant',methods=['GET','POST'])
def grant_rights():
    if request.method == 'POST':
        selected_units = request.form.getlist('unit-selects')
        selected_shops = request.form.getlist('shop-selects')
        idd = request.form.get('userID')
        get_all_data()
        conn = db_connection()
        cur = conn.cursor()

        cur.execute(""" UPDATE user_auth SET unit_code = %s WHERE id = %s """,(','.join(selected_units),idd))
        cur.execute(""" UPDATE user_auth SET shop_code = %s WHERE id = %s """,(','.join(selected_shops),idd))
        conn.commit()
        result = get_all_users(cur)
        
        cur.close()
        conn.close()
        return render_template('admin.html',authenticate=True,result = result,all_units=all_units,all_shops=all_shops)
    return render_template('admin.html')

@admin.route('/delUser',methods=['GET','POST'])
def delete_user():
    if request.method == 'POST':
        conn = db_connection()
        cur = conn.cursor()

        idd = request.form.get('delUserId')

        cur.execute(""" DELETE FROM user_auth WHERE id = %s""",(idd,))
        conn.commit()
        result = get_all_users(cur)
        cur.close()
        conn.close()
        if result == []:
            return render_template('admin.html')
    return render_template('admin.html',authenticate=True,result = result,all_units=all_units,all_shops=all_shops)

@admin.route('/grantAdmin/<idd>/<bol>')
def grand_admin_access(idd,bol):

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("UPDATE user_auth SET admin = %s WHERE id =%s",(bol,idd))
    conn.commit()

    cur.close()
    conn.close()
    
    return "Completed"

