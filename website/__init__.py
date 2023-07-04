from flask import Flask
import xmlrpc.client
from datetime import date, timedelta,datetime

class LineTracker:

    BI_tracker = {}
    ID_create = {}

    def __init__(self, db, username, pwd):
        self.db = db
        self.username = username
        self.pwd = pwd
        self.uid = 0
        self.end_date = date.today().strftime('%Y-%m-%d') + " 17:29:59"
        self.start_date = date.today().replace(day=1).strftime('%Y-%m-%d') + " 17:30:13"

    def authenticate_server(self, server):
        common = xmlrpc.client.ServerProxy("{}/xmlrpc/2/common".format(server))
        uid = common.authenticate(self.db, self.username, self.pwd, {})
        if uid:
            print(f"Authenticated with the unique ID - {uid}")
            self.uid = uid
        else:
            print("Invalid credentials or login..")
            print("Try again with valid credentials")
        return uid


    def initialize_objects_in_server(self, server:str):
        models = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(server))
        return models

    def filter_data(self,pay,recv,post,draft,recon,bi,pc,shop,rangeDate,ptnID,obj_models:object,rtnDate=False,owner = False):
        # print(pay,recv,post,draft,recon,bi,pc,shop,rangeDate,ptnID)
        rangeDate = rangeDate.replace("~","/")
        domain = []
        if pay and recv:
            domain.append('|')
            domain.append(('account_internal_type','=',"payable"))
            domain.append(('account_internal_type','=',"receivable"))
        else:
            if pay:
                domain.append(('account_internal_type','=',"payable"))
            else:
                domain.append(('account_internal_type','=',"receivable"))
        if post and  draft:
            domain.append('|')
            domain.append(('parent_state','=',"posted"))
            domain.append(('parent_state','=',"draft"))
        else:
            if post:
                domain.append(('parent_state','=',"posted"))
            else:
                domain.append(('parent_state','=',"draft"))
        if recon == 'Only show unreconciled entries':
            domain.append(('full_reconcile_id','=',False))
        domain.append(("unit_id","=",bi))
        if pc:
            domain.append(("project_code_id","=",pc))
        if shop:
            domain.append(("shop_id","=",shop))
        if owner:
            domain.append(('owner_id','=',ptnID))
        else:
            if ptnID:
                domain.append(('partner_id',"=",ptnID))
        self.end_date = date.today().strftime('%Y-%m-%d')
        if rangeDate == 'Today':
            self.start_date = (date.today() - timedelta (days=1)).strftime('%Y-%m-%d')
        elif rangeDate == 'This week':
            self.start_date = (date.today() - timedelta(days=date.today().weekday()+1)).strftime('%Y-%m-%d')
        elif rangeDate == 'This Month':
            self.start_date = date.today().replace(day=1).strftime('%Y-%m-%d')
        elif rangeDate == 'This Year':
            self.start_date = date.today().replace(day=1,month=1).strftime('%Y-%m-%d')
        else:
            start_date,end_date = rangeDate.split(" - ")
            self.start_date = (datetime.strptime(start_date, "%m/%d/%Y")).strftime("%Y-%m-%d")
            self.end_date = datetime.strptime(end_date, "%m/%d/%Y").strftime("%Y-%m-%d") 
        domain.append(('date', '>=', self.start_date))
        domain.append(('date', '<=', self.end_date))
        print(domain)
        result = obj_models.execute_kw(self.db,self.uid,self.pwd,'account.move.line','search_read',
                                    [domain],{"fields":['date','debit','credit','partner_id','date_maturity','currency_id',
                                    'matching_number','account_id','amount_currency','exchange_rate'],'order':'date'})
        print(len(result))
        if rtnDate:
            return result,self.start_date,self.end_date
        return result
    
def create_app():
    app = Flask(__name__)
    app.config['secret_key'] = "zaqwsxcderfvbgtyhnmjuik129838484734893"

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app
