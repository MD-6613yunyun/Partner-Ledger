from flask import Blueprint, render_template,request,redirect,url_for, session
from website import db_connection,password_hash

admin = Blueprint('admin',__name__)

all_units = {}
all_shops = {}
all_users = []

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
    global all_users
    cur.execute("""SELECT id,code,name,mail,admin,unit_code,shop_code FROM user_auth""")
    all_users = cur.fetchall()

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
                get_all_users(cur)
                cur.close()
                conn.close()
                return render_template('admin.html',authenticate=True,result = all_users,all_units=all_units,all_shops=all_shops)
        cur.close()
        conn.close()
        return redirect(url_for('auth.authenticate',atyp='log',mgs="Due to Authentication Failure of Admin Section , you must relogin..."))
    return render_template('admin.html')


@admin.route('/grant',methods=['GET','POST'])
def grant_rights():
    if request.method == 'POST':
        selected_units = request.form.get("unit-list-input").strip(",")
        selected_shops = request.form.get("shop-list-input").strip(",")
        idd = request.form.get('userID')
        get_all_data()
        conn = db_connection()
        cur = conn.cursor()

        cur.execute(""" UPDATE user_auth SET unit_code = %s WHERE id = %s """,(selected_units,idd))
        cur.execute(""" UPDATE user_auth SET shop_code = %s WHERE id = %s """,(selected_shops,idd))
        conn.commit()
        get_all_users(cur)
        
        cur.close()
        conn.close()
        return render_template('admin.html',authenticate=True,result = all_users,all_units=all_units,all_shops=all_shops)
    return render_template('admin.html')

@admin.route('/delUser',methods=['GET','POST'])
def delete_user():
    if request.method == 'POST':
        conn = db_connection()
        cur = conn.cursor()

        idd = request.form.get('delUserId')

        cur.execute(""" DELETE FROM user_auth WHERE id = %s""",(idd,))
        conn.commit()
        get_all_users(cur)
        cur.close()
        conn.close()
        if all_users == []:
            return render_template('admin.html')
    
    return render_template('admin.html',authenticate=True,result = all_users,all_units=all_units,all_shops=all_shops)

@admin.route('/grantAdmin/<idd>/<bol>')
def grand_admin_access(idd,bol):

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("UPDATE user_auth SET admin = %s WHERE id =%s",(bol,idd))
    conn.commit()

    cur.close()
    conn.close()
    
    return "Completed"

