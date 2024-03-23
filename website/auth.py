from flask import Blueprint, render_template, request,redirect,url_for,make_response,after_this_request,session
import subprocess
from website import db_connection
from website import password_hash
import random
import string
from datetime import datetime,timedelta

auth = Blueprint('auth',__name__)

def mix_string_with_random(string_to_mix, random_length):
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=random_length))
    mixed_string = ''.join(random.sample(string_to_mix + random_chars, len(string_to_mix + random_chars)))
    return mixed_string.replace(' ','')

def send_password_to_the_mail(mail,pwd):
    # Command to execute
    command = r"""(echo "Subject: Partner Ledger Account"; echo "MIME-Version: 1.0"; 
    echo "Content-Type: text/html"; echo ""; echo "<h1>Mudon Maung Maung Software Team</h1><h4>
    Authentication Password for Partner Ledger Account</h4><p>Your Password is *** <b>{}</b> ***</p>
    <br><i>Don't Share this password to anyone!!</i>") | /usr/sbin/sendmail -f mdmm.softwareteam@gmail.com -F   "MMM Software Team" {} -s "Partner Ledger Account Confirmation"  """.format(pwd,mail)

    # Execute the command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # Check the command output and return code
    if result.returncode == 0:
        print(command)
    else:
        print("Command failed.")
        print("Error:")
        print(result.stderr)


@auth.route("/")
@auth.route("<atyp>")
@auth.route("<atyp>/<mgs>")
def authenticate(atyp='log',mgs=None):
    session.pop('ledger_id', default=None)
    session.pop('ledger_admin', default=None)    
    return render_template("authenticate.html",mgs=mgs,atyp = atyp)

@auth.route('/delete-cookie-for-logout')
def delete_cookie_for_logout():
    print("session deleted")
    session.pop('ledger_id', default=None)
    session.pop('ledger_admin', default=None)

@auth.route("handle-auth/<typ>",methods=['GET','POST'])
def handle_auth(typ):
    session.pop('ledger_id', default=None)
    session.pop('ledger_admin', default=None)
    if request.method == 'POST':
        conn = db_connection()
        cur = conn.cursor()
        if typ == 'log':
            code = request.form.get('log-code')
            pwd = request.form.get('log-pwd')
            cur.execute("SELECT pwd,admin FROM user_auth WHERE code = %s",(code,))
            datas = cur.fetchall()
            
            if datas != []:
                try:
                    decrypted_pwd = password_hash.A3Decryption().startDecryption(datas[0][0])
                    if decrypted_pwd == pwd:
                        session['ledger_id'] = code
                        session['ledger_admin'] = str(datas[0][1])
                        return redirect(url_for('views.all_partners'))
                except:
                    pass
            return redirect(url_for('auth.authenticate',atyp=typ,mgs="Authentication Failure..."))
        elif typ == 'reg':
            code = request.form.get('reg-code')
            u_name = request.form.get('reg-name')
            mail = request.form.get('reg-mail')
            ref = request.form.get('reg-ref')
            cur.execute("""SELECT code FROM user_auth WHERE code = %s""",(code,))
            check = cur.fetchall()
            if check != []:
                return redirect(url_for('auth.authenticate',atyp=typ,mgs="Employee Code Already Registred..."))
            cur.execute("""SELECT ptn.name 
                FROM res_users userr
                LEFT JOIN res_partner ptn ON ptn.id = userr.partner_id
                WHERE userr.login = %s;""",('MD-'+code,))
            name = cur.fetchall()
            if name == [] or not name[0][0].strip().startswith(u_name):
                return redirect(url_for('auth.authenticate',atyp=typ,mgs="Invalid Employee Code..."))
            cur.execute("""SELECT id FROM res_partner WHERE name = %s;""",(ref.strip(),))
            idd = cur.fetchall()
            if idd == [] or ref.strip() == name[0][0]:
                return redirect(url_for('auth.authenticate',atyp=typ,mgs="Invalid Reference Person from MMM.."))
            pwd = mix_string_with_random(u_name+code,len(code))
            try:
                print(pwd)
                send_password_to_the_mail(mail,pwd)
                encrypted_pwd = password_hash.A3Encryption().start_encryption(pwd,u_name)
                cur.execute("""INSERT INTO user_auth (name,code,mail,pwd,ref_person) 
                            VALUES (%s,%s,%s,%s,%s)""",(u_name,code,mail,encrypted_pwd,ref)) 
                conn.commit()
                mgs = 'Account Credentials are succesfully sent to your email'
                return redirect(url_for('auth.authenticate',atyp='log',mgs=mgs))
            except:
                return redirect(url_for('auth.authenticate',atyp=typ,mgs = "Database Insertion Error"))                      
        elif typ == 'fog':
            mail = request.form.get('forget-mail')
            code = request.form.get('forget-code')
            ref = request.form.get('forget-ref')
            cur.execute("SELECT mail,name,ref_person FROM user_auth WHERE code = %s",(code,))
            datas = cur.fetchall()
            if datas != []:
                if datas[0][0] == mail and datas[0][2] == ref:
                    # sent email
                    pwd = mix_string_with_random(datas[0][1]+code,len(code))
                    print(pwd)
                    send_password_to_the_mail(mail,pwd)
                    encrypted_pwd = password_hash.A3Encryption().start_encryption(pwd,datas[0][1])
                    cur.execute("UPDATE user_auth SET pwd = %s WHERE code = %s",(encrypted_pwd,code))
                    conn.commit()
                    return redirect(url_for('auth.authenticate',atyp='log',mgs = "New Password is successfully sent to your mail.."))     
            return redirect(url_for('auth.authenticate',atyp=typ,mgs = "Employee Code or Reference Person doesn't match with your mail.."))
        elif typ == 'out':
            respon = delete_cookie_for_logout()
            return redirect(url_for('auth.authenticate',atyp='log',mgs = "Successfully Logout!!"))  

        cur.close()
        conn.close()
    return redirect(url_for('auth.authenticate'))

